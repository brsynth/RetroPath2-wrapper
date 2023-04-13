#!/usr/bin/env python3
"""
Created on January 16 2020

@author: Joan Hérisson, Melchior du Lac
@description: Python wrapper to run RetroPath2.0 KNIME workflow

"""
from os import (
    mkdir as os_mkdir,
    path  as os_path,
    rename
)
from shutil import copyfile
from brs_utils import extract_gz
from filetype import guess
from tempfile import TemporaryDirectory
from typing import Dict, Tuple
from logging import (
    Logger,
    getLogger
)
from re import match
from csv import reader as csv_reader
from colored import attr
from csv import reader
from .Args import (
    DEFAULT_KNIME_FOLDER,
    DEFAULT_MSC_TIMEOUT,
    DEFAULT_KNIME_VERSION,
    DEFAULT_RP2_VERSION,
    RETCODES,
)
from retropath2_wrapper.knime import Knime
from retropath2_wrapper.preference import Preference


here = os_path.dirname(os_path.realpath(__file__))


def retropath2(
    sink_file: str, source_file: str, rules_file: str,
    outdir: str,
    kinstall: str = DEFAULT_KNIME_FOLDER,
    kexec: str = None, kver: str = DEFAULT_KNIME_VERSION,
    knime: Knime = None,
    rp2_version: str = DEFAULT_RP2_VERSION,
    max_steps: int = 3,
    topx: int = 100,
    dmin: int = 0, dmax: int = 1000,
    mwmax_source: int = 1000,
    msc_timeout: int = DEFAULT_MSC_TIMEOUT,
    logger: Logger = getLogger(__name__)
) -> Tuple[str, Dict]:

    logger.debug(f'sink_file: {sink_file}')
    logger.debug(f'source_file: {source_file}')
    logger.debug(f'rules_file: {rules_file}')
    logger.debug(f'outdir: {outdir}')
    logger.debug(f'kexec: {kexec}')
    logger.debug(f'kinstall: {kinstall}')
    logger.debug(f'kver: {kver}')
    logger.debug(f'rp2_version: {rp2_version}')
    logger.debug(f'max_steps: {max_steps}')
    logger.debug(f'topx: {topx}')
    logger.debug(f'dmin: {dmin}')
    logger.debug(f'dmax: {dmax}')
    logger.debug(f'mwmax_source: {mwmax_source}')
    logger.debug(f'msc_timeout: {msc_timeout}')

    # Create Knime object
    if knime is None:
        knime = Knime(kexec=kexec, kinstall=kinstall, kver=kver)
    if rp2_version is not None:
        knime.workflow = os_path.join(
            here, 'workflows', f'RetroPath2.0_{rp2_version}.knwf'
        )

    logger.debug('knime: ' + str(knime))

    # Store RetroPath2 params into a dictionary
    rp2_params = {
        'max_steps'    : max_steps,
        'topx'         : topx,
        'dmin'         : dmin,
        'dmax'         : dmax,
        'mwmax_source' : mwmax_source
    }
    logger.debug('rp2_params: ' + str(rp2_params))

    r_code, inchi = check_input(source_file, sink_file)
    if r_code != RETCODES['OK']:
        return r_code, None

    # Install KNIME
    r_code = knime.install(logger=logger)
    if r_code > 0:
        return r_code, None

    logger.info('{attr1}Initializing{attr2}'.format(attr1=attr('bold'), attr2=attr('reset')))

    # Preferences
    preference = Preference(rdkit_timeout_minutes=msc_timeout)
    with TemporaryDirectory() as tempd:

        # Format files for KNIME
        files = format_files_for_knime(
            sink_file, source_file, rules_file,
            tempd, outdir,
            logger
        )
        logger.debug(files)

        # Create outdir if does not exist
        if not os_path.exists(outdir):
            os_mkdir(outdir)

        # Call KNIME
        r_code = knime.call(
            files=files,
            params=rp2_params,
            preference=preference,
            logger=logger,
        )
        if r_code == RETCODES['OSError']:
            return r_code, files

    r_code = check_src_in_sink_2(
        src_in_sink_file = os_path.join(files['outdir'], files['src-in-sk']),
        logger = logger
    )

    return r_code, files


def check_input(
    source_file: str,
    sink_file: str,
    logger: Logger = getLogger(__name__)
) -> Tuple[str, str]:

    logger.info('{attr1}Checking input data{attr2}'.format(attr1=attr('bold'), attr2=attr('reset')))

    # Check if InChI is well-formed
    inchi = check_inchi_from_file(source_file, logger)
    if inchi == '' or inchi in RETCODES.values():
        return RETCODES['InChI'], None

    # Check if source is in sink
    r_code = check_src_in_sink_1(inchi, sink_file, logger)
    if r_code == RETCODES['SrcInSink']:
        return RETCODES['SrcInSink'], None
    elif r_code == RETCODES['FileNotFound']:
        return RETCODES['FileNotFound'], None

    return RETCODES['OK'], inchi


def check_src_in_sink_1(
    source_inchi: str,
    sink_file: str,
    logger: Logger = getLogger(__name__)
) -> int:
    """
    Check if source is present in sink file. InChIs have to be strictly equal.

    Parameters
    ----------
    source_inchi: str
        Path to file containing the source.
    sink_file: str
        Path to file containing the sink.
    logger : Logger
        The logger object.

    Returns
    -------
    int Return code.

    """

    logger.info('   |- Source in Sink (simple)')

    try:
        with open(sink_file, 'r') as f:
            for row in csv_reader(f, delimiter=',', quotechar='"'):
                if source_inchi == row[1]:
                    logger.error('        source has been found in sink')
                    return RETCODES['SrcInSink']

    except FileNotFoundError as e:
        logger.error(e)
        return RETCODES['FileNotFound']

    return RETCODES['OK']


def check_inchi_from_file(
    file: str,
    logger: Logger = getLogger(__name__)
) -> str:

    logger.info('   |- InChI')

    try:
        with open(file, 'r') as f:
            f_reader = reader(f)
            header = next(f_reader)
            if [_.strip().lower() for _ in header[:2]] != ['name', 'inchi']:
                logger.error(header)
                return False
            compound_id, inchi = next(f_reader)[:2]  # Sniff first inchi
            inchi = inchi.strip()  # Remove trailing spaces
            # Match
            #
            #   InChI=
            #   -----
            #       matches 'InChI='
            #
            #   1(S)?
            #   -----
            #       matches:
            #           1    --> version number, currently 1
            #           (S)? --> standard or not
            #
            #   /(([a-z|[A-Z])\d+)+
            #   ------------------
            #       Main layer/Chemical formula, only mandatory sublayer
            #       matches:
            #           /                  --> layer separator
            #           (([a-z|[A-Z])\d+)+ --> a letter followed by at least one number, at least one time
            #
            #   (/.+)?
            #   ------
            #       Other (sub-)layers
            #       matches:
            #           (/.+)? --> if '/' is present, then at least one character/symbol is mandatory
            if match(r'InChI=1(S)?/(([a-z|[A-Z])+\d*)+(/.+)?$', inchi) is None:
                logger.error('        {inchi} is not a valid InChI notation'.format(inchi=inchi))
                return RETCODES['InChI']

    except FileNotFoundError as e:
        logger.error(e)
        return RETCODES['FileNotFound']

    return inchi


def check_src_in_sink_2(
    src_in_sink_file: str,
    logger: Logger = getLogger(__name__)
) -> int:
    """
    Check if source is present in sink file. InChIs could differ.

    Parameters
    ----------
    sink_file: str
        Path to file containing the sink.
    logger : Logger
        The logger object.

    Returns
    -------
    int Return code.

    """
    logger.debug(f'src_in_sink_file: {src_in_sink_file}')
    logger.info('   |- Checking Source in Sink (advanced)')

    try:
        count = 0
        with open(src_in_sink_file, 'r') as f:
            for i in csv_reader(f, delimiter=',', quotechar='"'):
                count += 1
                if count > 1:
                    logger.warning('        |- source has been found in sink')
                    return RETCODES['SrcInSink']

    except FileNotFoundError as e:
        logger.error(e)
        return RETCODES['FileNotFound']

    return RETCODES['OK']


def gunzip_to_csv(filename: str, indir: str) -> str:
    """
    Uncompress gzip file into indir.

    Parameters
    ----------
    filename : str
        Path of file to deflate.
    indir : str
        Path where install.

    """
    new_f = os_path.join(
        indir,
        os_path.basename(filename)+'.gz'
        )
    copyfile(filename, new_f)
    filename = extract_gz(new_f, indir)
    rename(filename, filename+'.csv')
    filename += '.csv'

    return filename


def format_files_for_knime(
    sinkfile: str, sourcefile: str, rulesfile: str,
    indir: str, outdir: str,
    logger: Logger = getLogger(__name__)
) -> Dict:
    """
    Format files according to KNIME expectations.

    Parameters
    ----------
    sinkfile : str
        Path of sink file.
    sourcefile : str
        Path of source file.
    rulesfile : str
        Path of rules file.
    indir : str
        Path where install.
    outdir : str
        Path to output the resuts.
    logger : Logger
        The logger object.

    Returns
    -------
    Dict Dictionary containing filenames.

   """
    logger.info('   |- Formatting files for KNIME')

    # If 'rulesfile' is a pure gzip archive without tar
    kind = guess(rulesfile)
    if kind:
        if kind.mime == 'application/gzip':
            rulesfile = gunzip_to_csv(rulesfile, indir)

    files = {
        'sink'      : os_path.abspath(sinkfile),
        'source'    : os_path.abspath(sourcefile),
        'rules'     : os_path.abspath(rulesfile),
        'results'   : 'results'+'.csv',
        'src-in-sk' : 'source-in-sink'+'.csv',
        'outdir'    : os_path.abspath(outdir)
    }
    # Because KNIME accepts only '.csv' file extension,
    # files have to be renamed
    for key in ['sink', 'source', 'rules']:
        if os_path.splitext(files[key])[-1] != '.csv':
            new_f = os_path.join(
                indir,
                os_path.basename(files[key])+'.csv'
                )
            copyfile(files[key], new_f)
            files[key] = new_f

    return files

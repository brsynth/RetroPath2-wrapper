#!/usr/bin/env python3
"""
Created on January 16 2020

@author: Joan Hérisson, Melchior du Lac
@description: Python wrapper to run RetroPath2.0 KNIME workflow

"""
from os         import (
    mkdir as os_mkdir,
    path  as os_path,
    rename,
    devnull,
    environ as os_environ
    # geteuid,
    # getegid
)
from getpass import getuser
from shutil import (
    copyfile,
    copytree,
    rmtree
)
from sys        import platform  as sys_platform
from subprocess import (
    TimeoutExpired
)  # nosec
from brs_utils  import (
    download_and_extract_tar_gz,
    download,
    download_and_unzip,
    extract_gz,
    chown_r,
    subprocess_call
)
from filetype import guess
from tempfile import (
    NamedTemporaryFile,
    TemporaryDirectory
)
from typing import (
    Dict,
    List,
    Tuple
)
from logging import (
    Logger,
    getLogger
)
from re import match
from csv import reader as csv_reader
from colored import fg, bg, attr
from logging import StreamHandler
from csv import reader
from .Args import (
    DEFAULT_TIMEOUT,
    DEFAULT_KNIME_VERSION,
    DEFAULT_RP2_VERSION,
    RETCODES
)

here = os_path.dirname(os_path.realpath(__file__))


def set_vars(
    kexec: str,
    kpkg_install: bool,
    kver: str = DEFAULT_KNIME_VERSION,
    rp2_version: str = DEFAULT_RP2_VERSION
) -> Dict:
    """
    Set variables and store them into a dictionary.

    Parameters
    ----------
    kexec : str
        Path to KNIME executable.
    kver : str
        Version of KNIME to install.
    kpkg_install : bool
        Boolean to know if KNIME packages have to be installed.
    rp2_version : str
        RetroPath2.0 version.

    """

    # Setting kexec, kpath, kinstall, kver
    kexec_install = False
    if kexec is None:
        kinstall = os_path.join(here, '.knime', sys_platform)
        if sys_platform == 'darwin':
            kpath = os_path.join(kinstall, f'KNIME_{kver}.app')
            kexec = os_path.join(kpath, 'Contents', 'MacOS', 'knime')
        else:
            kpath = os_path.join(kinstall, f'knime_{kver}')
            kexec = os_path.join(kpath, 'knime')
            if sys_platform == 'win32':
                kexec += '.exe'
        if not os_path.exists(kexec):
            kexec_install = True
    else:
        if sys_platform == 'linux':
            kpath = kexec[:kexec.rfind('/')]
            kinstall = kpath[:kpath.rfind('/')]
        elif sys_platform == 'darwin':
            kpath = kexec[:kexec.rfind('/')]
            kinstall = kpath[:kpath.rfind('/')]

    # Build a dict to store KNIME vars
    return {
        'kexec'         : kexec,
        'kexec_install' : kexec_install,
        'kver'          : kver,
        'kpath'         : kpath,
        'kinstall'      : kinstall,
        'kpkg_install'  : kpkg_install,
        'workflow'      : os_path.join(
            here,
            'workflows',
            f'RetroPath2.0_{rp2_version}.knwf'
        )
    }


def retropath2(
    sink_file: str, source_file: str, rules_file: str,
    outdir: str,
    kexec: str = None, kpkg_install: bool = True, kver: str = DEFAULT_KNIME_VERSION,
    rp2_version: str = DEFAULT_RP2_VERSION,
    kvars: Dict = None,
    max_steps: int = 3,
    topx: int = 100,
    dmin: int = 0, dmax: int = 100,
    mwmax_source: int = 1000,
    timeout: int = DEFAULT_TIMEOUT,
    logger: Logger = getLogger(__name__)
) -> Tuple[str, Dict]:

    logger.debug(f'sink_file: {sink_file}')
    logger.debug(f'source_file: {source_file}')
    logger.debug(f'rules_file: {rules_file}')
    logger.debug(f'outdir: {outdir}')
    logger.debug(f'kexec: {kexec}')
    logger.debug(f'kpkg_install: {kpkg_install}')
    logger.debug(f'kver: {kver}')
    logger.debug(f'rp2_version: {rp2_version}')
    logger.debug(f'kvars: {kvars}')
    logger.debug(f'max_steps: {max_steps}')
    logger.debug(f'topx: {topx}')
    logger.debug(f'dmin: {dmin}')
    logger.debug(f'dmax: {dmax}')
    logger.debug(f'mwmax_source: {mwmax_source}')
    logger.debug(f'mwmax_cof: {mwmax_cof}')
    logger.debug(f'timeout: {timeout}')

    if kvars is None:
        # Store KNIME vars into a dictionary
        kvars = set_vars(
            kexec=kexec,
            kver=kver,
            kpkg_install=kpkg_install,
            rp2_version=rp2_version
        )
        logger.debug('kvars: ' + str(kvars))
    # Store RetroPath2 params into a dictionary
    rp2_params = {
        'max_steps'    : max_steps,
        'topx'         : topx,
        'dmin'         : dmin,
        'dmax'         : dmax,
        'mwmax_source' : mwmax_source,
    }
    logger.debug('rp2_params: ' + str(rp2_params))

    r_code, inchi = check_input(source_file, sink_file)
    print(r_code)
    if r_code != RETCODES['OK']:
        return r_code, None

    # Install KNIME
    #      if kexec is not specified
    #  and executable not detected in default path
    if kvars['kexec_install']:
        install_knime(
            kvars['kinstall'],
            kvars['kver'],
            logger
        )
        if sys_platform == 'darwin':
            kpkg_install = os_path.join(kvars['kpath'], 'Contents', 'Eclipse')
        else:
            kpkg_install = kvars['kpath']
        r_code = install_knime_pkgs(
            kpkg_install=kpkg_install,
            kver=kvars['kver'],
            kexec=kvars['kexec'],
            logger=logger
        )
        if r_code > 0:
            return r_code, None
        elif r_code == RETCODES['OSError']:
            return RETCODES['OSError'], None
    else:
        # Add packages to KNIME
        if kvars['kpkg_install']:
            if sys_platform == 'darwin':
                kpkg_install = os_path.join(kvars['kpath'], 'Contents', 'Eclipse')
            else:
                kpkg_install = kvars['kpath']
            r_code = install_knime_pkgs(
                kpkg_install=kpkg_install,
                kver=kvars['kver'],
                kexec=kvars['kexec'],
                logger=logger
            )
            if r_code > 0:
                return r_code, None
            elif r_code == RETCODES['OSError']:
                return RETCODES['OSError'], None

    logger.info('{attr1}Initializing{attr2}'.format(attr1=attr('bold'), attr2=attr('reset')))

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
        r_code = call_knime(
            kvars,
            files,
            rp2_params,
            timeout,
            logger
        )
        if r_code == RETCODES['TimeLimit'] or r_code == RETCODES['OSError']:
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
    if inchi == '':
        return RETCODES['InChI'], None

    # Check if source is in sink
    r_code = check_src_in_sink_1(inchi, sink_file, logger)
    if r_code == -1:
        return RETCODES['SrcInSink'], None
    elif r_code == -2:
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


def install_knime(
    kinstall: str,
    kver: str,
    logger: Logger = getLogger(__name__)
) -> None:
    """
    Install KNIME.

    Parameters
    ----------
    kinstall : str
        Path where install KNIME into.
    kver : str
        Version of KNIME to install.
    logger : Logger
        The logger object.

    """
    logger.info('{attr1}Downloading KNIME {kver}...{attr2}'.format(attr1=attr('bold'), kver=kver, attr2=attr('reset')))

    if sys_platform == 'linux':
        kurl = f'http://download.knime.org/analytics-platform/linux/knime_{kver}.linux.gtk.x86_64.tar.gz'
        download_and_extract_tar_gz(kurl, kinstall)
        chown_r(kinstall, getuser())
        # chown_r(kinstall, geteuid(), getegid())

    elif sys_platform == 'darwin':
        dmg = f'knime_{kver}.app.macosx.cocoa.x86_64.dmg'
        kurl = f'https://download.knime.org/analytics-platform/macosx/{dmg}'
        with NamedTemporaryFile() as tempf:
            download(kurl, tempf.name)
            app_path = f'{kinstall}/KNIME_{kver}.app'
            if os_path.exists(app_path):
                rmtree(app_path)
            with TemporaryDirectory() as tempd:
                cmd = f'hdiutil mount -noverify {tempf.name} -mountpoint {tempd}/KNIME'
                returncode = subprocess_call(cmd, logger=logger)
                copytree(
                    f'{tempd}/KNIME/KNIME {kver}.app',
                    app_path
                )
                cmd = f'hdiutil unmount {tempd}/KNIME'
                returncode = subprocess_call(cmd, logger=logger)

    else:  # Windows
        kurl = f'https://download.knime.org/analytics-platform/win/knime_{kver}.win32.win32.x86_64.zip'
        download_and_unzip(kurl, kinstall)

    logger.info('   |--url: '+kurl)
    logger.info('   |--install_dir: '+kinstall)
    

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


def install_knime_pkgs(
    kpkg_install: str,
    kver: str,
    kexec: str,
    logger: Logger = getLogger(__name__)
) -> int:
    """
    Install KNIME packages needed to execute RetroPath2.0 workflow.

    Parameters
    ----------
    kpath : str
        Path that contains KNIME executable.
    kver : str
        Version of KNIME installed.
    logger : Logger
        The logger object.

    Returns
    -------
    int Return code.

   """
    StreamHandler.terminator = ""
    logger.info( '   |- Checking KNIME packages...')
    logger.debug(f'        + kpkg_install: {kpkg_install}')
    logger.debug(f'        + kver: {kver}')

    args = \
        ' -application org.eclipse.equinox.p2.director' \
      + ' -nosplash -consolelog' \
      + ' -r http://update.knime.org/community-contributions/trunk,' \
          + 'http://update.knime.com/community-contributions/trusted/'+kver[:3]+',' \
          + 'http://update.knime.com/analytics-platform/'+kver[:3] \
      + ' -i org.knime.features.chem.types.feature.group,' \
          + 'org.knime.features.datageneration.feature.group,' \
          + 'org.knime.features.python.feature.group,' \
          + 'org.rdkit.knime.feature.feature.group' \
      + ' -bundlepool ' + kpkg_install + ' -d ' + kpkg_install

    cmd = f'{kexec} {args}'

    returncode = subprocess_call(cmd, logger=logger)
    StreamHandler.terminator = "\n"
    logger.info(' OK')
    return returncode

def call_knime(
    kvars: Dict,
    files: Dict,
    params: Dict,
    timeout: int,
    logger: Logger = getLogger(__name__)
) -> int:
    """
    Install KNIME packages needed to execute RetroPath2.0 workflow.

    Parameters
    ----------
    kvars: Dict
        KNIME variables.
    files: Dict
        Paths of sink, source, rules files.
    params: Dict
        Parameters of the workflow to process.
    timeout: int
        Time after which the run returns.
    logger : Logger
        The logger object.

    Returns
    -------
    int Return code.

   """

    StreamHandler.terminator = ""
    logger.info('{attr1}Running KNIME...{attr2}'.format(attr1=attr('bold'), attr2=attr('reset')))

    args = ' -nosplash -nosave -reset --launcher.suppressErrors -application org.knime.product.KNIME_BATCH_APPLICATION ' \
         + ' -workflowFile=' + kvars['workflow'] \
         + ' -workflow.variable=input.dmin,"'              + str(params['dmin'])         + '",int' \
         + ' -workflow.variable=input.dmax,"'              + str(params['dmax'])         + '",int' \
         + ' -workflow.variable=input.max-steps,"'         + str(params['max_steps'])    + '",int' \
         + ' -workflow.variable=input.sourcefile,"'        + files['source']             + '",String' \
         + ' -workflow.variable=input.sinkfile,"'          + files['sink']               + '",String' \
         + ' -workflow.variable=input.rulesfile,"'         + files['rules']              + '",String' \
         + ' -workflow.variable=input.topx,"'              + str(params['topx'])         + '",int' \
         + ' -workflow.variable=input.mwmax-source,"'      + str(params['mwmax_source']) + '",int' \
         + ' -workflow.variable=output.dir,"'              + files['outdir']             + '",String' \
         + ' -workflow.variable=output.solutionfile,"'     + files['results']            + '",String' \
         + ' -workflow.variable=output.sourceinsinkfile,"' + files['src-in-sk']          + '",String'

    logger.debug(kvars['kexec'] + ' ' + args)

    try:
        printout = open(devnull, 'wb') if logger.level > 10 else None
        # Hack to link libGraphMolWrap.so (RDKit) against libfreetype.so.6 (from conda)
        os_environ['LD_LIBRARY_PATH'] = os_environ.get(
            'LD_LIBRARY_PATH',
            ''
        ) + ':' + os_path.join(
            os_environ['CONDA_PREFIX'],
            "lib"
        )
        returncode = subprocess_call(cmd=kvars['kexec'] + args, logger=logger)
        os_environ['LD_LIBRARY_PATH'] = ':'.join(
            os_environ['LD_LIBRARY_PATH'].split(':')[:-1]
        )
        StreamHandler.terminator = "\n"
        logger.info(' {bold}OK{reset}'.format(bold=attr('bold'), reset=attr('reset')))
        return returncode

    except TimeoutExpired as e:
        logger.warning('   |- Time limit ({timeout} min) is reached'.format(timeout=timeout))
        logger.warning('      Results collected until now are available')
        return RETCODES['TimeLimit']

    except OSError as e:
        logger.error(e)
        return RETCODES['OSError']

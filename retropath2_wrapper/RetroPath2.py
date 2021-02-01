#!/usr/bin/env python3
"""
Created on January 16 2020

@author: Joan Hérisson, Melchior du Lac
@description: Python wrapper to run RetroPath2.0 KNIME workflow

"""
from os         import mkdir     as os_mkdir
from os         import path      as os_path
from os         import rename, devnull
from shutil     import copyfile
from sys        import platform  as sys_platform
from logging    import getLogger
from csv        import reader    as csv_reader
from subprocess import run, STDOUT, TimeoutExpired  # nosec
from brs_utils  import download_and_extract_tar_gz
from glob       import glob
from filetype   import guess
from brs_utils  import extract_gz
from tempfile   import TemporaryDirectory
from typing     import Dict, List, Tuple
from logging    import Logger
from retropath2_wrapper._version import __version__


__KNIME_VER__        = '4.3.0'
__RETROPATH2_KWF__   = 'RetroPath2.0_r20210127.knwf'


def print_conf(kvars: Dict, logger: Logger = getLogger(__name__)):
    """
    Print configuration.

    Parameters
    ----------
    kvars : Dict
        Dictionnary with variables to print.
    logger : Logger
        The logger object.

    Returns
    -------
    int Return code.

    """
    logger.info('Configuration')
    logger.info(' + '+logger.name)
    logger.info('    - version: '+__version__)
    logger.info(' + KNIME')
    logger.info('    - path: '+kvars['kexec'])
    # logger.info('    - version: '+kvars['kver'])
    logger.info(' + RetroPath2.0 workflow')
    logger.info('    - path: '+kvars['workflow'])
    # logger.info('    - version: r20210127')
    logger.info('')


def retropath2(
    sinkfile: str, sourcefile: str, rulesfile: str,
    outdir: str,
    kexec: str = None, kpkg_install: bool = True, kver: str = None,
    workflow: str = None,
    max_steps: int = 3, topx: int = 100, dmin: int = 0, dmax: int = 100, mwmax_source: int = 1000, mwmax_cof: int = 1000,
    timeout: int = 30,
    is_forward: bool = False,
    logger: Logger = getLogger(__name__)
    ) -> Tuple[int, str]:

    # Create outdir if does not exist
    if not os_path.exists(outdir):
        os_mkdir(outdir)

    # Store KNIME vars into a dictionary
    kvars = set_vars(
        kexec,
        kver,
        kpkg_install,
        workflow)
    logger.debug(kvars)
    # Store RetroPath2 params into a dictionary
    rp2_params = {
        'max_steps'    : max_steps,
        'topx'         : topx,
        'dmin'         : dmin,
        'dmax'         : dmax,
        'mwmax_source' : mwmax_source,
        'mwmax_cof'    : mwmax_cof
    }
    logger.debug(rp2_params)

    # Print out configuration
    print_conf(kvars, logger)

    # Install KNIME
    #      if kexec is not specified
    #  and executable not detected in default path
    if kvars['kexec_install']:
        install_knime(
            kvars['kinstall'],
            kvars['kver'],
            logger)

    logger.info('Initializing')
    # Add packages to KNIME
    if kpkg_install:
        r_code = install_knime_pkgs(
            kvars['kpath'],
            kvars['kver'],
            logger)
        if r_code > 0:
            return r_code, None

    with TemporaryDirectory() as tempd:

        # Format files for KNIME
        files = format_files_for_knime(
                    sinkfile, sourcefile, rulesfile,
                    tempd, outdir,
                    logger
                    )
        logger.debug(files)

        # Call KNIME
        r_code = call_knime(
                    kvars,
                    files,
                    rp2_params,
                    timeout,
                    logger
                    )
        if r_code > 0:
            return r_code, None

        logger.info('Results')
        # Check if source is in sink
        r_code = check_src_in_sink(files, logger=logger)
        if r_code > 0:
            return r_code, None

    code, results_filename = check_scope(outdir, logger)

    return code, results_filename


def set_vars(
    kexec: str,
    kver: str,
    kpkg_install: bool,
    workflow: str
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
    workflow: str
        Path to workflow to process.
    logger : Logger
        The logger object.

    """

    # Take workflow in the package if not passed as an argument
    if workflow is None:
        workflow = os_path.join(
            os_path.dirname(os_path.abspath(__file__)),
            'workflows',
            __RETROPATH2_KWF__
            )

    # Setting kexec, kpath, kinstall, kver
    kexec_install = False
    if kexec is None:
        kinstall = os_path.dirname(os_path.abspath(__file__))
        if not kver:
            kver = __KNIME_VER__
        kpath = os_path.join(
            kinstall,
            'knime_'
            ) + kver
        kexec = os_path.join(
            kpath,
            'knime'
            )
        if not os_path.exists(kexec):
            kexec_install = True
    else:
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
        'workflow'      : workflow
    }


def check_scope(
    outdir: str, logger: Logger = getLogger(__name__)
    ) -> int:
    """
    Check if result is present in outdir.

    Parameters
    ----------
    outdir : str
        The folder where results heve been written.
    logger : Logger
        The logger object.

    Returns
    -------
    int Return code.

    """
    csv_scopes = sorted(
        glob(os_path.join(outdir, '*_scope.csv')),
        key=lambda scope: os_path.getmtime(scope)
        )

    if csv_scopes:
        return 0, csv_scopes[-1]
    else:
        logger.warning('RetroPath2.0 has found no solution')
        return 5, None


def check_src_in_sink(
    files: Dict, logger: Logger = getLogger(__name__)
    ) -> int:
    """
    Check if source is present in sink.

    Parameters
    ----------
    files : Dict
        Dictionnary with paths of source, sink and rules files.
    logger : Logger
        The logger object.

    Returns
    -------
    int Return code.

    """
    logger.info( '   |- Checking... ')

    try:
        count = 0
        with open(os_path.join(files['outdir'], files['src-in-sk'])) as f:
            for i in csv_reader(f, delimiter=',', quotechar='"'):
                count += 1
                if count > 1:
                    logger.error('Source has been found in the sink')
                    return 1

    except FileNotFoundError as e:
        logger.error(e)
        return 2
    
    return 0


def install_knime(
    kinstall: str,
    kver: str,
    logger: Logger = getLogger(__name__)
    ):
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
    logger.info('Downloading KNIME '+kver+'...')

    if sys_platform == 'linux':
        kurl = 'http://download.knime.org/analytics-platform/linux/knime_'+kver+'.linux.gtk.x86_64.tar.gz'
        download_and_extract_tar_gz(kurl, kinstall)

    elif sys_platform == 'darwin':
        # kurl = 'https://download.knime.org/analytics-platform/macosx/knime-'+kver+'-app.macosx.cocoa.x86_64.dmg'
        kurl = 'https://download.knime.org/analytics-platform/macosx/knime-latest-app.macosx.cocoa.x86_64.dmg'

    else:
        kurl = 'https://download.knime.org/analytics-platform/win/knime-'+kver+'-installer-win32.win32.x86_64.exe'

    logger.debug('   |- url: '+kurl)
    logger.debug('   |- install dir: '+kinstall)


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
    logger.info('   |- Formatting files for KNIME...')

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
        'outdir'    : outdir
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
    kpath: str,
    kver: str,
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
    logger.info( '   |- Checking KNIME packages... ')
    logger.debug('        + kpath: '+kpath)
    logger.debug('        + kver: '+kver)

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
      + ' -bundlepool ' + kpath + ' -d ' + kpath

    if ' ' in kpath:
        cmd = '"'+os_path.join(kpath, 'knime')+'"' \
            + args
    else:
        cmd = os_path.join(kpath, 'knime') \
            + args

    try:
        printout = open(devnull, 'wb') if logger.level > 10 else None
        CPE = run(
            cmd.split(),
            stdout=printout,
            stderr=printout,
            shell=False)  # nosec
        logger.debug(CPE)
        return CPE.returncode

    except OSError as e:
        logger.error(e)
        return 3


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

    logger.info('Running KNIME')

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
         + ' -workflow.variable=input.mwmax-cof,"'         + str(params['mwmax_cof'])    + '",int' \
         + ' -workflow.variable=output.dir,"'              + files['outdir']             + '",String' \
         + ' -workflow.variable=output.solutionfile,"'     + files['results']            + '",String' \
         + ' -workflow.variable=output.sourceinsinkfile,"' + files['src-in-sk']          + '",String'

    logger.debug(kvars['kexec'] + ' ' + args)

    try:
        printout = open(devnull, 'wb') if logger.level > 10 else None
        CPE = run(
            [kvars['kexec']] + args.split(),
            stdout=printout,
            stderr=printout,
            timeout=timeout*60,
            shell=False
            )  # nosec
        logger.debug(CPE)
        return CPE.returncode

    except TimeoutExpired as e:
        logger.warning('Time limit ('+str(timeout)+' minutes) reached')
        logger.warning('   |- Results collected until now are available')
        return 6

    except OSError as e:
        logger.error(e)
        return 3

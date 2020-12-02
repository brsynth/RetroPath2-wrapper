#!/usr/bin/env python3
"""
Created on January 16 2020

@author: Melchior du Lac, Joan Hérisson
@description: Python wrapper to run RetroPath2.0 KNIME workflow

"""
from os         import mkdir          as os_mkdir
from os         import path           as os_path
from os         import rename
from shutil     import copyfile
from sys        import platform       as sys_platform
from logging    import getLogger
from csv        import reader         as csv_reader
from resource   import setrlimit, RLIMIT_AS, RLIM_INFINITY
from subprocess import call, STDOUT, TimeoutExpired  # nosec
from brs_utils  import download_and_extract_tar_gz
from glob       import glob
from filetype   import guess
from brs_utils  import extract_gz
from tempfile   import TemporaryDirectory

# KVER         = '3.6.2'
KVER         = '4.2.2'
if sys_platform == 'linux':
    KURL = 'http://download.knime.org/analytics-platform/linux/knime_'+KVER+'.linux.gtk.x86_64.tar.gz'
elif sys_platform == 'darwin':
    KURL = 'https://download.knime.org/analytics-platform/macosx/knime-'+KVER+'-app.macosx.cocoa.x86_64.dmg'
else:
    KURL = 'https://download.knime.org/analytics-platform/win/knime-'+KVER+'-installer-win32.win32.x86_64.exe'
KINSTALL     = os_path.dirname(os_path.abspath(__file__))
KPATH        = os_path.join(KINSTALL, 'knime_')+KVER
KEXEC        = os_path.join(KPATH, 'knime')
RP_WORK_PATH = os_path.join(os_path.dirname(os_path.abspath(__file__)), 'workflow', 'RetroPath2.0-v9.knwf')
MAX_VIRTUAL_MEMORY = 20000*1024*1024  # 20 GB -- define what is the best
EXT = '.csv'

# logging.basicConfig(level=logging.DEBUG)
logger = getLogger(__name__)


def limit_virtual_memory():
    setrlimit(RLIMIT_AS, (MAX_VIRTUAL_MEMORY, RLIM_INFINITY))


def retropath2(sinkfile, sourcefile, rulesfile, outdir,
               kexec='',
               max_steps=3,
               topx=100,
               dmin=0, dmax=100,
               mwmax_source=1000, mwmax_cof=1000,
               timeout=30,
               is_forward=False):

    if not os_path.exists(outdir):
        os_mkdir(outdir)

    if not kexec:
        kexec = KEXEC

    ### run the KNIME RETROPATH2.0 workflow
    try:

        if not os_path.exists(kexec):
            download_and_extract_tar_gz(KURL, KINSTALL)

        # Add packages to Knime
        install_knime_pkgs(kexec)

        with TemporaryDirectory() as tempd:

            rulesfile = format_rulesfile(rulesfile, tempd)

            files = format_files_for_knime(sinkfile, sourcefile, rulesfile, tempd)
            files['outdir'] = outdir

            try:
                call_knime(kexec,
                           files,
                           max_steps,
                           topx,
                           dmin, dmax,
                           mwmax_source, mwmax_cof,
                           timeout)
            except TimeoutExpired:
                return 6, '\n'.join(['*** WARNING',
                                     '      |- Time limit ('+str(timeout)+' minutes) reached',
                                     '      |- Results collected until now are available'])

        ### if source is in sink
        try:
            count = 0
            with open(os_path.join(outdir, files['src-in-sk'])) as f:
                for i in csv_reader(f, delimiter=',', quotechar='"'):
                    count += 1
                    if count > 1:
                        return 1, 'Source has been found in the sink'
        except FileNotFoundError as e:
            return 2, 'Cannot find '+files['src-in-sk']+' file'

    except OSError as e:
        return 3, 'Running the RetroPath2.0 Knime program produced an OSError'
    except ValueError as e:
        return 4, 'Cannot set the RAM usage limit'

    csv_scopes = sorted(glob(os_path.join(outdir, '*_scope.csv')),
                        key=lambda scope: os_path.getmtime(scope))

    if csv_scopes:
        return 0, csv_scopes[-1]
    else:
        return 5, 'RetroPath2.0 has not found any solution'


def format_rulesfile(rulesfile, indir):
    # If 'rulesfile' is a pure gzip archive without tar
    kind = guess(rulesfile)
    if kind:
        if kind.mime == 'application/gzip':
            new_f = os_path.join(indir, os_path.basename(rulesfile)+'.gz')
            copyfile(rulesfile, new_f)
            rulesfile = extract_gz(new_f, indir)
            rename(rulesfile, rulesfile+EXT)
            rulesfile += EXT

    return rulesfile


def format_files_for_knime(sinkfile, sourcefile, rulesfile, indir):

    # Because KNIME accepts only '.csv' file extension, files have to be renamed
    files = {'sink': sinkfile, 'source': sourcefile, 'rules': rulesfile}
    for key in files:
        if os_path.splitext(files[key])[-1] != EXT:
            new_f = os_path.join(indir, os_path.basename(files[key])+EXT)
            copyfile(files[key], new_f)
            files[key] = new_f

    files['results']   = 'results' + EXT
    files['src-in-sk'] = 'source-in-sink' + EXT

    return files


def install_knime_pkgs(kexec):
    knime_add_pkgs = kexec \
        + ' -application org.eclipse.equinox.p2.director' \
        + ' -nosplash -consolelog' \
        + ' -r http://update.knime.org/community-contributions/trunk,' \
            + 'http://update.knime.com/analytics-platform/'+KVER[:3]+',' \
            + 'http://update.knime.com/community-contributions/trusted/'+KVER[:3] \
        + ' -i org.knime.features.chem.types.feature.group,' \
            + 'org.knime.features.datageneration.feature.group,' \
            + 'jp.co.infocom.cheminfo.marvin.feature.feature.group,' \
            + 'org.knime.features.python.feature.group,' \
            + 'org.rdkit.knime.feature.feature.group' \
        + ' -bundlepool ' + KPATH + ' -d ' + KPATH
    call(knime_add_pkgs.split(), stderr=STDOUT, shell=False)  # nosec


def call_knime(kexec, files, max_steps, topx, dmin, dmax, mwmax_source, mwmax_cof, timeout):
    knime_command = kexec \
        + ' -nosplash -nosave -reset --launcher.suppressErrors -application org.knime.product.KNIME_BATCH_APPLICATION ' \
        + ' -workflowFile=' + RP_WORK_PATH \
        + ' -workflow.variable=input.dmin,"'              + str(dmin)           + '",int' \
        + ' -workflow.variable=input.dmax,"'              + str(dmax)           + '",int' \
        + ' -workflow.variable=input.max-steps,"'         + str(max_steps)      + '",int' \
        + ' -workflow.variable=input.sourcefile,"'        + files['source']     + '",String' \
        + ' -workflow.variable=input.sinkfile,"'          + files['sink']       + '",String' \
        + ' -workflow.variable=input.rulesfile,"'         + files['rules']      + '",String' \
        + ' -workflow.variable=input.topx,"'              + str(topx)           + '",int' \
        + ' -workflow.variable=input.mwmax-source,"'      + str(mwmax_source)   + '",int' \
        + ' -workflow.variable=input.mwmax-cof,"'         + str(mwmax_cof)      + '",int' \
        + ' -workflow.variable=output.dir,"'              + files['outdir']     + '",String' \
        + ' -workflow.variable=output.solutionfile,"'     + files['results']    + '",String' \
        + ' -workflow.variable=output.sourceinsinkfile,"' + files['src-in-sk']  + '",String'

    call(knime_command.split(), stderr=STDOUT, timeout=timeout*60, shell=False)  # nosec

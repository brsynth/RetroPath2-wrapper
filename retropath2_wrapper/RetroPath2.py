#!/usr/bin/env python3
"""
Created on January 16 2020

@author: Melchior du Lac, Joan Hérisson
@description: Python wrapper to run RetroPath2.0 KNIME workflow

"""
from os         import mkdir          as os_mkdir
from os         import path           as os_path
from argparse   import ArgumentParser as argparse_ArgumentParser
from logging    import getLogger
from csv        import reader         as csv_reader
from resource   import setrlimit, RLIMIT_AS, RLIM_INFINITY
from subprocess import call, STDOUT, TimeoutExpired# nosec
from brs_utils  import download_and_extract_tar_gz


# KVER         = '3.6.2'
KVER         = '4.2.2'
KURL         = 'http://download.knime.org/analytics-platform/linux/knime_'+KVER+'.linux.gtk.x86_64.tar.gz'
KINSTALL     = os_path.dirname(os_path.abspath( __file__ ))
KPATH        = os_path.join(KINSTALL, 'knime_')+KVER
KEXEC        = os_path.join(KPATH, 'knime')
RP_WORK_PATH = os_path.join(os_path.dirname(os_path.abspath( __file__ )), 'workflow', 'RetroPath2.0-v9.knwf')
MAX_VIRTUAL_MEMORY = 20000*1024*1024 # 20 GB -- define what is the best

##
#
#
def limit_virtual_memory():
    setrlimit(RLIMIT_AS, (MAX_VIRTUAL_MEMORY, RLIM_INFINITY))


##
#
#
def retropath2(sinkfile,
               sourcefile,
               rulesfile,
               outdir,
               kexec='',
               max_steps=3,
               topx=100,
               dmin=0,
               dmax=1000,
               mwmax_source=1000,
               mwmax_cof=1000,
               timeout=30,
               is_forward=False,
               logger=None):

    if not logger:
        # logging.basicConfig(level=logging.DEBUG)
        logger = getLogger(__name__)

    if not os_path.exists(outdir):
        os_mkdir(outdir)

    if not kexec:
        kexec = KEXEC

    ### run the KNIME RETROPATH2.0 workflow
    try:

        results_filename   = 'results.csv'
        src_in_sk_filename = 'source-in-sink.csv'

        if not os_path.exists(kexec):
            download_and_extract_tar_gz(KURL, KINSTALL)
            # Add packages to Knime
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
            call(knime_add_pkgs.split(), stderr=STDOUT, shell=False)# nosec

        knime_command = kexec \
            + ' -nosplash -nosave -reset --launcher.suppressErrors -application org.knime.product.KNIME_BATCH_APPLICATION ' \
            + ' -workflowFile=' + RP_WORK_PATH \
            + ' -workflow.variable=input.dmin,"'              + str(dmin)                + '",int' \
            + ' -workflow.variable=input.dmax,"'              + str(dmax)                + '",int' \
            + ' -workflow.variable=input.max-steps,"'         + str(max_steps)           + '",int' \
            + ' -workflow.variable=input.sourcefile,"'        + sourcefile               + '",String' \
            + ' -workflow.variable=input.sinkfile,"'          + sinkfile                 + '",String' \
            + ' -workflow.variable=input.rulesfile,"'         + rulesfile                + '",String' \
            + ' -workflow.variable=input.topx,"'              + str(topx)                + '",int' \
            + ' -workflow.variable=input.mwmax-source,"'      + str(mwmax_source)        + '",int' \
            + ' -workflow.variable=input.mwmax-cof,"'         + str(mwmax_cof)           + '",int' \
            + ' -workflow.variable=output.dir,"'              + os_path.join(outdir, "") + '",String' \
            + ' -workflow.variable=output.solutionfile,"'     + results_filename         + '",String' \
            + ' -workflow.variable=output.sourceinsinkfile,"' + src_in_sk_filename       + '",String'

        try:
            call(knime_command.split(), stderr=STDOUT, timeout=timeout*60, shell=False)# nosec
        except TimeoutExpired:
            logger.warning('*** WARNING')
            logger.warning('      |- Time limit ('+str(timeout)+' minutes) reached')
            logger.warning('      |- Results collected until now are available')

        ### if source is in sink
        try:
            count = 0
            with open(os_path.join(outdir, src_in_sk_filename)) as f:
                for i in csv_reader(f, delimiter=',', quotechar='"'):
                    count += 1
                    if count>1:
                        logger.error('Source has been found in the sink')
                        return 1
        except FileNotFoundError as e:
            logger.error('Cannot find '+src_in_sk_filename+' file')
            logger.error(e)
            return 2

    except OSError as e:
        logger.error('Running the RetroPath2.0 Knime program produced an OSError')
        logger.error(e)
        return 3
    except ValueError as e:
        logger.error('Cannot set the RAM usage limit')
        logger.error(e)
        return 4

    return os_path.join(outdir, results_filename)

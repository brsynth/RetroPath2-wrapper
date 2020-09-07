#!/usr/bin/env python3
"""
Created on January 16 2020

@author: Melchior du Lac, Joan Hérisson
@description: Python wrapper to run RetroPath2.0 KNIME workflow

"""


from os import mkdir as os_mkdir
from os import path as os_path
from argparse import ArgumentParser as argparse_ArgumentParser
import logging
from csv import reader as csv_reader
import resource
from shutil import copy as shutil_cp
from subprocess import call, STDOUT, TimeoutExpired# nosec
from brs_utils import download_and_extract_gz

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

KVER         = '3.6.2'
KURL         = 'http://download.knime.org/analytics-platform/linux/knime_'+KVER+'.linux.gtk.x86_64.tar.gz'
KINSTALL     = './'
KPATH        = KINSTALL+'/knime_'+KVER
KEXEC        = KPATH+'/knime'
RP_WORK_PATH = os_path.dirname(os_path.abspath( __file__ ))+'/workflow/RetroPath2.0.knwf'
MAX_VIRTUAL_MEMORY = 20000*1024*1024 # 20 GB -- define what is the best

##
#
#
def limit_virtual_memory():
    resource.setrlimit(resource.RLIMIT_AS, (MAX_VIRTUAL_MEMORY, resource.RLIM_INFINITY))


##
#
#
def run(sinkfile,
        sourcefile,
        rulesfile,
        outdir='out',
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
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)

    if not os_path.exists(outdir):
        os_mkdir(outdir)
    shutil_cp(sinkfile, outdir+"/sink.csv")
    shutil_cp(sourcefile, outdir+"/source.csv")
    shutil_cp(rulesfile, outdir+"/rules.csv")

    ### run the KNIME RETROPATH2.0 workflow
    try:

        results_filename   = 'results.csv'
        src_in_sk_filename = 'source-in-sink.csv'

        if not os_path.exists(kexec):
            kexec = KEXEC
            download_and_extract_gz(KURL, KINSTALL)
            # Add packages to Knime
            knime_add_pkgs = KEXEC \
                + ' -application org.eclipse.equinox.p2.director' \
                + ' -nosplash -consolelog' \
                + ' -r http://update.knime.org/community-contributions/trunk,' \
                    + 'http://update.knime.com/analytics-platform/3.6,' \
                    + 'http://update.knime.com/community-contributions/trusted/3.6' \
                + ' -i org.knime.features.chem.types.feature.group,' \
                    + 'org.knime.features.datageneration.feature.group,' \
                    + 'jp.co.infocom.cheminfo.marvin.feature.feature.group,' \
                    + 'org.knime.features.python.feature.group,' \
                    + 'org.rdkit.knime.feature.feature.group' \
                + ' -bundlepool '+KPATH+' -d '+KPATH
            call(knime_add_pkgs.split(), stderr=STDOUT, shell=False)# nosec

        knime_command = kexec \
            + ' -nosplash -nosave -reset --launcher.suppressErrors -application org.knime.product.KNIME_BATCH_APPLICATION ' \
            + ' -workflowFile='+RP_WORK_PATH \
            + ' -workflow.variable=input.dmin,"'+str(dmin)+'",int' \
            + ' -workflow.variable=input.dmax,"'+str(dmax)+'",int' \
            + ' -workflow.variable=input.max-steps,"'+str(max_steps)+'",int' \
            + ' -workflow.variable=input.sourcefile,"'+outdir+"/source.csv"+'",String' \
            + ' -workflow.variable=input.sinkfile,"'+outdir+"/sink.csv"+'",String' \
            + ' -workflow.variable=input.rulesfile,"'+outdir+"/rules.csv"+'",String' \
            + ' -workflow.variable=input.topx,"'+str(topx)+'",int' \
            + ' -workflow.variable=input.mwmax-source,"'+str(mwmax_source)+'",int' \
            + ' -workflow.variable=input.mwmax-cof,"'+str(mwmax_cof)+'",int' \
            + ' -workflow.variable=output.dir,"'+outdir+'/",String' \
            + ' -workflow.variable=output.solutionfile,"'+results_filename+'",String' \
            + ' -workflow.variable=output.sourceinsinkfile,"'+src_in_sk_filename+'",String'

        try:
            call(knime_command.split(), stderr=STDOUT, timeout=timeout*60, shell=False)# nosec
        except TimeoutExpired:
            logger.warning('*** WARNING')
            logger.warning('      |- Time limit ('+str(timeout)+' minutes) reached')
            logger.warning('      |- Results collected until now are available')

        ### if source is in sink
        try:
            count = 0
            with open(outdir+'/'+src_in_sk_filename) as f:
                for i in csv_reader(f, delimiter=',', quotechar='"'):
                    count += 1
                    if count>1:
                        logger.error('Source has been found in the sink')
                        return 'sourceinsinkerror', 'Command: '+str(knime_command)+'\n Error: Source found in Sink'
        except FileNotFoundError as e:
            logger.error('Cannot find'+src_in_sk_filename+' file')
            logger.error(e)
            return 'sourceinsinknotfounderror', 'Command: '+str(knime_command)+'\n Error: '+str(e)

    except OSError as e:
        logger.error('Running the RetroPath2.0 Knime program produced an OSError')
        logger.error(e)
        return 'oserror', 'Command: '+str(knime_command)+'\n Error: '+str(e)
    except ValueError as e:
        logger.error('Cannot set the RAM usage limit')
        logger.error(e)
        return 'ramerror', 'Command: '+str(knime_command)+'\n Error: '+str(e)

    return results_filename


def build_args_parser():
    parser = argparse_ArgumentParser('Python wrapper to parse RP2 to generate rpSBML collection of unique and complete (cofactors) pathways')
    parser = _add_arguments(parser)

    return parser

def _add_arguments(parser):
    parser.add_argument('sinkfile', type=str)
    parser.add_argument('sourcefile', type=str)
    parser.add_argument('rulesfile', type=str)
    parser.add_argument('--outdir', type=str, default='out')
    parser.add_argument('--knime_exec', type=str, default='',
                                        help='path to Knime executable file (Knime will be downloaded if not already installed or path is wrong).')
    parser.add_argument('--max_steps', type=int, default=3)
    parser.add_argument('--topx', type=int, default=100)
    parser.add_argument('--dmin', type=int, default=0)
    parser.add_argument('--dmax', type=int, default=1000)
    parser.add_argument('--mwmax_source', type=int, default=1000)
    parser.add_argument('--mwmax_cof', type=int, default=1000)
    parser.add_argument('--timeout', type=int, default=30)
    parser.add_argument('--is_forward', type=str, default=False)

    return parser

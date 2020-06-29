#!/usr/bin/env python3
"""
Created on January 16 2020

@author: Melchior du Lac
@description: Galaxy script to query rpRetroPath2.0 REST service

"""


import sys
#sys.path.insert(0, '/home/')
import os
import argparse
import subprocess
import logging
import csv
import glob
import resource
import tempfile
from shutil import copy as shutil_cp
from subprocess import STDOUT, check_output, TimeoutExpired

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

KPATH = '/usr/local/knime/knime'
RP_WORK_PATH = '/home/workflows/9/RetroPath2.0.knwf'
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
        max_steps,
        rulesfile,
        outdir,
        topx=100,
        dmin=0,
        dmax=1000,
        mwmax_source=1000,
        mwmax_cof=1000,
        timeout=30,
        is_forward=False,
        logger=None):

    if logger==None:
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)

    if not os.path.exists(outdir):
        os.mkdir(outdir)
    shutil_cp(sinkfile, outdir+"/sink.csv")
    shutil_cp(sourcefile, outdir+"/source.csv")
    shutil_cp(rulesfile, outdir+"/rules.csv")

    ### run the KNIME RETROPATH2.0 workflow
    try:

        results_filename = 'results.csv'
        src_in_sk_filename = 'source-in-sink.csv'

        knime_command = KPATH \
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
            output = check_output(knime_command, stderr=STDOUT, timeout=timeout*60, shell=True)
        except TimeoutExpired:
            logger.warning('*** WARNING')
            logger.warning('      |- Time limit ('+str(timeout)+' minutes) reached')
            logger.warning('      |- Results collected until now are available')

        ### if source is in sink
        try:
            count = 0
            with open(outdir+'/'+src_in_sk_filename) as f:
                for i in csv.reader(f, delimiter=',', quotechar='"'):
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

    return 'Job', 'SUCCESS'




def build_parser():
    #### WARNING: as it stands one can only have a single source molecule
    parser = argparse.ArgumentParser('Python wrapper for the KNIME workflow to run RetroPath2.0')
    parser.add_argument('-sinkfile', type=str)
    parser.add_argument('-sourcefile', type=str)
    parser.add_argument('-max_steps', type=int)
    parser.add_argument('-rulesfile', type=str)
    parser.add_argument('-topx', type=int)
    parser.add_argument('-dmin', type=int)
    parser.add_argument('-dmax', type=int)
    parser.add_argument('-mwmax_source', type=int)
    parser.add_argument('-mwmax_cof', type=int)
    parser.add_argument('-outdir', type=str)
    parser.add_argument('-timeout', type=int)
    parser.add_argument('-is_forward', type=str)

    return parser


def entrypoint(params=sys.argv[1:]):
    parser = build_parser()

    args = parser.parse_args(params)

    if args.is_forward=='False' or args.is_forward=='false' or args.is_forward==False:
        args.is_forward = False
    elif args.is_forward=='True' or args.is_forward=='true' or args.is_forward==True:
        args.is_forward = True
    if (args.rulesfile==None) or (args.rulesfile==b'None') or (args.rulesfile=='None') or (args.rulesfile=='') or (args.rulesfile==b''):
        args.rulesfile = os.getcwd()+'/in/empty_file.csv'
    result = run(args.sinkfile,
                args.sourcefile,
                args.max_steps,
                args.rulesfile,
                args.outdir,
                args.topx,
                args.dmin,
                args.dmax,
                args.mwmax_source,
                args.mwmax_cof,
                args.timeout,
                args.is_forward,
                logger)

    return result


if __name__ == '__main__':
    entrypoint()

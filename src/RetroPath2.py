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
def run(sinkfile, sourcefile, max_steps, rulesfile, outdir, topx=100, dmin=0, dmax=1000, mwmax_source=1000, mwmax_cof=1000, timeout=30, is_forward=False, logger=None):
    if logger==None:
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)

    os.mkdir(outdir)

    ### run the KNIME RETROPATH2.0 workflow
    try:

        knime_command = KPATH \
            + ' -nosplash -nosave -reset --launcher.suppressErrors -application org.knime.product.KNIME_BATCH_APPLICATION ' \
            + ' -workflowFile='+RP_WORK_PATH \
            + ' -workflow.variable=input.dmin,"'+str(dmin)+'",int' \
            + ' -workflow.variable=input.dmax,"'+str(dmax)+'",int' \
            + ' -workflow.variable=input.max-steps,"'+str(max_steps)+'",int' \
            + ' -workflow.variable=input.sourcefile,"'+str(sourcefile)+'",String' \
            + ' -workflow.variable=input.sinkfile,"'+str(sinkfile)+'",String' \
            + ' -workflow.variable=input.rulesfile,"'+str(rulesfile)+'",String' \
            + ' -workflow.variable=output.topx,"'+str(topx)+'",int' \
            + ' -workflow.variable=output.mwmax-source,"'+str(mwmax_source)+'",int' \
            + ' -workflow.variable=output.mwmax-cof,"'+str(mwmax_cof)+'",int' \
            + ' -workflow.variable=output.dir,"'+str(outdir)+'/",String' \
            + ' -workflow.variable=output.solutionfile,"results.csv",String' \
            + ' -workflow.variable=output.sourceinsinkfile,"source-in-sink.csv",String'

        commandObj = subprocess.Popen(knime_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=limit_virtual_memory)

        try:
            commandObj.wait(timeout=timeout*60.0)
        except subprocess.TimeoutExpired as e:
            logger.error('Timeout from retropath2.0 ('+str(timeout)+' minutes)')
            commandObj.kill()
            return 'timeout', 'Command: '+str(knime_command)+'\n Error: '+str(e)

        (result, error) = commandObj.communicate()
        result = result.decode('utf-8')
        error = error.decode('utf-8')

        ### if java has a memory issue
        if 'There is insufficient memory for the Java Runtime Environment to continue' in result:
            logger.error('RetroPath2.0 does not have sufficient memory to continue')
            return 'memerror', 'Command: '+str(knime_command)+'\n Error: Memory error'

        ### if source is in sink
        try:
            count = 0
            with open(outdir+'/source-in-sink.csv') as f:
                reader = csv.reader(f, delimiter=',', quotechar='"')
                for i in reader:
                    count += 1
            if count>1:
                logger.error('Source has been found in the sink')
                return 'sourceinsinkerror', 'Command: '+str(knime_command)+'\n Error: Source found in sink'
        except FileNotFoundError as e:
            logger.error('Cannot find source-in-sink.csv file')
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
    result = run(
            args.sinkfile,
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
            logger
            )

    return result


if __name__ == '__main__':
    entrypoint()

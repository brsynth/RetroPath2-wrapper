#!/usr/bin/env python3
"""
Created on January 16 2020

@author: Melchior du Lac
@description: Galaxy script to query rpRetroPath2.0 REST service

"""


import sys
sys.path.insert(0, '/home/')
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
def run(sinkfile_bytes, sourcefile_bytes, max_steps, rules_bytes=b'None', topx=100, dmin=0, dmax=1000, mwmax_source=1000, mwmax_cof=1000, timeout=30, is_forward=False, logger=None):
    if logger==None:
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)
    with tempfile.TemporaryDirectory() as tmpOutputFolder:
        sink_path = tmpOutputFolder+'/tmp_sink.csv'
        with open(sink_path, 'wb') as outfi:
            outfi.write(sinkfile_bytes)
        source_path = tmpOutputFolder+'/tmp_source.csv'
        with open(source_path, 'wb') as outfi:
            outfi.write(sourcefile_bytes)
        #rulesfile, fname_rules = readCopyFile(rulesfile, tmpOutputFolder)
        rules_path = tmpOutputFolder+'/tmp_rules.csv'
        with open(rules_path, 'wb') as outfi:
            outfi.write(rules_bytes)
        ### run the KNIME RETROPATH2.0 workflow
        try:
            knime_command = KPATH \
                + ' -nosplash -nosave -reset --launcher.suppressErrors -application org.knime.product.KNIME_BATCH_APPLICATION ' \
                + ' -workflowFile='+RP_WORK_PATH \
                + ' -workflow.variable=input.dmin,"'+str(dmin)+'",int' \
                + ' -workflow.variable=input.dmax,"'+str(dmax)+'",int' \
                + ' -workflow.variable=input.max-steps,"'+str(max_steps)+'",int' \
                + ' -workflow.variable=input.sourcefile,"'+str(source_path)+'",String' \
                + ' -workflow.variable=input.sinkfile,"'+str(sink_path)+'",String' \
                + ' -workflow.variable=input.rulesfile,"'+str(rules_path)+'",String' \
                + ' -workflow.variable=output.topx,"'+str(topx)+'",int' \
                + ' -workflow.variable=output.mwmax-source,"'+str(mwmax_source)+'",int' \
                + ' -workflow.variable=output.mwmax-cof,"'+str(mwmax_cof)+'",int' \
                + ' -workflow.variable=output.dir,"'+str(tmpOutputFolder)+'/",String' \
                + ' -workflow.variable=output.solutionfile,"results.csv",String' \
                + ' -workflow.variable=output.sourceinsinkfile,"source-in-sink.csv",String'
            print(knime_command)
            commandObj = subprocess.Popen(knime_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=limit_virtual_memory)
            try:
                commandObj.wait(timeout=timeout*60.0)
            except subprocess.TimeoutExpired as e:
                logger.error('Timeout from retropath2.0 ('+str(timeout)+' minutes)')
                commandObj.kill()
                return b'', b'timeout', 'Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))
            (result, error) = commandObj.communicate()
            result = result.decode('utf-8')
            error = error.decode('utf-8')
            ### if java has a memory issue
            if 'There is insufficient memory for the Java Runtime Environment to continue' in result:
                logger.error('RetroPath2.0 does not have sufficient memory to continue')
                return b'', b'memerror', 'Command: '+str(knime_command)+'\n Error: Memory error \n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))
            ### if source is in sink
            try:
                count = 0
                with open(tmpOutputFolder+'/source-in-sink.csv') as f:
                    reader = csv.reader(f, delimiter=',', quotechar='"')
                    for i in reader:
                        count += 1
                if count>1:
                    logger.error('Source has been found in the sink')
                    return b'', b'sourceinsinkerror', 'Command: '+str(knime_command)+'\n Error: Source found in sink\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))
            except FileNotFoundError as e:
                logger.error('Cannot find source-in-sink.csv file')
                logger.error(e)
                return b'', b'sourceinsinknotfounderror', 'Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))
            ### csv scope copy to the .dat location
            try:
                csv_scope = glob.glob(tmpOutputFolder+'/*_scope.csv')
                with open(csv_scope[0], 'rb') as op:
                    scope_csv = op.read()
                return scope_csv, b'noerror', ''
            except IndexError as e:
                logger.error('RetroPath2.0 has not found any results')
                logger.error(e)
                return b'', b'noresulterror', 'Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))
        except OSError as e:
            logger.error('Running the RetroPath2.0 Knime program produced an OSError')
            logger.error(e)
            return b'', b'oserror', 'Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))
        except ValueError as e:
            logger.error('Cannot set the RAM usage limit')
            logger.error(e)
            return b'', b'ramerror', 'Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))



if __name__ == "__main__":
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
    parser.add_argument('-server_url', type=str)
    parser.add_argument('-scope_csv', type=str)
    parser.add_argument('-timeout', type=int)
    parser.add_argument('-is_forward', type=str)
    params = parser.parse_args()
    if params.is_forward=='False' or params.is_forward=='false' or params.is_forward==False:
        params.is_forward = False
    elif params.is_forward=='True' or params.is_forward=='true' or params.is_forward==True:
        params.is_forward = True
    if (params.rulesfile==None) or (params.rulesfile==b'None') or (params.rulesfile=='None') or (params.rulesfile=='') or (params.rulesfile==b''):
        params.rulesfile = os.getcwd()+'/empty_file.csv'
        with open(params.rulesfile, 'wb') as ef:
            ef.write(b'')
    with open(params.sinkfile, 'rb') as sinkfile_bytes:
        with open(params.sourcefile, 'rb') as sourcefile_bytes:
            with open(params.rulesfile, 'rb') as rulesfile_bytes:
                result = run(sinkfile_bytes.read(),
                             sourcefile_bytes.read(),
                             params.max_steps,
                             rulesfile_bytes.read(),
                             params.topx,
                             params.dmin,
                             params.dmax,
                             params.mwmax_source,
                             params.mwmax_cof,
                             params.timeout,
                             params.is_forward,
                             logger)
    with open(params.scope_csv, 'wb') as s_c:
        s_c.write(result[0])

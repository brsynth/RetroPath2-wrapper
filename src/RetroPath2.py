#!/usr/bin/env python3
"""
Created on January 16 2020

@author: Melchior du Lac
@description: Galaxy script to query rpRetroPath2.0 REST service

"""


import subprocess
import logging
import csv
import glob
import resource
import tempfile


KPATH = '/usr/local/knime/knime'
RP_WORK_PATH = '/home/workflow/RetroPath2.0.knwf'
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
            knime_command = KPATH+' -nosplash -nosave -reset --launcher.suppressErrors -application org.knime.product.KNIME_BATCH_APPLICATION -workflowFile='+RP_WORK_PATH+' -workflow.variable=input.dmin,"'+str(dmin)+'",int -workflow.variable=input.dmax,"'+str(dmax)+'",int -workflow.variable=input.max-steps,"'+str(max_steps)+'",int -workflow.variable=input.sourcefile,"'+str(source_path)+'",String -workflow.variable=input.sinkfile,"'+str(sink_path)+'",String -workflow.variable=input.rulesfile,"'+str(rules_path)+'",String -workflow.variable=output.topx,"'+str(topx)+'",int -workflow.variable=output.mwmax-source,"'+str(mwmax_source)+'",int -workflow.variable=output.mwmax-cof,"'+str(mwmax_cof)+'",int -workflow.variable=output.dir,"'+str(tmpOutputFolder)+'/",String -workflow.variable=output.solutionfile,"results.csv",String -workflow.variable=output.sourceinsinkfile,"source-in-sink.csv",String'
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

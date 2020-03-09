#!/usr/bin/env python3
"""
Created on September 21 2019

@author: Melchior du Lac
@description: Galaxy script to query rpRetroPath2.0 REST service

"""
import sys
sys.path.insert(0, '/home/')
import os
import argparse
import logging

import src.RetroPath2 as RP2

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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
                result = RP2.run_rp2(sinkfile_bytes.read(),
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

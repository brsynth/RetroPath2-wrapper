"""
Created on March 7 2019

@author: Melchior du Lac
@description: Standalone version of RP2paths. Returns bytes to be able to use the same file in REST application

"""
import subprocess
import tempfile
import logging
import resource
import glob
# import io
# import tarfile
# #from flask import Flask, request, jsonify, send_file, abort
# from flask import request, Response, send_file
# import json

MAX_VIRTUAL_MEMORY = 20000 * 1024 * 1024 # 20GB -- define what is the best
#MAX_VIRTUAL_MEMORY = 20 * 1024 * 1024 # 20GB -- define what is the best

##
#
#
def limit_virtual_memory():
    resource.setrlimit(resource.RLIMIT_AS, (MAX_VIRTUAL_MEMORY, resource.RLIM_INFINITY))

sys.path.insert(0, '/home/')
from src.RetroPath2 import run as run_rp2

##
#
#
#def run(rp2_pathways_bytes, timeout, logger=None):
def run(args):
    return run_rp2(
                args['sinkfile_bytes'],
                args['sourcefile_bytes'],
                args['max_steps'],
                args['rules_bytes'],
                args['topx'],
                args['dmin'],
                args['dmax'],
                args['mwmax_source'],
                args['mwmax_cof'],
                args['timeout'],
                args['is_forward'],
                args['logger']
                )


from flask import request, Response, send_file
import io
import tarfile
import json
import logging

def post(rest_query):
    sourcefile_bytes = request.files['sourcefile'].read()
    sinkfile_bytes = request.files['sinkfile'].read()
    rulesfile_bytes = request.files['rulesfile'].read()
    params = json.load(request.files['data'])
    args = {
            'sinkfile_bytes': sinkfile_bytes,
            'sourcefile_bytes': sourcefile_bytes,
            'max_steps': int(params['max_steps']),
            'rulesfile_bytes': rulesfile_bytes,
            'topx': int(params['topx']),
            'dmin': int(params['dmin']),
            'dmax': int(params['dmax']),
            'mwmax_source': int(params['mwmax_source']),
            'mwmax_cof': int(params['mwmax_cof']),
            'timeout': int(params['timeout']),
            'is_forward': bool(params['is_forward']),
            'logger': None
           }
    result = rest_query.run(args)
    if result[0]==b'':
        app.logger.error('Empty results')
        return Response("Empty results \n"+str(result[2]), status=400)
    elif result[1]==b'timeout':
        app.logger.error.error('Timeout of RetroPath2.0')
        return Response("Timeout of RetroPath2.0 \n"+str(result[2]), status=400)
    elif result[1]==b'memoryerror':
        app.logger.error.error('Memory allocation error')
        return Response("Memory allocation error \n"+str(result[2]), status=400)
    elif result[1]==b'oserror':
        app.logger.error.error('rp2paths has generated an OS error')
        return Response("rp2paths has generated an OS error \n"+str(result[2]), status=400)
    elif result[1]==b'ramerror':
        app.logger.error.error('Could not setup a RAM limit')
        return Response("Could not setup a RAM limit \n"+str(result[2]), status=400)
    scope_csv = io.BytesIO()
    scope_csv.write(result[0])
    ###### IMPORTANT ######
    scope_csv.seek(0)
    #######################
    return send_file(scope_csv, as_attachment=True, attachment_filename='rp2_pathways.csv', mimetype='text/csv')

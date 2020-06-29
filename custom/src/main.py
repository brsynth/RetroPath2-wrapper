#!/usr/bin/env python3

from os import path as os_path
from os import mkdir as os_mkdir



from retropath2 import run, build_parser

def _cli():
    parser = build_parser()
    params = parser.parse_args()
    if not os_path.exists(params.outdir):
        os_mkdir(params.outdir)
    return run(params.sinkfile, params.sourcefile, params.max_steps, params.rulesfile, params.outdir)

if __name__ == '__main__':
    _cli()

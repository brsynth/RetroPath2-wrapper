#!/usr/bin/env python


from os       import getcwd     as os_getcwd
from tempfile import gettempdir

from brs_utils          import extract_gz
from retropath2_wrapper import retropath2, build_args_parser


def _cli():
    parser = build_args_parser()
    args  = parser.parse_args()

    # If rulesfile is a pure gzip archive without tar
    if args.rulesfile.endswith('.gz') and '.tar.' not in args.rulesfile:
        args.rulesfile = extract_gz(args.rulesfile, gettempdir())

    outFile = retropath2(args.sinkfile,
                         args.sourcefile,
                         args.rulesfile,
                         args.outdir,
                         args.knime_exec,
                         args.max_steps,
                         args.topx,
                         args.dmin,
                         args.dmax,
                         args.mwmax_source,
                         args.mwmax_cof,
                         args.timeout,
                         args.forward)

    print(outFile)


if __name__ == '__main__':
    _cli()

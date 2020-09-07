#!/usr/bin/env python


from os import getcwd as os_getcwd

from retropath2_wrapper import run, build_args_parser


def _cli():
    parser = build_args_parser()
    args  = parser.parse_args()

    args.is_forward = args.is_forward.lower() in ['true', 't']

    if not args.rulesfile or (args.rulesfile==b'None') or (args.rulesfile=='None') or (args.rulesfile=='') or (args.rulesfile==b''):
        args.rulesfile = os_getcwd()+'/in/empty_file.csv'
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
                 args.is_forward)

    return result


if __name__ == '__main__':
    _cli()

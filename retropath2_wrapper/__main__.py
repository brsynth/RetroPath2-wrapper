#!/usr/bin/env python


from retropath2_wrapper import retropath2, build_args_parser
from os                 import path as os_path
from sys                import exit as sys_exit


def _cli():
    parser = build_args_parser()
    args  = parser.parse_args()

    r_code, result = retropath2(args.sinkfile, args.sourcefile, args.rulesfile,
                                args.outdir,
                                args.knime_exec,
                                args.max_steps,
                                args.topx,
                                args.dmin, args.dmax,
                                args.mwmax_source, args.mwmax_cof,
                                args.timeout,
                                args.forward)


    print()
    if r_code > 0:
        print('*** Error:')
        print(end='     ')
    else:
        print('Results are stored in', end='')
    print(result)
    print()


if __name__ == '__main__':
    _cli()

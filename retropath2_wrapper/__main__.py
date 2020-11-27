#!/usr/bin/env python


from retropath2_wrapper import retropath2, build_args_parser


def _cli():
    parser = build_args_parser()
    args  = parser.parse_args()

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

    print()
    print("Results are stored in", outFile)
    print()


if __name__ == '__main__':
    _cli()

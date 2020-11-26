#!/usr/bin/env python


from os       import getcwd     as os_getcwd
from tempfile import gettempdir

from retropath2_wrapper import retropath2, build_args_parser


def _cli():
    parser = build_args_parser()
    args  = parser.parse_args()

# from shutil     import copy           as shutil_cp
    # shutil_cp(sinkfile,   os_path.join(outdir, "sink.csv"))
    # shutil_cp(sourcefile, os_path.join(outdir, "source.csv"))
    # untar_rulesfile = rulesfile

    # from brs_utils  import extract_tar_gz
    # if args.rulesfile.endswith('.gz') or args.rulesfile.endswith('.tgz'):
    #     extract_tar_gz(args.rulesfile, gettempdir())

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

    print("Results are stored in", outFile)


if __name__ == '__main__':
    _cli()

#!/usr/bin/env python


from retropath2_wrapper import (
    retropath2,
    build_args_parser
)
from os import (
    path as os_path
)
from sys import (
    exit as sys_exit
)
from brs_utils import (
    create_logger
)


def _cli():
    parser = build_args_parser()
    args  = parser.parse_args()
    if args.kver is None and args.kpkg_install and args.kexec is not None:
        parser.error("--kexec requires --kver.")

    # Create logger
    logger = create_logger(parser.prog, args.log)

    logger.debug(args)

    r_code, r_filename = retropath2(
        args.sinkfile, args.sourcefile, args.rulesfile,
        args.outdir,
        args.kexec, args.kpkg_install, args.kver,
        args.kwf,
        args.max_steps, args.topx, args.dmin, args.dmax, args.mwmax_source, args.mwmax_cof,
        args.timeout,
        args.forward,
        logger=logger
        )

    if r_code == 0:
        logger.info('   |- path: '+args.outdir)


if __name__ == '__main__':
    _cli()

#!/usr/bin/env python


from retropath2_wrapper import (
    retropath2,
    build_args_parser
)
from os import (
    path as os_path,
    mkdir as os_mkdir
)
from sys import (
    exit as sys_exit
)
from brs_utils import (
    create_logger
)
from argparse import ArgumentParser


def _cli():
    parser = build_args_parser()
    args = parse_and_check_args(parser)

    # Create logger
    logger = create_logger(parser.prog, args.log)

    logger.debug(args)

    r_code, r_filename = retropath2(
        args.sink_file, args.target_file, args.rules_file,
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


def parse_and_check_args(
    parser: ArgumentParser
) -> None:

    args = parser.parse_args()

    if args.kver is None and args.kpkg_install and args.kexec is not None:
        parser.error("--kexec requires --kver.")

    # Create outdir if does not exist
    if not os_path.exists(args.outdir):
        os_mkdir(args.outdir)

    if args.target_file is not None:
        if args.target_name is not None:
            parser.error("--target_name is not compliant with --target_file.")
        if args.target_inchi is not None:
            parser.error("--target_inchi is not compliant with --target_file.")
    else:
        if args.target_inchi is None:
            parser.error("--target_inchi is mandatory.")
        if args.target_name is None or args.target_name == '':
            args.target_name = 'target'
        # Create temporary source file
        args.target_file = os_path.join(args.outdir, 'source.csv')
        with open(args.target_file, 'w') as temp_f:
            temp_f.write('Name,InChI\n')
            temp_f.write('"%s","%s"' % (args.target_name, args.target_inchi))

    return args


if __name__ == '__main__':
    _cli()

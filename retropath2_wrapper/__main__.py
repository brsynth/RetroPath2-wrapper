#!/usr/bin/env python


from retropath2_wrapper import retropath2, build_args_parser
from os                 import path as os_path
from sys                import exit as sys_exit
from colorlog           import ColoredFormatter
from logging import (
    Logger,
    getLogger,
    StreamHandler
)


def _cli():
    parser = build_args_parser()
    args  = parser.parse_args()
    if args.kver is None and not args.skip_kpkg_install and not args.kexec is None:
        parser.error("--kexec requires --kver.")

    # Create logger
    logger = create_logger(parser.prog, args.log)

    logger.debug(args)

    r_code, r_filename = retropath2(
        args.sinkfile, args.sourcefile, args.rulesfile,
        args.outdir,
        args.kexec, not args.skip_kpkg_install, args.kver,
        args.kwf,
        args.max_steps, args.topx, args.dmin, args.dmax, args.mwmax_source, args.mwmax_cof,
        args.timeout,
        args.forward,
        logger=logger
        )

    if r_code == 0:
        logger.info('   |- path: '+args.outdir)


def create_logger(
    name: str = __name__,
    log_level: str = 'def_info'
    ) -> Logger:
    """
    Create a logger with name and log_level.

    Parameters
    ----------
    name : str
        A string containing the name that the logger will print out

    log_level : str
        A string containing the verbosity of the logger

    Returns
    -------
    Logger
        The logger object.

    """    
    logger  = getLogger(name)
    handler = StreamHandler()

    if log_level.startswith('def_'):
        log_format = '%(log_color)s%(message)s%(reset)s'
        log_level  = log_level[4:]
    else:
        log_format = '%(log_color)s%(levelname)-8s | %(asctime)s.%(msecs)03d %(module)s - %(funcName)s(): %(message)s%(reset)s'
 
    formatter = ColoredFormatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(log_level.upper())

    return logger


if __name__ == '__main__':
    _cli()

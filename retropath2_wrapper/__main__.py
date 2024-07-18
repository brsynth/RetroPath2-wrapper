#!/usr/bin/env python
import os
import sys
from os import (
    path as os_path,
    mkdir as os_mkdir,
)
from argparse import ArgumentParser
from logging import (
    Logger,
    getLogger
)
from glob import glob
from typing import (
    Dict,
)
from colored import fg, attr

from brs_utils import (
    create_logger
)

from .RetroPath2 import (
    retropath2
)
from .Args import (
    build_args_parser,
    RETCODES
)
from ._version import __version__
from .knime import Knime


def print_conf(
    knime: Knime,
    prog: str,
    logger: Logger = getLogger(__name__)
) -> None:
    """
    Print configuration.

    Parameters
    ----------
    knime: Knime
        A Knime object
    logger : Logger
        The logger object.

    Returns
    -------
    int Return code.

    """
    # print ('%s%s Configuration %s' % (fg('magenta'), attr('bold'), attr('reset')))
    print('{fg}{attr1}Configuration {attr2}'.format(fg=fg('cyan'), attr1=attr('bold'), attr2=attr('reset')))
    print('{fg}'.format(fg=fg('cyan')), end='')
    print(' + ' + prog)
    print('     |--version: '+__version__)
    print(' + KNIME')
    print('     |--path: '+knime.kexec)
    # logger.info('    - version: '+kvars['kver'])
    print(' + RetroPath2.0 workflow')
    print('     |--path: '+knime.workflow)
    # logger.info('    - version: r20210127')
    print('')
    print ('{attr}'.format(attr=attr('reset')), end='')


def _cli():
    parser = build_args_parser()
    args = parse_and_check_args(parser)

    if args.log.lower() in ['silent', 'quiet'] or args.silent:
        args.log = 'CRITICAL'

    # Create logger
    logger = create_logger(parser.prog, args.log)

    # Create Knime object
    here = os_path.dirname(os_path.realpath(__file__))
    if args.kplugins == "":
        kplugins = []
    else:
        kplugins = args.kplugins.split(',')
    knime = Knime(
        kexec=args.kexec,
        kinstall=args.kinstall,
        kver=args.kver,
        kplugins=kplugins,
        workflow=os_path.join(here, 'workflows', 'RetroPath2.0_%s.knwf' % (args.rp2_version,)),
        network=not args.no_network,
    )
    # Print out configuration
    if not args.silent and args.log.lower() not in ['critical', 'error']:
        print_conf(knime, prog = parser.prog)

    logger.debug('args: ' + str(args))

    r_code, result_files = retropath2(
        sink_file=args.sink_file,
        source_file=args.source_file,
        rules_file=args.rules_file,
        outdir=args.outdir,
        max_steps=args.max_steps,
        topx=args.topx,
        dmin=args.dmin,
        dmax=args.dmax,
        mwmax_source=args.mwmax_source,
        rp2_version=None,
        knime=knime,
        msc_timeout=args.msc_timeout,
        logger=logger
    )

    logger.info('')

    if r_code == RETCODES['OK']:
        logger.info('{attr1}Results{attr2}'.format(attr1=attr('bold'), attr2=attr('reset')))
        logger.info('   |- Checking... ')
        r_code = check_results(result_files, logger)
        logger.info('   |--path: '+args.outdir)
    elif r_code == RETCODES['NoSolution']:
        logger.warning('No solution has been found.')
        logger.warning('Exiting...')
    elif r_code == RETCODES['SrcInSink']:
        logger.warning('It seems that the target product is already in the chassis.')
        logger.warning('Exiting...')
    elif r_code == RETCODES['SinkFileMalformed']:
        logger.error('The sink file is malformed.')
        logger.error('Exiting...')
    else:
        logger.error(f'The following error occured: {r_code}')
        logger.error('Exiting...')

    return r_code


def check_results(
    result_files: Dict,
    logger: Logger = getLogger(__name__)
) -> int:

    # Check if any result has been found
    r_code = check_scope(result_files['outdir'], logger)
    return r_code


def check_scope(
    outdir: str,
    logger: Logger = getLogger(__name__)
) -> int:
    """
    Check if result is present in outdir.

    Parameters
    ----------
    outdir : str
        The folder where results heve been written.
    logger : Logger
        The logger object.

    Returns
    -------
    int Return code.

    """
    csv_scopes = sorted(
        glob(os_path.join(outdir, '*_scope.csv')),
        key=lambda scope: os_path.getmtime(scope)
        )

    if csv_scopes == []:
        logger.warning('       Warning: No solution has been found')
        return RETCODES['NoSolution']

    return RETCODES['OK']


def parse_and_check_args(
    parser: ArgumentParser
):

    args = parser.parse_args()

    if args.kexec is not None:
        if not os.path.isfile(args.kexec):
            parser.error("--kexec is not a file: %s" %(args.kexec,))
        if not os.access(args.kexec, os.X_OK):
            parser.error("--kexec is not executable: %s" %(args.kexec,))

    # Create outdir if does not exist
    if not os_path.exists(args.outdir):
        os_mkdir(args.outdir)

    if args.source_file is not None:
        if args.source_name is not None:
            parser.error("--source_name is not compliant with --source_file.")
        if args.source_inchi is not None:
            parser.error("--source_inchi is not compliant with --source_file.")
    else:
        if args.source_inchi is None:
            parser.error("--source_inchi is mandatory.")
        if args.source_name is None or args.source_name == '':
            args.source_name = 'target'
        # Create temporary source file
        args.source_file = os_path.join(args.outdir, 'source.csv')
        with open(args.source_file, 'w') as temp_f:
            temp_f.write('Name,InChI\n')
            temp_f.write('"%s","%s"' % (args.source_name, args.source_inchi.strip()))

    return args


if __name__ == '__main__':
    sys.exit(_cli())

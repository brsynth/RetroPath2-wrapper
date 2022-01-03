"""
Created on May 4 2020

@author: Joan Hérisson

"""

from argparse import ArgumentParser
from retropath2_wrapper._version import __version__

DEFAULT_TIMEOUT = 60
DEFAULT_KNIME_VERSION = '4.3.0'
DEFAULT_RP2_VERSION = '20211221'

def build_args_parser():
    parser = ArgumentParser(prog='retropath2_wrapper', description='Python wrapper to parse RP2 to generate rpSBML collection of unique and complete (cofactors) pathways')
    parser = _add_arguments(parser)

    return parser


def _add_arguments(parser):

    ## Positional arguments
    #

    parser.add_argument(
        'sink_file',
        type=str,
        help='Path of file containing metabolites present in the system'
    )
    # parser.add_argument(
    #     'source',
    #     type=str,
    #     help='InChI of compound to produce if starts with \'InchI=\', path of file containing the InChI otherwise'
    # )
    parser.add_argument(
        'rules_file',
        type=str,
        help='Path of file containing reaction rules'
    )
    parser.add_argument(
        'outdir',
        type=str,
        help='Folder path where results will be written into'
    )


    ## Optional arguments
    #

    # KNIME options
    parser.add_argument(
        '--source_file',
        type=str,
        help='Path of file containing the InChI (not compliant with --source_name nor --source_inchi)'
    )
    parser.add_argument(
        '--source_name',
        type=str,
        default=None,
        help='Name of compound to produce (needs --inchi, not compliant with --source_file).'
    )
    parser.add_argument(
        '--source_inchi',
        type=str,
        default=None,
        help='InChI of compound to produce (not compliant with --source_file).'
    )
    parser.add_argument(
        '--kexec',
        type=str,
        default=None,
        help='path to KNIME executable file (KNIME will be \
              downloaded if not already installed or path is \
              wrong).'
    )
    parser.add_argument(
        '--kver',
        type=str,
        default=DEFAULT_KNIME_VERSION,
        help='version of KNIME (mandatory if --kexec is passed).',
    )
    parser.add_argument(
        '--kpkg_install',
        action='store_true',
        default=False,
        help='Install Knime packages (default: False).'
    )
    parser.add_argument(
        '--rp2_version',
        type=str,
        default=DEFAULT_RP2_VERSION,
        choices=['20210127', '20211221'],
        help=f'version of RetroPath2.0 workflow (default: {DEFAULT_RP2_VERSION}).'
    )

    # RetroPath2.0 workflow options
    parser.add_argument('--max_steps'    , type=int, default=3)
    parser.add_argument('--topx'         , type=int, default=100)
    parser.add_argument('--dmin'         , type=int, default=0)
    parser.add_argument('--dmax'         , type=int, default=1000)
    parser.add_argument('--mwmax_source' , type=int, default=1000)
    parser.add_argument('--mwmax_cof'    , type=int, default=1000)
    parser.add_argument(
        '--timeout',
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f'Defines the time after which the program will stop and return calculated results (default: {DEFAULT_TIMEOUT})'
    )
    # parser.add_argument('--forward'      , action='store_true')

    # Program options
    parser.add_argument(
        '--log',
        metavar='ARG',
        type=str,
        choices=[
            'debug', 'info', 'warning', 'error', 'critical', 'silent', 'quiet',
            'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'SILENT', 'QUIET'
        ],
        default='def_info',
        help='Adds a console logger for the specified level (default: error)'
    )
    parser.add_argument(
        '--silent',
        action='store_true',
        default=False,
        help='run %(prog)s silently'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(__version__),
        help='show the version number and exit'
    )

    return parser

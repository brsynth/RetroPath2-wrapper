"""
Created on May 4 2020

@author: Joan Hérisson

"""

from argparse  import ArgumentParser
from retropath2_wrapper._version import __version__


def build_args_parser():
    parser = ArgumentParser(prog='retropath2_wrapper', description='Python wrapper to parse RP2 to generate rpSBML collection of unique and complete (cofactors) pathways')
    parser = _add_arguments(parser)

    return parser


def _add_arguments(parser):

    ## Positional arguments
    #

    parser.add_argument('sinkfile'   , type=str)
    parser.add_argument('sourcefile' , type=str)
    parser.add_argument('rulesfile'  , type=str)
    parser.add_argument('outdir'     , type=str)


    ## Optional arguments
    #

    # KNIME options
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
        default=None,
        help='version of KNIME (mandatory if --kexec is passed).',
    )
    parser.add_argument(
        '--kpkg_install',
        action='store_true',
        default=False,
        help='Install Knime packages (default: False).'
    )
    parser.add_argument(
        '--kwf',
        type=str,
        help='path to Knime workflow file.'
    )

    # RetroPath2.0 workflow options
    parser.add_argument('--max_steps'    , type=int, default=3)
    parser.add_argument('--topx'         , type=int, default=100)
    parser.add_argument('--dmin'         , type=int, default=0)
    parser.add_argument('--dmax'         , type=int, default=1000)
    parser.add_argument('--mwmax_source' , type=int, default=1000)
    parser.add_argument('--mwmax_cof'    , type=int, default=1000)
    parser.add_argument('--timeout'      , type=int, default=30)
    parser.add_argument('--forward'      , action='store_true')

    # Program options
    parser.add_argument(
        '--log',
        metavar='ARG',
        type=str,
        choices=[
            'debug', 'info', 'warning', 'error', 'critical',
            'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        ],
        default='def_info',
        help='Adds a console logger for the specified level (default: error)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(__version__),
        help='show the version number and exit'
    )

    return parser

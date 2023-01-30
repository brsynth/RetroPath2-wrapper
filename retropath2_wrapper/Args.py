"""
Created on May 4 2020

@author: Joan Hérisson

"""
from os import path as os_path
from argparse import ArgumentParser
from retropath2_wrapper._version import __version__


DEFAULT_MSC_TIMEOUT = 10  # minutes
DEFAULT_KNIME_VERSION = "4.6.4"
DEFAULT_RP2_VERSION = 'r20220104'
KNIME_ZENODO = {"4.6.4": "7515771", "4.7.0": "7564938"} # Map to Zenodo ID
DEFAULT_ZENODO_VERSION = "NA"
RETCODES = {
    'OK': 0,
    'NoError': 0,
    # Warnings
    'SrcInSink': 10,
    'NoSolution': 11,
    # Errors
    'FileNotFound': 1,
    'OSError': 2,
    'InChI': 3
}
__PACKAGE_FOLDER = os_path.dirname(
    os_path.realpath(__file__)
)
DEFAULT_KNIME_FOLDER = __PACKAGE_FOLDER


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
        '--kinstall',
        type=str,
        default=DEFAULT_KNIME_FOLDER,
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
        '--kzenodo',
        choices=[DEFAULT_ZENODO_VERSION] + list(KNIME_ZENODO.keys()),
        default=DEFAULT_ZENODO_VERSION,
        help='install Knime and its dependencies from Zenodo.'
    )

    parser.add_argument(
        '--rp2_version',
        type=str,
        default=DEFAULT_RP2_VERSION,
        choices=['v9', 'r20210127', 'r20220104', "r20220224"],
        help=f'version of RetroPath2.0 workflow (default: {DEFAULT_RP2_VERSION}).'
    )

    # RetroPath2.0 workflow options
    parser.add_argument('--max_steps'    , type=int, default=3)
    parser.add_argument('--topx'         , type=int, default=100)
    parser.add_argument('--dmin'         , type=int, default=0)
    parser.add_argument('--dmax'         , type=int, default=1000)
    parser.add_argument('--mwmax_source' , type=int, default=1000)
    parser.add_argument(
        '--msc_timeout',
        type=int,
        default=DEFAULT_MSC_TIMEOUT,
        help=f'Defines the time after which the RDKit MCS Aggregation method will stop searching for best match (default: {DEFAULT_MSC_TIMEOUT}).'
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

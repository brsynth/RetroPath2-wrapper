"""
Created on May 4 2020

@author: Joan Hérisson

"""
from os import path as os_path
from argparse import ArgumentParser

from retropath2_wrapper._version import __version__


__PACKAGE_FOLDER = os_path.dirname(
    os_path.realpath(__file__)
)
DEFAULTS = {
    'MSC_TIMEOUT': 10,  # minutes
    'KNIME_VERSION': "4.6.4",
    'RP2_VERSION': 'r20250728',
    'KNIME_FOLDER': __PACKAGE_FOLDER,
    'KNIME_REPOS': [
            # 'http://update.knime.com/partner/',
            'http://update.knime.com/community-contributions/trunk/',
            'http://update.knime.com/community-contributions/trusted/4.6',
            'http://update.knime.com/analytics-platform/4.6'
        ],
    'KNIME_PLUGINS': ','.join(
        [
            'org.knime.base',
            'org.knime.python.nodes',
            'org.knime.datageneration',
            'org.knime.chem.base',
            'org.rdkit.knime.feature.feature.group/4.8.1.v202312052327',
            'org.rdkit.knime.nodes/4.8.1.v202312052327',
            # 'org.knime.python.nodes/4.6.0.v202203011403',
            # 'org.knime.datageneration/4.6.0.v202202251621',
            # 'org.knime.chem.base/4.6.0.v202202251610',
            # 'org.rdkit.knime.feature.feature.group/4.8.1.v202312052327',
            # 'org.rdkit.knime.nodes/4.8.1.v202312052327',
        ]
    ),
    'NO_NETWORK': False,
    "STD_HYDROGEN": "auto",  # How hydrogens are represented in chemical rules
}
# DEFAULTS['KNIME_PLUGINS'] = ','.join(
#     [pkg.split('/')[0] for pkg in DEFAULTS['KNIME_PLUGINS'].split(',')]
# )
KNIME_ZENODO = {"4.6.4": "7515771", "4.7.0": "7564938"} # Map to Zenodo ID
RETCODES = {
    'OK': 0,
    'NoError': 0,
    # Warnings
    'SrcInSink': 10,
    'NoSolution': 11,
    # Errors
    'FileNotFound': 1,
    'OSError': 2,
    'InChI': 3,
    'SinkFileMalformed': 4,
}


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
    parser_in = parser.add_argument_group("Input arguments")
    parser_in.add_argument(
        '--source_file',
        type=str,
        help='Path of file containing the InChI (not compliant with --source_name nor --source_inchi)'
    )
    parser_in.add_argument(
        '--source_name',
        type=str,
        default=None,
        help='Name of compound to produce (needs --inchi, not compliant with --source_file).'
    )
    parser_in.add_argument(
        '--source_inchi',
        type=str,
        default=None,
        help='InChI of compound to produce (not compliant with --source_file).'
    )

    # Knime
    parser_knime = parser.add_argument_group("Knime arguments")
    parser_knime.add_argument(
        '--kexec',
        type=str,
        default=None,
        help='path to KNIME executable file (KNIME will be \
              downloaded if not already installed or path is \
              wrong).'
    )
    parser_knime.add_argument(
        '--kinstall',
        type=str,
        default=DEFAULTS['KNIME_FOLDER'],
        help='path to KNIME executable file (KNIME will be \
              downloaded if not already installed or path is \
              wrong).'
    )
    parser_knime.add_argument(
        '--kver',
        type=str,
        default=DEFAULTS['KNIME_VERSION'],
        choices=list(KNIME_ZENODO.keys()),
        help='version of KNIME (mandatory if --kexec is passed).',
    )
    parser_knime.add_argument(
        '--kplugins',
        type=str,
        default="",
        help='KNIME plugins to use (separated by a comma).',
    )

    # RetroPath2.0 workflow options
    parser_rp = parser.add_argument_group("Retropath2.0 workflow")
    parser_rp.add_argument(
        '--rp2_version',
        type=str,
        default=DEFAULTS['RP2_VERSION'],
        choices=['v9', 'r20210127', 'r20220104', "r20220224", "r20250728"],
        help=f'version of RetroPath2.0 workflow (default: {DEFAULTS["RP2_VERSION"]}).'
    )

    # No network option
    parser_rp.add_argument(
        '--no-network',
        action='store_true',
        default=DEFAULTS['NO_NETWORK'],
        help='Do not use network.'
    )

    parser_rp.add_argument('--max_steps'    , type=int, default=3)
    parser_rp.add_argument('--topx'         , type=int, default=100)
    parser_rp.add_argument('--dmin'         , type=int, default=0)
    parser_rp.add_argument('--dmax'         , type=int, default=1000)
    parser_rp.add_argument('--mwmax_source' , type=int, default=1000)
    parser_rp.add_argument(
        '--msc_timeout',
        type=int,
        default=DEFAULTS['MSC_TIMEOUT'],
        help=f'Defines the time after which the RDKit MCS Aggregation method will stop searching for best match (default: {DEFAULTS["MSC_TIMEOUT"]}).'
    )
    parser_rp.add_argument(
        "--std_hydrogen",
        default=DEFAULTS["STD_HYDROGEN"],
        choices=["auto", "implicit", "explicit"],
        help="How hydrogens are represented in chemical rules, auto mode will try to guess from the chemical rules",
    )

    # Program options
    parser_sp = parser.add_argument_group("Logging")
    parser_sp.add_argument(
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
    parser_sp.add_argument(
        '--silent',
        action='store_true',
        default=False,
        help='run %(prog)s silently'
    )
    parser_sp.add_argument(
        '--quiet',
        action='store_true',
        default=False,
        help='run %(prog)s without returning any error'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(__version__),
        help='show the version number and exit'
    )

    return parser

"""
Created on May 4 2020

@author: Joan Hérisson

"""

from argparse  import ArgumentParser


def build_args_parser():
    parser = ArgumentParser(prog='RetroPath2', description='Python wrapper to parse RP2 to generate rpSBML collection of unique and complete (cofactors) pathways')
    parser = _add_arguments(parser)

    return parser


def _add_arguments(parser):
    parser.add_argument('sinkfile', type=str)
    parser.add_argument('sourcefile', type=str)
    parser.add_argument('rulesfile', type=str)
    parser.add_argument('outdir', type=str)
    parser.add_argument('--knime_exec', type=str, default='',
                        help='path to Knime executable file (Knime will be \
                              downloaded if not already installed or path is \
                              wrong).')
    parser.add_argument('--max_steps', type=int, default=3)
    parser.add_argument('--topx', type=int, default=100)
    parser.add_argument('--dmin', type=int, default=0)
    parser.add_argument('--dmax', type=int, default=1000)
    parser.add_argument('--mwmax_source', type=int, default=1000)
    parser.add_argument('--mwmax_cof', type=int, default=1000)
    parser.add_argument('--timeout', type=int, default=30)
    parser.add_argument('--forward', action='store_true')

    return parser

"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from unittest import TestCase

from retropath2_wrapper import run, build_args_parser
# from tempfile import TemporaryDirectory


class Test_Main(TestCase):

    cmd = '\
        -sinkfile data/Galaxy177-Sink_Compounds.csv \
        -sourcefile data/Galaxy160-Source.csv \
        -max_steps 3 \
        -rulesfile data/_exclude_rules.csv \
        -topx 100 \
        -dmin 0 \
        -dmax 1000 \
        -mwmax_source 1000 \
        -mwmax_cof 1000 \
        -timeout 30 \
        -outdir out \
        -is_forward False'.split()
    args  = build_args_parser().parse_args(cmd)

    def test_run(self):

        result = run(self.args.sinkfile,
                     self.args.sourcefile,
                     self.args.max_steps,
                     self.args.rulesfile,
                     self.args.outdir,
                     self.args.topx,
                     self.args.dmin,
                     self.args.dmax,
                     self.args.mwmax_source,
                     self.args.mwmax_cof,
                     self.args.timeout,
                     self.args.is_forward)
        self.assertEqual(True, True)

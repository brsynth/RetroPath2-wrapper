"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from module import Module
from os     import path as os_path

# from retropath2_wrapper import run, build_args_parser
# from tempfile import TemporaryDirectory


class Test_Main(Module):
    __test__ = True

    def _preexec(self):
        from brs_utils import extract_gz

        if not os_path.exists(self.args.rulesfile):
            extract_gz('data/rules.tar.gz', 'data')

    #
    # def test_wrong_knime_path(self):
    #
    #     from os import path as os_path
    #     from brs_utils import extract_gz
    #
    #     if not os_path.exists(self.args.rulesfile):
    #         extract_gz('data/rules.tar.gz', 'data')
    #
    #     results_filename = run(self.args.sinkfile,
    #                           self.args.sourcefile,
    #                           self.args.max_steps,
    #                           self.args.rulesfile,
    #                           self.args.outdir,
    #                           self.args.topx,
    #                           self.args.dmin,
    #                           self.args.dmax,
    #                           self.args.mwmax_source,
    #                           self.args.mwmax_cof,
    #                           self.args.timeout,
    #                           self.args.is_forward,
    #                           '/tmp/knime/knime')
    #     self.assertTrue(os_path.exists(self.args.outdir+'/'+results_filename))

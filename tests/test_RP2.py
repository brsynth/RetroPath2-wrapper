"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

# from _main     import Main
from unittest  import TestCase
from tempfile  import TemporaryDirectory, gettempdir
from os        import path      as os_path
from filecmp   import cmp
# from os        import stat      as os_stat
# from argparse  import Namespace as argparse_Namespace
from brs_utils          import extract_tar_gz
from retropath2_wrapper import retropath2



class Test_RP2(TestCase):

    data_path  = 'data'
    sinkfile   = os_path.join(data_path,    'Galaxy177-Sink_Compounds.csv')
    sourcefile = os_path.join(data_path,    'Galaxy160-Source.csv')
    rulesfile  = os_path.join(gettempdir(), 'rules.csv')
    ref_file   = os_path.join(data_path,    'results.csv')
    outdir = TemporaryDirectory().name
    outdir = '/tmp/joan'

    def _preexec(self):
        from brs_utils import extract_gz

        if not os_path.exists(self.rulesfile):
            extract_tar_gz(os_path.join(self.data_path, 'rules.tar.gz'), gettempdir())


    def test_light(self):

        outFile = retropath2(self.sinkfile,
                             self.sourcefile,
                             self.rulesfile,
                             self.outdir,
                             dmin=2, dmax=2)

        print(outFile)

        self.assertTrue(cmp(outFile, self.ref_file))


    # files = [
    # (os_path.join(tempdir, 'results.csv'), 'a8a5522a3db9e53f2a44c95c81ba78562e30e0450467050730b0b4cb3a551101')
    # ]

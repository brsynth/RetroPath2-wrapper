"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from unittest  import TestCase
from tempfile  import TemporaryDirectory, gettempdir
from os        import path      as os_path
from filecmp   import cmp
from brs_utils          import extract_tar_gz
from retropath2_wrapper import retropath2



class Test_RP2(TestCase):

    data_path  = 'data'
    sinkfile   = os_path.join(data_path,    'sink.csv')
    sourcefile = os_path.join(data_path,    'source.csv')
    rulesfile  = os_path.join(gettempdir(), 'rules.csv')
    ref_file   = os_path.join(data_path,    'results.csv')
    outdir = TemporaryDirectory().name
    outdir = '/tmp/joan'

    def setUp(self):
        if not os_path.exists(self.rulesfile):
            extract_tar_gz(os_path.join(self.data_path, 'rules.tar.gz'), gettempdir())


    def test_light(self):

        outFile = retropath2(self.sinkfile,
                             self.sourcefile,
                             self.rulesfile,
                             self.outdir,
                             dmin=16)

        print(outFile)

        self.assertTrue(cmp(outFile, self.ref_file))

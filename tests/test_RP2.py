"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from unittest  import TestCase
from tempfile  import TemporaryDirectory, gettempdir
from os        import path      as os_path
from filecmp   import cmp
from brs_utils          import extract_gz
from retropath2_wrapper import retropath2



class Test_RP2(TestCase):

    data_path  = 'data'
    sinkfile   = os_path.join(data_path, 'sink')
    sourcefile = os_path.join(data_path, 'source')
    rulesfile  = os_path.join(data_path, 'rules')
    ref_file   = os_path.join(data_path, 'scope.csv')
    outdir     = TemporaryDirectory().name
    ext = '.csv'


    def test_light(self):

        outFile = retropath2(self.sinkfile+self.ext,
                             self.sourcefile+self.ext,
                             extract_gz(self.rulesfile+self.ext+'.gz',
                                        gettempdir()),
                             self.outdir,
                             dmin=16)

        self.assertTrue(cmp(outFile, self.ref_file))


    def test_GZ(self):

        outFile = retropath2(self.sinkfile+self.ext,
                             self.sourcefile+self.ext,
                             self.rulesfile+self.ext+'.gz',
                             self.outdir,
                             dmin=16)

        self.assertTrue(cmp(outFile, self.ref_file))


    def test_woCSV(self):

        ext = '.dat'
        outFile = retropath2(self.sinkfile+ext,
                             self.sourcefile+ext,
                             self.rulesfile+ext,
                             self.outdir,
                             dmin=16)

        self.assertTrue(cmp(outFile, self.ref_file))

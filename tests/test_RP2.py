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
        r_code, result = retropath2(self.sinkfile+self.ext,
                                    self.sourcefile+self.ext,
                                    extract_gz(self.rulesfile+self.ext+'.gz',
                                               gettempdir()),
                                    self.outdir,
                                    dmin=16)
        self.assertTrue(cmp(result, self.ref_file))


    def test_GZ(self):
        r_code, result = retropath2(self.sinkfile+self.ext,
                                    self.sourcefile+self.ext,
                                    self.rulesfile+self.ext+'.gz',
                                    self.outdir,
                                    dmin=16)
        self.assertTrue(cmp(result, self.ref_file))


    def test_woCSV(self):
        ext = '.dat'
        r_code, result = retropath2(self.sinkfile+ext,
                                    self.sourcefile+ext,
                                    self.rulesfile+ext,
                                    self.outdir,
                                    dmin=16)
        self.assertTrue(cmp(result, self.ref_file))

    # def test_lycopene(self):
    #     data_path  = 'data/lycopene'
    #     sinkfile   = os_path.join(data_path, 'in', 'sink')
    #     sourcefile = os_path.join(data_path, 'in', 'source')
    #     rulesfile  = os_path.join(data_path, 'in', 'rules_d12')
    #     ref_file   = os_path.join(data_path, 'out', 'target_scope.csv')
    #     ext = '.dat'
    #     r_code, result = retropath2(self.sinkfile+ext,
    #                                 self.sourcefile+ext,
    #                                 self.rulesfile+ext,
    #                                 self.outdir,
    #                                 dmin=16)
    #     self.assertTrue(cmp(result, self.ref_file))

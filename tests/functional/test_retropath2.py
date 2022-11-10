"""
Created on Jul 15 2020

@author: Joan Hérisson
"""
import filecmp
import os
import tempfile

from retropath2_wrapper.__main__ import create_logger
from retropath2_wrapper.Args import RETCODES
from retropath2_wrapper.RetroPath2 import retropath2
from tests.main_test import Main_test


class TestRetropath2(Main_test):
    def setUp(self):
        self.logger = create_logger(__name__, 'DEBUG')

    def test_src_in_sink(self):
         with tempfile.TemporaryDirectory() as tmpdir:
             r_code, result = retropath2(
                 sink_file=self.lycopene_sink_csv,
                 source_file=self.source_mnxm790_csv,
                 rules_file=self.rules_csv,
                 outdir=tmpdir,
                 logger=self.logger,
             )
             self.assertEqual(r_code, RETCODES['SrcInSink'])

    def test_lycopene(self):
        with tempfile.TemporaryDirectory() as tempd:
            r_code, result = retropath2(
                sink_file=self.lycopene_sink_csv,
                source_file=self.lycopene_source_csv,
                rules_file=self.rulesd12_csv,
                outdir=tempd,
            )
            self.assertTrue(
                filecmp.cmp(os.path.join(result['outdir'], result['results']), self.lycopene_r20220104_results_csv)
            )

    """
    # Set attributes
    maxDiff = None
    csv        = '.csv'
    gz         = '.gz'
    data_path  = os_path.join(here, 'data')
    iml1515_sinkfile   = os_path.join(data_path, 'lycopene', 'in', 'sink') + csv
    lycopene_sourcefile = os_path.join(data_path, 'lycopene', 'in', 'source') + csv
    alanine_sourcefile = os_path.join(data_path, 'alanine', 'in', 'source') + csv
    rulesfile  = os_path.join(data_path, 'rules') + csv + gz
    rulesfile_d12 = os_path.join(data_path, 'rules_d12') + csv + gz
    ref_file   = os_path.join(data_path, 'lycopene', 'out', 'r20220104', 'results') + csv

    # def test_light(self):
    #     r_code, result = retropath2(
    #         self.sinkfile+self.csv,
    #         self.sourcefile+self.csv,
    #         extract_gz(
    #             self.rulesfile,
    #             gettempdir()),
    #         self.outdir,
    #         dmin=16
    #         )
    #     self.assertTrue(cmp(result, self.ref_file+self.csv))


    # def test_GZ(self):
    #     r_code, result = retropath2(
    #         self.sinkfile+self.csv,
    #         self.sourcefile+self.csv,
    #         self.rulesfile,
    #         self.outdir,
    #         dmin=16,
    #         logger=self.logger
    #         )
    #     self.assertTrue(cmp(result, self.ref_file+self.csv))


    # def test_woCSV(self):
    #     if not os_path.exists(self.outdir):
    #         os_mkdir(self.outdir)
    #     rulesfile = gunzip_to_csv(
    #         self.rulesfile_d12,
    #         self.outdir
    #         )
    #     ext = '.dat'
    #     r_code, result = retropath2(
    #         self.sinkfile + ext,
    #         self.sourcefile + ext,
    #         rulesfile,
    #         self.outdir,
    #         dmin=12
    #         )
    #     self.assertTrue(cmp(result, self.ref_file+'_d12'+self.csv))
    """

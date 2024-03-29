"""
Created on Jul 15 2020

@author: Joan Hérisson
"""
import filecmp
import os
import shutil
import sys
import tempfile

import pytest
from retropath2_wrapper.__main__ import create_logger
from retropath2_wrapper.Args import RETCODES
from retropath2_wrapper.RetroPath2 import retropath2


FUNCTIONAL = "RP2_FUNCTIONAL" not in os.environ

@pytest.fixture(scope="function")
def logger():
    return create_logger(__name__, 'DEBUG')

class TestRetropath2:
    @pytest.mark.skipif(FUNCTIONAL, reason="Functional test")
    def test_src_in_sink(self, lycopene_sink_csv, source_mnxm790_csv, rules_csv, logger):
        tempdir = tempfile.mkdtemp()

        r_code, result = retropath2(
            sink_file=lycopene_sink_csv,
            source_file=source_mnxm790_csv,
            rules_file=rules_csv,
            outdir=tempdir,
            logger=logger,
        )
        assert r_code == RETCODES['SrcInSink']

        shutil.rmtree(tempdir, ignore_errors=True)

    @pytest.mark.skipif(FUNCTIONAL, reason="Functional test")
    def test_lycopene(self, lycopene_sink_csv, lycopene_source_csv, rulesd12_7325_csv, lycopene_r20220104_results_7325_csv, logger):
        tempdir = tempfile.mkdtemp()

        r_code, result = retropath2(
            sink_file=lycopene_sink_csv,
            source_file=lycopene_source_csv,
            rules_file=rulesd12_7325_csv,
            kinstall=tempdir,
            outdir=tempdir,
            msc_timeout=10,
            logger=logger,
        )
        # Specific test for windows due to Github Runner memory consumption.
        # Only check first lines.
        if sys.platform == 'win32':
            with open(result['outdir'] + "/" + result['results']) as fid:
                result_lines = fid.read().splitlines()
            with open(self.lycopene_r20220104_results_7325_csv) as fid:
                theorical_lines = fid.read().splitlines()
            nb_lines = len(result_lines)

            assert nb_lines > 5
            assert result_lines == theorical_lines[:nb_lines]
        else:
            assert filecmp.cmp(result['outdir'] + "/" + result['results'], lycopene_r20220104_results_7325_csv)
        shutil.rmtree(tempdir, ignore_errors=True)

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

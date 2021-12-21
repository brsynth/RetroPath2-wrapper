"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from unittest  import TestCase
from tempfile  import TemporaryDirectory, gettempdir
from os        import path      as os_path
from os        import mkdir     as os_mkdir
from filecmp   import cmp
from brs_utils import extract_gz
from pathlib   import Path
from shutil    import copyfile
from retropath2_wrapper.RetroPath2 import (
    retropath2,
    __KNIME_VER__,
    __RETROPATH2_KWF__,
    set_vars,
    gunzip_to_csv,
    check_inchi_from_file
)
from retropath2_wrapper.__main__ import create_logger


class Test_RP2(TestCase):

    # Set attributes
    csv        = '.csv'
    gz         = '.gz'
    data_path  = 'data'
    sinkfile   = os_path.join(data_path, 'sink')
    sourcefile = os_path.join(data_path, 'source')
    rulesfile  = os_path.join(data_path, 'rules') + csv + gz
    rulesfile_d12 = os_path.join(data_path, 'rules_d12') + csv + gz
    ref_file   = os_path.join(data_path, 'scope')
    outdir     = TemporaryDirectory().name
    logger     = create_logger(__name__, 'DEBUG')


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


    def test_set_vars_None(self):
        # Process the function to test
        kvars = set_vars(
            kexec        = None,
            kver         = None,
            kpkg_install = True
            )

        # Prepare expectd data
        from retropath2_wrapper import __path__ as rp2_path
        rp2_path = rp2_path[0]
        kinstall = rp2_path
        kver = __KNIME_VER__
        kpath    = os_path.join(kinstall, 'knime_')+kver
        kexec    = os_path.join(kpath, 'knime')
        workflow = os_path.join(
            rp2_path,
            'workflows',
            __RETROPATH2_KWF__
            )
        kvars_expected = {
            'kexec'         : kexec,
            'kexec_install' : not os_path.exists(kpath),
            'kver'          : kver,
            'kpath'         : kpath,
            'kinstall'      : kinstall,
            'kpkg_install'  : True
        }
        self.assertDictEqual(kvars, kvars_expected)


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


class TestMethods:

    inchi_test_file = Path(__file__).parent / 'data' / 'inchi_test_cases.csv'

    def test_check_inchi_from_file(self, tmpdir):
        with open(self.inchi_test_file) as ifh:
            inchis = ifh.read().splitlines() 
        for inchi in inchis:
            tmp_file = Path(tmpdir) / 'source.csv'
            with open(tmp_file, 'w') as ofh:
                ofh.write('"Name","InChI"\n')
                ofh.write(f'"target","{inchi}"')
            try:
                assert check_inchi_from_file(tmp_file) != ''
            except AssertionError as e:
                raise e
"""
Created on Jul 15 2020

@author: Joan Hérisson
"""
import os
import tempfile

from retropath2_wrapper.Args import RETCODES
from retropath2_wrapper.RetroPath2 import check_inchi_from_file, check_input
from tests.main_test import Main_test


class TestHelpers(Main_test):
    def test_check_input(self):
        ret, inchi = check_input(source_file=self.source_weird_csv, sink_file=self.lycopene_sink_csv)
        self.assertEqual(ret, RETCODES["InChI"])

        ret, inchi = check_input(source_file=self.lycopene_source_csv, sink_file=self.johndoe)
        self.assertEqual(ret, RETCODES["FileNotFound"])

        ret, inchi = check_input(source_file=self.johndoe, sink_file=self.lycopene_sink_csv)
        self.assertEqual(ret, RETCODES["InChI"])

        ret, inchi = check_input(source_file=self.source_mnxm790_csv, sink_file=self.lycopene_sink_csv)
        self.assertEqual(ret, RETCODES["SrcInSink"])

        ret, inchi = check_input(source_file=self.lycopene_source_csv, sink_file=self.lycopene_sink_csv)
        self.assertEqual(ret, RETCODES["OK"])

    def test_check_inchi_from_file(self):
        with open(self.inchi_csv) as ifh:
            inchis = ifh.read().splitlines()
        for inchi in inchis:
            fod = tempfile.NamedTemporaryFile(delete=False)
            fod.write(bytes('"Name","InChI"\n', "utf8"))
            fod.write(bytes('"target","%s"' % (inchi,), "utf8"))
            fod.close()
            self.assertNotEqual(check_inchi_from_file(fod.name), "")
            os.remove(fod.name)

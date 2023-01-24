"""
Created on Jul 15 2020

@author: Joan Hérisson
"""
import os
import tempfile

from retropath2_wrapper.Args import RETCODES
from retropath2_wrapper.RetroPath2 import check_inchi_from_file, check_input


class TestHelpers:
    def test_check_input_inchi(self, source_weird_csv, lycopene_sink_csv, johndoe):
        ret, inchi = check_input(source_file=source_weird_csv, sink_file=lycopene_sink_csv)
        assert ret == RETCODES["InChI"]
        ret, inchi = check_input(source_file=johndoe, sink_file=lycopene_sink_csv)
        assert ret ==  RETCODES["InChI"]

    def test_check_input_filenotfound(self, lycopene_source_csv, johndoe):
        ret, inchi = check_input(source_file=lycopene_source_csv, sink_file=johndoe)
        assert ret == RETCODES["FileNotFound"]

    def test_check_input_srcinsink(self, lycopene_sink_csv, source_mnxm790_csv):
        ret, inchi = check_input(source_file=source_mnxm790_csv, sink_file=lycopene_sink_csv)
        assert ret == RETCODES["SrcInSink"]

    def test_check_input_srcinsink(self, lycopene_sink_csv, lycopene_source_csv):
        ret, inchi = check_input(source_file=lycopene_source_csv, sink_file=lycopene_sink_csv)
        assert ret == RETCODES["OK"]

    def test_check_inchi_from_file(self, inchi_csv):
        with open(inchi_csv) as ifh:
            inchis = ifh.read().splitlines()
        for inchi in inchis:
            fod = tempfile.NamedTemporaryFile(delete=False)
            fod.write(bytes('"Name","InChI"\n', "utf8"))
            fod.write(bytes('"target","%s"' % (inchi,), "utf8"))
            fod.close()
            assert check_inchi_from_file(fod.name) != ""
            os.remove(fod.name)

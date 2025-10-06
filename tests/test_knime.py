import os
import pathlib
import shutil
import subprocess
import tempfile

import pytest
from retropath2_wrapper.Args import RETCODES
from retropath2_wrapper.knime import Knime


FUNCTIONAL = "RP2_FUNCTIONAL" not in os.environ

class TestKnime:
    @classmethod
    def filter_exec(cls, path: str):
        kexec = None
        args = [
            "-application",
            "org.eclipse.equinox.p2.director",
            "-nosplash",
            "-consolelog",
            "-help",
        ]
        for x in pathlib.Path(path).glob(os.path.join("**", "knime*")):
            if x.is_file() is False:
                continue
            try:
                ret = subprocess.run([str(x.absolute())] + args)
                if ret.returncode == 0:
                    kexec = x
                    break
            except:
                pass
        return kexec

    def test_standardize_path(self):
        path = os.getcwd()
        spath = Knime.standardize_path(path=path)
        assert "\\" not in spath

    @pytest.mark.skipif(FUNCTIONAL, reason="Functional test")
    def test_install_knime_from_zenodo(self):
        tempdir = tempfile.mkdtemp()
        knime = Knime(workflow="", kinstall=tempdir)
        knime.install(kver=list(Knime.ZENODO.keys())[0])
        kexec = TestKnime.filter_exec(path=tempdir)
        assert kexec is not None
        shutil.rmtree(tempdir, ignore_errors=True)

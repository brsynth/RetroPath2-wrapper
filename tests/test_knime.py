import os
import pathlib
import shutil
import subprocess
import tempfile

import pytest
from retropath2_wrapper.Args import DEFAULT_KNIME_VERSION, DEFAULT_ZENODO_VERSION, KNIME_ZENODO, RETCODES
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
    def test_install_knime_from_knime(self):
        tempdir = tempfile.mkdtemp()

        knime = Knime(workflow="", kinstall=tempdir)
        knime.install_exec()
        kexec = TestKnime.filter_exec(path=tempdir)
        assert kexec is not None
        # Failed could be araise due to missing dependecy
        try:
            ret = knime.install_pkgs()
            assert ret == RETCODES['OK']
        except Exception:
            pass
        shutil.rmtree(tempdir, ignore_errors=True)

    @pytest.mark.skipif(FUNCTIONAL, reason="Functional test")
    def test_install_knime_from_zenodo(self):
        tempdir = tempfile.mkdtemp()

        knime = Knime(workflow="", kinstall=tempdir, kzenodo_ver=list(KNIME_ZENODO.keys())[0])
        knime.install_exec()
        kexec = TestKnime.filter_exec(path=tempdir)
        assert kexec is not None
        ret = knime.install_pkgs()
        assert ret == RETCODES['OK']
        shutil.rmtree(tempdir, ignore_errors=True)

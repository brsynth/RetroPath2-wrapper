import os
import glob
import shutil
import subprocess
import tempfile
import unittest


from retropath2_wrapper.Args import DEFAULT_KNIME_VERSION
from retropath2_wrapper.RetroPath2 import install_knime, install_knime_pkgs


class TestKnime(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        try:
            os.remove(self.tempdir)
        except:
            pass

    def test_install_knime(self):
        install_knime(
            kinstall=self.tempdir,
            kver=DEFAULT_KNIME_VERSION,
        )
        # Filter execs
        kexec = None
        args = [
            "-application",
            "org.eclipse.equinox.p2.director",
            "-nosplash",
            "-consolelog",
            "-help",
        ]
        for x in glob.glob(os.path.join(self.tempdir, "**", "knime"), recursive=True):
            ret = subprocess.run([x] + args)
            if ret.returncode == 0:
                kexec = x
                break
        self.assertIsNot(kexec, None)
        return kexec

    def test_install_knime_pkgs(self):
        kexec = self.test_install_knime()
        install_knime(
            kinstall=self.tempdir,
            kver=DEFAULT_KNIME_VERSION,
        )
        res = install_knime_pkgs(
            kpkg_install=self.tempdir,
            kver=DEFAULT_KNIME_VERSION,
            kexec=kexec,
        )
        self.assertEqual(res, 0)

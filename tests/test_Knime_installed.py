"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from module import Module
from os     import path as os_path

# from retropath2_wrapper import run, build_args_parser
# from tempfile import TemporaryDirectory


class Test_Main(Module):
    __test__ = True

    def _preexec(self):
        from subprocess import call, STDOUT, TimeoutExpired# nosec
        from brs_utils import download_and_extract_gz, extract_gz

        if not os_path.exists(self.args.rulesfile):
            extract_gz('data/rules.tar.gz', 'data')

        download_and_extract_gz(self.KURL, '/tmp')
        knime_add_pkgs = self.KEXEC \
            + ' -application org.eclipse.equinox.p2.director' \
            + ' -nosplash -consolelog' \
            + ' -r http://update.knime.org/community-contributions/trunk,' \
                + 'http://update.knime.com/analytics-platform/3.6,' \
                + 'http://update.knime.com/community-contributions/trusted/3.6' \
            + ' -i org.knime.features.chem.types.feature.group,' \
                + 'org.knime.features.datageneration.feature.group,' \
                + 'jp.co.infocom.cheminfo.marvin.feature.feature.group,' \
                + 'org.knime.features.python.feature.group,' \
                + 'org.rdkit.knime.feature.feature.group' \
            + ' -bundlepool '+self.KPATH+' -d '+self.KPATH
        call(knime_add_pkgs.split(), stderr=STDOUT, shell=False)# nosec

        self.args.kexec = self.KEXEC

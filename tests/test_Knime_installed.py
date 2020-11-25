"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from module    import Module
from os        import path as os_path
from brs_utils import extract_tar_gz, download_and_extract_tar_gz
from tempfile  import gettempdir
from subprocess import call, STDOUT, TimeoutExpired# nosec


class Test_Main(Module):
    __test__ = True

    KVER         = '3.6.2'
    # KVER         = '3.7.1'
    KURL         = 'http://download.knime.org/analytics-platform/linux/knime_'+KVER+'.linux.gtk.x86_64.tar.gz'
    KINSTALL     = gettempdir()
    KPATH        = os_path.join(KINSTALL, 'knime_')+KVER
    KEXEC        = os_path.join(KPATH, 'knime')

    def _preexec(self):
        if not os_path.exists(self.args.rulesfile):
            extract_tar_gz(os_path.join('data', 'rules.tar.gz'), gettempdir())

        if not os_path.exists(KEXEC):
            download_and_extract_tar_gz(self.KURL, gettempdir())
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

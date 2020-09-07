"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from unittest  import TestCase
from os import path as os_path

from retropath2_wrapper import run, build_args_parser
# from tempfile import TemporaryDirectory


class Test_Main(TestCase):

    cmd = '\
        -sinkfile data/Galaxy177-Sink_Compounds.csv \
        -sourcefile data/Galaxy160-Source.csv \
        -max_steps 3 \
        -rulesfile data/rules.csv \
        -topx 100 \
        -dmin 0 \
        -dmax 1000 \
        -mwmax_source 1000 \
        -mwmax_cof 1000 \
        -timeout 30 \
        -outdir out \
        -is_forward False'.split()
    args  = build_args_parser().parse_args(cmd)

    def test_from_scratch(self):

        from brs_utils import extract_gz

        if not os_path.exists(self.args.rulesfile):
            extract_gz('data/rules.tar.gz', 'data')

        results_filename = run(self.args.sinkfile,
                               self.args.sourcefile,
                               self.args.max_steps,
                               self.args.rulesfile,
                               self.args.outdir,
                               self.args.topx,
                               self.args.dmin,
                               self.args.dmax,
                               self.args.mwmax_source,
                               self.args.mwmax_cof,
                               self.args.timeout,
                               self.args.is_forward)
        self.assertTrue(os_path.exists(self.args.outdir+'/'+results_filename))


    def test_with_knime_installed_with_right_path(self):

        from subprocess import call, STDOUT, TimeoutExpired# nosec
        from brs_utils import download_and_extract_gz, extract_gz

        if not os_path.exists(self.args.rulesfile):
            extract_gz('data/rules.tar.gz', 'data')

        KVER         = '3.6.2'
        KURL         = 'http://download.knime.org/analytics-platform/linux/knime_'+KVER+'.linux.gtk.x86_64.tar.gz'
        KINSTALL     = '/tmp'
        KPATH        = KINSTALL+'/knime_'+KVER
        KEXEC        = KPATH+'/knime'

        download_and_extract_gz(KURL, '/tmp')
        knime_add_pkgs = KEXEC \
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
            + ' -bundlepool '+KPATH+' -d '+KPATH
        call(knime_add_pkgs.split(), stderr=STDOUT, shell=False)# nosec

        results_filename =  = run(self.args.sinkfile,
                                  self.args.sourcefile,
                                  self.args.max_steps,
                                  self.args.rulesfile,
                                  self.args.outdir,
                                  self.args.topx,
                                  self.args.dmin,
                                  self.args.dmax,
                                  self.args.mwmax_source,
                                  self.args.mwmax_cof,
                                  self.args.timeout,
                                  self.args.is_forward,
                                  KEXEC)
        self.assertTrue(os_path.exists(self.args.outdir+'/'+results_filename))


    def test_wrong_knime_path(self):

        from os import path as os_path
        from brs_utils import extract_gz

        if not os_path.exists(self.args.rulesfile):
            extract_gz('data/rules.tar.gz', 'data')
    
        results_filename = run(self.args.sinkfile,
                              self.args.sourcefile,
                              self.args.max_steps,
                              self.args.rulesfile,
                              self.args.outdir,
                              self.args.topx,
                              self.args.dmin,
                              self.args.dmax,
                              self.args.mwmax_source,
                              self.args.mwmax_cof,
                              self.args.timeout,
                              self.args.is_forward,
                              '/tmp/knime/knime')
        self.assertTrue(os_path.exists(self.args.outdir+'/'+results_filename))

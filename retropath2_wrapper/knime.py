import os
import requests
import shutil
import sys
import tempfile
import urllib.parse
from getpass import getuser
from logging import (
    getLogger,
    Logger,
    StreamHandler,
)
from typing import Any, Dict, Optional
from colored import attr

from brs_utils  import (
    download_and_extract_tar_gz,
    download,
    download_and_unzip,
    chown_r,
    subprocess_call
)
from retropath2_wrapper.Args import (
    DEFAULT_KNIME_FOLDER,
    DEFAULT_KNIME_VERSION,
    KNIME_ZENODO,
    RETCODES,
)
from retropath2_wrapper.preference import Preference


class Knime(object):
    """Knime is useful to install executable, install packages or commandline.

    Attributes
    ----------
    workflow: str
        path of the Knime workflow
    kver: str
        knime version to download, install or use
    kexec: str
        path of Knime executable
    kexec_install: bool
        install or not Knime executable
    kinstall: str
        path install knime
    kurl: str
        an url to download Knime (from Knime or Zenodo)
    kzenodo_id: str
        Zenodo repository ID

    Methods
    -------
    zenodo_show_repo(self) -> Dict[str, Any]
        Show Zenodo repository informations.

    @classmethod
    def standardize_path(cls, path: str) -> str
        Path are given with double backslashes on windows.

    install_exec(self, logger: Logger = getLogger(__name__)) -> None
        Install Knime executable

    install_pkgs(self, logger: Logger = getLogger(__name__)) -> int
        Install KNIME packages needed to execute RetroPath2.0 workflow.

    call(self, files: Dict, params: Dict, preference: Preference, logger: Logger = getLogger(__name__)) -> int
        Run Knime workflow.
    """
    ZENODO_API = "https://zenodo.org/api/"
    KNIME_URL = "http://download.knime.org/analytics-platform/"

    def __init__(self, workflow: str="", kinstall: str=DEFAULT_KNIME_FOLDER, kver: str = DEFAULT_KNIME_VERSION, kexec: Optional[str]=None, *args, **kwargs) -> None:

        self.workflow = workflow
        self.kinstall = kinstall
        self.kver = kver
        self.kexec = kexec
        self.kexec_install = False
        self.kpkg_install = ""
        self.kurl = ""
        self.kzenodo_id = ""

        # Setting kexec, kpath, kinstall, kver
        if self.kexec is None:
            self.kzenodo_id = KNIME_ZENODO[self.kver]
            zenodo_query = self.zenodo_show_repo()
            for zenodo_file in zenodo_query["files"]:
                if sys.platform in zenodo_file["links"]["self"]:
                    self.kurl = zenodo_file["links"]["self"]
                    break

            self.kinstall = os.path.join(self.kinstall, '.knime', sys.platform)
            if sys.platform == 'darwin':
                kpath = os.path.join(self.kinstall, f'KNIME_{self.kver}.app')
                self.kexec = os.path.join(kpath, 'Contents', 'MacOS', 'knime')
            else:
                kpath = os.path.join(self.kinstall, f'knime_{self.kver}')
                self.kexec = os.path.join(kpath, 'knime')
                if sys.platform == 'win32':
                    self.kexec += '.exe'

            # Check if exec already exists
            if not os.path.exists(self.kexec):
                self.kexec_install = True

            # Create url
            self.kurl = ""
            if self.kver != "":
                if sys.platform == "linux":
                    self.kurl = urllib.parse.urljoin(self.KNIME_URL, "linux/knime_%s.linux.gtk.x86_64.tar.gz" % (self.kver,))
                elif sys.platform == "darwin":
                    self.kurl = urllib.parse.urljoin(self.KNIME_URL, "macosx/knime_%s.app.macosx.cocoa.x86_64.dmg" % (self.kver,))
                else:
                    self.kurl = urllib.parse.urljoin(self.KNIME_URL, "win/knime_%s.win32.win32.x86_64.zip" % (self.kver,))

            # Pkg variable
            self.kpkg_install = kpath
            if sys.platform == 'darwin':
                self.kpkg_install = os.path.join(self.kpkg_install, 'Contents', 'Eclipse')

        else:
            if sys.platform in ['linux', 'darwin']:
                self.kinstall = os.path.dirname(os.path.dirname(self.kexec))
            self.kver = ""

    def __repr__(self):
        s = ["Knime vars:"]
        s.append("workflow: " + self.workflow)
        s.append("kver: " + self.kver)
        s.append("kpkg_install: " + self.kpkg_install)
        s.append("kexec: " + self.kexec)
        s.append("kexec_install: " + str(self.kexec_install))
        s.append("kinstall: " + self.kinstall)
        if self.kurl != "":
            s.append("kurl: " + self.kurl)
        if self.kzenodo_id != "":
            s.append("kzenodo_id: " + self.kzenodo_id)
        return "\n".join(s)

    def zenodo_show_repo(self) -> Dict[str, Any]:
        """Show Zenodo repository informations.

        Return
        ------
        Dict[str, Any]
        """
        url = urllib.parse.urljoin(
            self.ZENODO_API, "records/%s" % (self.kzenodo_id,)
        )
        r = requests.get(url)
        if r.status_code > 202:
            raise ValueError(r.text)
        return r.json()

    @classmethod
    def standardize_path(cls, path: str) -> str:
        """Path are given with double backslashes on windows.
        Knime needs a path with simple slash in commandline.

        Parameters
        ----------
        path: str
            a path

        Return
        ------
        str
        """
        if sys.platform == 'win32':
            path = "/".join(path.split(os.sep))
        return path

    def install_exec(self, logger: Logger = getLogger(__name__)) -> None:
        """Install Knime executable

        Return
        ------
        None
        """
        logger.info('{attr1}Downloading KNIME {kver}...{attr2}'.format(attr1=attr('bold'), kver=self.kver, attr2=attr('reset')))
        if sys.platform == 'linux':
            download_and_extract_tar_gz(self.kurl, self.kinstall)
            chown_r(self.kinstall, getuser())
            # chown_r(kinstall, geteuid(), getegid())
        elif sys.platform == 'darwin':
            with tempfile.NamedTemporaryFile() as tempf:
                download(self.kurl, tempf.name)
                app_path = f'{self.kinstall}/KNIME_{self.kver}.app'
                if os.path.exists(app_path):
                    shutil.rmtree(app_path)
                with tempfile.TemporaryDirectory() as tempd:
                    cmd = f'hdiutil mount -noverify {tempf.name} -mountpoint {tempd}/KNIME'
                    subprocess_call(cmd, logger=logger)
                    shutil.copytree(
                        f'{tempd}/KNIME/KNIME {self.kver}.app',
                        app_path
                    )
                    cmd = f'hdiutil unmount {tempd}/KNIME'
                    subprocess_call(cmd, logger=logger)
        else:  # Windows
            download_and_unzip(self.kurl, self.kinstall)
        logger.info('   |--url: ' + self.kurl)
        logger.info('   |--install_dir: ' + self.kinstall)

    def install_pkgs(self, logger: Logger = getLogger(__name__)) -> int:
        """Install KNIME packages needed to execute RetroPath2.0 workflow.

        Parameters
        ----------
        logger : Logger
            The logger object.

        Return
        ------
        int
        """
        returncode = 0
        StreamHandler.terminator = ""
        logger.info( '   |- Checking KNIME packages...')
        logger.debug(f'        + kpkg_install: {self.kpkg_install}')
        logger.debug(f'        + kver: {self.kver}')

        tmpdir = tempfile.mkdtemp()

        args = [self.kexec]
        args += ['-application', 'org.eclipse.equinox.p2.director']
        args += ['-nosplash']
        args += ['-consoleLog']
        # Download from Zenodo
        zenodo_query = self.zenodo_show_repo()
        repositories = []
        for zenodo_file in zenodo_query["files"]:
            url = zenodo_file["links"]["self"]
            if "update.analytics-platform" in url or "TrustedCommunityContributions" in url:
                repo_path = os.path.join(tmpdir, os.path.basename(url))
                download(url, repo_path)
                repositories.append(repo_path)

        args += ["-r"]
        args.append(",".join(["jar:file:%s!/" % (x,) for x in repositories]))

        args += ["-i", 'org.knime.features.chem.types.feature.group,' \
            + 'org.knime.features.datageneration.feature.group,' \
            + 'org.knime.features.python.feature.group,' \
            + 'org.rdkit.knime.feature.feature.group']
        args += ['-bundlepool', self.kpkg_install]
        args += ['-d', self.kpkg_install]

        returncode = subprocess_call(" ".join(args), logger=logger)
        StreamHandler.terminator = "\n"
        shutil.rmtree(tmpdir, ignore_errors=True)

        logger.info(' OK')
        return returncode

    def install(self, logger: Logger = getLogger(__name__)) -> int:
        if self.kexec_install:
            self.install_exec(logger=logger)
            r_code = self.install_pkgs(logger=logger)
            return r_code
        return 0

    def call(
        self,
        files: Dict,
        params: Dict,
        preference: Preference,
        logger: Logger = getLogger(__name__)
    ) -> int:
        """Run Knime workflow.

        Parameters
        ----------
        files: Dict
            Paths of sink, source, rules files.
        params: Dict
            Parameters of the workflow to process.
        preference: Preference
            A preference object.
        logger : Logger
            The logger object.

        Return
        ------
        int
        """
        StreamHandler.terminator = ""
        logger.info('{attr1}Running KNIME...{attr2}'.format(attr1=attr('bold'), attr2=attr('reset')))

        args = [self.kexec]
        args += ["-nosplash"]
        args += ["-nosave"]
        args += ["-reset"]
        args += ["-consoleLog"]
        args += ["--launcher.suppressErrors"]
        args += ["-application", "org.knime.product.KNIME_BATCH_APPLICATION"]
        args += ["-workflowFile=%s" % (self.standardize_path(path=self.workflow),)]

        args += ['-workflow.variable=input.dmin,"%s",int' % (params['dmin'],)]
        args += ['-workflow.variable=input.dmax,"%s",int' % (params['dmax'],)]
        args += ['-workflow.variable=input.max-steps,"%s",int' % (params['max_steps'],)]
        args += ['-workflow.variable=input.topx,"%s",int' % (params['topx'],)]
        args += ['-workflow.variable=input.mwmax-source,"%s",int' % (params['mwmax_source'],)]

        args += ['-workflow.variable=input.sourcefile,"%s",String' % (self.standardize_path(files['source']),)]
        args += ['-workflow.variable=input.sinkfile,"%s",String' % (self.standardize_path(files['sink']),)]
        args += ['-workflow.variable=input.rulesfile,"%s",String' % (self.standardize_path(files['rules']),)]
        args += ['-workflow.variable=output.dir,"%s",String' % (self.standardize_path(files['outdir']),)]
        args += ['-workflow.variable=output.solutionfile,"%s",String' % (self.standardize_path(files['results']),)]
        args += ['-workflow.variable=output.sourceinsinkfile,"%s",String' % (self.standardize_path(files['src-in-sk']),)]
        if preference and preference.is_init():
            preference.to_file()
            args += ["-preferences=" + self.standardize_path(preference.path)]

        logger.debug(" ".join(args))

        try:
            printout = open(os.devnull, 'wb') if logger.level > 10 else None
            # Hack to link libGraphMolWrap.so (RDKit) against libfreetype.so.6 (from conda)
            is_ld_path_modified = False
            if "CONDA_PREFIX" in os.environ.keys():
                os.environ['LD_LIBRARY_PATH'] = os.environ.get(
                    'LD_LIBRARY_PATH',
                    ''
                ) + ':' + os.path.join(
                    os.environ['CONDA_PREFIX'],
                    "lib"
                ) + ':' + os.path.join(
                    os.environ['CONDA_PREFIX'],
                    "x86_64-conda-linux-gnu/sysroot/usr/lib64"
                )
                is_ld_path_modified = True

            returncode = subprocess_call(cmd=" ".join(args), logger=logger)
            if is_ld_path_modified:
                os.environ['LD_LIBRARY_PATH'] = ':'.join(
                    os.environ['LD_LIBRARY_PATH'].split(':')[:-1]
                )

            StreamHandler.terminator = "\n"
            logger.info(' {bold}OK{reset}'.format(bold=attr('bold'), reset=attr('reset')))
            return returncode

        except OSError as e:
            logger.error(e)
            return RETCODES['OSError']

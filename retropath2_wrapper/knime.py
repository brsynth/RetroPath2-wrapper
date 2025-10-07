import argparse
import glob
import os
import requests
import shutil
import subprocess
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
from typing import List
from subprocess import PIPE as sp_PIPE

from brs_utils  import (
    download_and_extract_tar_gz,
    download,
    download_and_unzip,
    chown_r,
    subprocess_call,
)
from retropath2_wrapper.Args import (
    DEFAULTS,
    RETCODES,
)
from retropath2_wrapper.preference import Preference


class Knime(object):
    """Knime is useful to install executable, install packages or commandline.

    Attributes
    ----------
    kinstall: str
        directory to found a "knime" executable
    workflow: str
        path of the Knime workflow
    """
    ZENODO_API = "https://zenodo.org/api/"
    KNIME_URL = "http://download.knime.org/analytics-platform/"
    ZENODO = {
        "4.6.4": "7515771",
        "4.7.0": "7564938",
    }
    DEFAULT_VERSION = "4.6.4"
    PLUGINGS = [
        "org.eclipse.equinox.preferences",
        "org.knime.chem.base",
        "org.knime.datageneration",
        "org.knime.python.nodes",
        "org.knime.features.chem.types.feature.group",
        "org.knime.features.datageneration.feature.group",
        "org.knime.features.python.feature.group",
        "org.rdkit.knime.feature.feature.group",
        "org.rdkit.knime.nodes",
    ]

    def __init__(
            self,
            kinstall: str = DEFAULTS['KNIME_FOLDER'],
            workflow: str = "",
        ) -> None:
        self.kinstall = kinstall
        self.workflow = workflow
        self.kexec = Knime.find_executable(path=self.kinstall)

    def __repr__(self):
        s = []
        s.append(f"workflow: {self.workflow}")
        s.append(f"kinstall: {self.kinstall}")
        s.append(f"kexec: {self.kexec}")
        return "\n".join(s)

    @classmethod
    def zenodo_show_repo(cls, kver: str) -> Dict[str, Any]:
        """Show Zenodo repository informations.

        Return
        ------
        Dict[str, Any]
        """
        
        kzenodo_id = Knime.ZENODO[kver]
        url = urllib.parse.urljoin(
            Knime.ZENODO_API, f"records/{kzenodo_id}"
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

    @classmethod
    def find_executable(cls, path: str) -> str:
        for root, _, files in os.walk(path):
            for file in files:
                path_file = os.path.join(root, file)
                if os.access(path_file, os.X_OK) and os.path.isfile(path_file):
                    if file.lower() == "knime":
                        return os.path.abspath(path_file)
        return ""

    @classmethod
    def find_p2_dir(cls, path: str) -> str:
        for root, _, files in os.walk(path):
            for file in files:
                path_file = os.path.join(root, file)
                if file == "p2" and os.path.isdir(path_file):
                    return os.path.abspath(path_file)
        return ""

    def install(self, kver: str, logger: Logger = getLogger(__name__)) -> bool:
        data = Knime.zenodo_show_repo(kver=kver)
        # Install Knime
        for file in data["files"]:
            basename = file["key"]
            url = file["links"]["self"]
            if "linux" in basename and sys.platform == "linux":
                download_and_extract_tar_gz(url, self.kinstall)
                chown_r(self.kinstall, getuser())
                # chown_r(kinstall, geteuid(), getegid())
                break
            elif "macosx" in basename and sys.platform == "darwin":
                with tempfile.NamedTemporaryFile() as tempf:
                    download(url, tempf.name)
                    app_path = f'{self.kinstall}/KNIME_{kver}.app'
                    if os.path.exists(app_path):
                        shutil.rmtree(app_path)
                    with tempfile.TemporaryDirectory() as tempd:
                        cmd = f'hdiutil mount -noverify {tempf.name} -mountpoint {tempd}/KNIME'
                        subprocess_call(cmd, logger=logger)
                        shutil.copytree(
                            f'{tempd}/KNIME/KNIME {kver}.app',
                            app_path
                        )
                        cmd = f'hdiutil unmount {tempd}/KNIME'
                        subprocess_call(cmd, logger=logger)
                break
            elif "win32" in basename and sys.platform == "win32":
                download_and_unzip(url, self.kinstall)
                break

        # Download Plugins
        tempdir = tempfile.mkdtemp()
        try:
            path_plugins = []
            for file in data["files"]:
                basename = file["key"]
                url = file["links"]["self"]
                if "org.knime.update" in basename or "TrustedCommunity" in basename:
                    path_plugin = os.path.join(tempdir, basename)
                    download(url=url, file=path_plugin)
                    path_plugins.append(path_plugin)

            # Install Plugins
            self.kexec = Knime.find_executable(path=self.kinstall)
            p2_dir = Knime.find_p2_dir(path=self.kinstall)
            knime_dir = [x for x in glob.glob(os.path.join(self.kinstall, "*")) if "knime" in x.lower()]
            args = [f"{self.kexec}"]
            args += ["-nosplash", "-consoleLog"]
            args += ["-application", "org.eclipse.equinox.p2.director"]
            args += ["-repository", ",".join([f"jar:file:{path_plugin}!/" for path_plugin in path_plugins])]
            args += ["-bundlepool", p2_dir]
            args += ["-destination", os.path.abspath(knime_dir[0])]
            args += ["-i", ",".join(Knime.PLUGINGS)]

            CPE = subprocess.run(args)
            logger.debug(CPE)
        except Exception as error:
            logger.error(error)
        finally:
            # Clean up
            shutil.rmtree(tempdir)
        return True

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
        print("Hydrogen:", params["std_hydrogen"])
        args += ['-workflow.variable=input.std_mode,"%s",String' % (params["std_hydrogen"],)]
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

            CPE = subprocess.run(args)
            logger.debug(CPE)
            if is_ld_path_modified:
                os.environ['LD_LIBRARY_PATH'] = ':'.join(
                    os.environ['LD_LIBRARY_PATH'].split(':')[:-1]
                )

            StreamHandler.terminator = "\n"
            logger.info(' {bold}OK{reset}'.format(bold=attr('bold'), reset=attr('reset')))
            return CPE.returncode

        except OSError as e:
            logger.error(e)
            return RETCODES['OSError']


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--kinstall", required=True, help="Path to install Knime"
    )
    parser.add_argument(
        "--kver", default="4.6.4", choices=["4.6.4", "4.7.0"], help="Knime version"
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="Install even if the executable is not present"
    )
    args = parser.parse_args()

    path_knime = args.kinstall
    kver = args.kver
    to_overwrite = True if args.overwrite else False

    os.makedirs(path_knime, exist_ok=True)
    knime = Knime(kinstall=path_knime)

    if to_overwrite or not knime.kexec:
        knime.install(kver=kver)
    
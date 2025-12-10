import argparse
import glob
import os
import re
from zipfile import ZipFile
import requests
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path
from getpass import getuser
from logging import (
    getLogger,
    Logger,
    StreamHandler,
)
from typing import Any, Dict, Optional
from colored import attr
from typing import Set
from subprocess import PIPE as sp_PIPE

from brs_utils  import (
    extract_tar_gz,
    download,
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
    http://download.knime.org/analytics-platform/

    Attributes
    ----------
    kinstall: str
        directory to found a "knime" executable
    workflow: str
        path of the Knime workflow
    """
    ZENODO_API = "https://zenodo.org/api/"
    ZENODO = {
        "4.6.4": "7515771",
        "4.7.0": "7564938",
    }
    DEFAULT_VERSION = "4.6.4"
    PLUGINS = [
        "org.eclipse.equinox.preferences",
        "org.knime.chem.base",
        "org.knime.datageneration",
        "org.knime.features.chem.types.feature.group",
        "org.knime.features.datageneration.feature.group",
        "org.knime.features.python.feature.group",
        "org.knime.python.nodes",
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
                    if "knime" in os.path.basename(file.lower()):
                        return os.path.abspath(path_file)
        return ""

    @classmethod
    def find_p2_dir(cls, path: str) -> str:
        for dirpath, dirnames, _ in os.walk(path):
            if "p2" in dirnames:
                return os.path.abspath(os.path.join(dirpath, "p2"))
        return ""

    @classmethod
    def collect_top_level_dirs(cls, path) -> Set:
        root = Path(path)
        names = set()
        for p in root.iterdir():
            if p.is_dir():
                names.add(p.name)
        return names

    @classmethod
    def download_from_zenodo(cls, path: str, kver: str, logger: Logger = getLogger(__name__)):
        """
        Download files from a Zenodo repository

        Parameters
        ----------
        path: str
            An empty directory where files will be downloaded
        kver: str
            4.6.4 or 4.7.0
        """
        data = Knime.zenodo_show_repo(kver=kver)
        if sys.platform == "win32" or sys.platform == "linux":
            platform_tag = sys.platform
        elif sys.platform == "darwin":
            platform_tag = "macosx"
        else:
            raise RuntimeError(f"Platform {sys.platform} not supported for KNIME installation")
        for file in data["files"]:
            basename = file["key"]
            if platform_tag in basename:
                url = file["links"]["self"]
                foutput = os.path.join(path, basename)
                logger.info(f"Download: {url} to {foutput}")
                download(url, foutput)
                break

    def install(self, path: str, logger: Logger = getLogger(__name__)) -> bool:
        """
        Install KNIME and required plugins (headless mode).
        """

        knime_files = glob.glob(os.path.join(path, "*"))

        # ---------------------------------------------------------
        # 1) Extract KNIME base installation
        # ---------------------------------------------------------
        dirs_before = Knime.collect_top_level_dirs(path=self.kinstall)
        for file in knime_files:
            basename = os.path.basename(file)

            # Linux
            if "linux" in basename and sys.platform == "linux":
                extract_tar_gz(file, self.kinstall)
                chown_r(self.kinstall, getuser())
                break

            # macOS
            elif "macosx" in basename and sys.platform == "darwin":
                match = re.search(r"\d+\.\d+\.\d+", basename)
                if not match:
                    raise ValueError(f"Could not determine version from filename: {file}")
                kver = match.group()

                app_path = f"{self.kinstall}/KNIME_{kver}.app"
                if os.path.exists(app_path):
                    shutil.rmtree(app_path)

                with tempfile.TemporaryDirectory() as tempd:
                    cmd = f'hdiutil mount -noverify {file} -mountpoint {tempd}/KNIME'
                    subprocess_call(cmd, logger=logger)
                    shutil.copytree(
                        f'{tempd}/KNIME/KNIME {kver}.app',
                        app_path
                    )
                    cmd = f'hdiutil unmount {tempd}/KNIME'
                    subprocess_call(cmd, logger=logger)
                break

            # Windows
            elif "win32" in basename and sys.platform == "win32":
                unzip(file, self.kinstall)
                break

        dirs_after = Knime.collect_top_level_dirs(path=self.kinstall)
        dirs_only_after = dirs_after - dirs_before
        assert len(dirs_only_after) == 1, f"New directory not unique: {dirs_only_after}"

        knime_root = os.path.abspath(os.path.join(self.kinstall, dirs_only_after.pop()))

        # ---------------------------------------------------------
        # 2) Collect local plugin repositories (ZIPs from Zenodo)
        # ---------------------------------------------------------
        local_repos = []
        for file in knime_files:
            basename = os.path.basename(file)
            if ("org.knime.update" in basename or 
                "TrustedCommunity" in basename or
                "chemistry" in basename.lower()):  # allow offline chemistry repo ZIP too
                local_repos.append(f"jar:file:{os.path.abspath(file)}!/")

        # ---------------------------------------------------------
        # 3) Add online repositories (required for chemistry & RDKit)
        # ---------------------------------------------------------
        online_repos = [
            "https://update.knime.com/analytics-platform/4.6/",
            "https://update.knime.com/analytics-platform/4.6/chemistry/",
            # optional but useful:
            "https://update.knime.com/community-contributions/trusted/4.6/"
        ]

        all_repos = local_repos + online_repos

        # ---------------------------------------------------------
        # 4) Run p2 director to install plugins
        # ---------------------------------------------------------
        self.kexec = Knime.find_executable(path=self.kinstall)
        p2_dir = Knime.find_p2_dir(path=self.kinstall)

        if not self.kexec:
            raise FileNotFoundError(f"KNIME executable not found under {self.kinstall}")
        if not p2_dir:
            raise RuntimeError("p2 directory not found after installation.")

        args = [
            self.kexec,
            "-nosplash",
            "-consoleLog",
            "-application", "org.eclipse.equinox.p2.director",
            "-repository", ",".join(all_repos),
            "-bundlepool", p2_dir,
            "-destination", knime_root,
            "-i", ",".join(Knime.PLUGINS)
        ]

        logger.info("Command line to install KNIME plugins:")
        logger.info(" ".join(args))

        CPE = subprocess.run(args)
        logger.debug(CPE)

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

        if not self.kexec or not os.path.exists(self.kexec):
            raise FileNotFoundError(f"KNIME executable not found under {self.kinstall}")

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
        args += ['-workflow.variable=input.std_mode,"%s",String' % (params["std_hydrogen"],)]
        if preference and preference.is_init():
            preference.to_file()
            args += ["-preferences=" + self.standardize_path(preference.path)]

        logger.debug(" ".join(args))

        old_ld = os.environ.get("LD_LIBRARY_PATH")
        try:
            printout = open(os.devnull, 'wb') if logger.level > 10 else None
            # Hack to link libGraphMolWrap.so (RDKit) against libfreetype.so.6 (from conda)
            if "CONDA_PREFIX" in os.environ:
                extra = [
                    os.path.join(os.environ["CONDA_PREFIX"], "lib"),
                    os.path.join(os.environ["CONDA_PREFIX"], "x86_64-conda-linux-gnu/sysroot/usr/lib64"),
                ]
                os.environ["LD_LIBRARY_PATH"] = ":".join(filter(None, [old_ld, *extra]))

            CPE = subprocess.run(args)
            logger.debug(CPE)

            StreamHandler.terminator = "\n"
            logger.info(' {bold}OK{reset}'.format(bold=attr('bold'), reset=attr('reset')))
            return CPE.returncode

        except OSError as e:
            logger.error(e)
            return RETCODES['OSError']
        finally:
            if old_ld is None:
                os.environ.pop("LD_LIBRARY_PATH", None)
            else:
                os.environ["LD_LIBRARY_PATH"] = old_ld


def install_online(args, logger: Logger = getLogger(__name__)):
    path_knime = args.kinstall
    kver = args.kver

    tempdir = tempfile.mkdtemp()
    os.makedirs(path_knime, exist_ok=True)
    try:
        Knime.download_from_zenodo(path=tempdir, kver=kver, logger=logger)
        knime = Knime(kinstall=path_knime)
        knime.install(path=tempdir, logger=logger)
    except Exception as e:
        raise RuntimeError(e)
    finally:
        shutil.rmtree(tempdir)

def install_local(args, logger: Logger = getLogger(__name__)):
    path_knime = args.kinstall
    path_zenodo = args.zenodo_zip

    tempdir = tempfile.mkdtemp()
    os.makedirs(path_knime, exist_ok=True)
    try:
        logger.info(f"Unzip: {path_zenodo}")
        unzip(
            file=path_zenodo,
            dir=tempdir,
        )
        knime = Knime(kinstall=path_knime)
        logger.info(f"Install to: {path_knime}")
        knime.install(path=tempdir, logger=logger)
    except Exception as e:
        raise RuntimeError(e)
    finally:
        shutil.rmtree(tempdir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    # Online
    par_onl = subparsers.add_parser("online")
    par_onl.add_argument(
        "--kinstall", required=True, help="Path to install Knime"
    )
    par_onl.add_argument(
        "--kver", default="4.6.4", choices=["4.6.4", "4.7.0"], help="Knime version"
    )
    par_onl.set_defaults(func=install_online)
    
    # Local
    par_loc = subparsers.add_parser("local")
    par_loc.add_argument(
        "--kinstall", required=True, help="Path to install Knime"
    )
    zenodo_files = ", ".join([x + ".zip" for x in Knime.ZENODO.values()])
    par_loc.add_argument(
        "--zenodo-zip", required=True, help=f"Zenodo file obtained from \"Download all\" button from Zenodo, such as {zenodo_files}"
    )
    par_loc.set_defaults(func=install_local)

    args = parser.parse_args()
    args.func(args)
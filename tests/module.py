"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from _main import Main
from tempfile import TemporaryDirectory
from os import path as os_path
from os import stat as os_stat
from argparse import Namespace as argparse_Namespace

tempdir = TemporaryDirectory()


class Module(Main):
    __test__ = False

    mod_name  = 'retropath2_wrapper'
    func_name = 'run'
    data_path = 'data'
    args      = argparse_Namespace()
    args.sinkfile   = data_path+'/Galaxy177-Sink_Compounds.csv'
    args.sourcefile = data_path+'/Galaxy160-Source.csv'
    args.rulesfile  = data_path+'/rules.csv'
    args.outdir     = tempdir.name

    files = [
    (tempdir.name+'/'+'results.csv', 'a8a5522a3db9e53f2a44c95c81ba78562e30e0450467050730b0b4cb3a551101')
    ]

    KVER         = '3.6.2'
    KURL         = 'http://download.knime.org/analytics-platform/linux/knime_'+KVER+'.linux.gtk.x86_64.tar.gz'
    KINSTALL     = '/tmp'
    KPATH        = KINSTALL+'/knime_'+KVER
    KEXEC        = KPATH+'/knime'

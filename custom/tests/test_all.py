"""
Created on June 17 2020

@author: Joan Hérisson
"""

from unittest import TestCase

from os import stat
from sys import path as sys_path
sys_path.insert(0, './src')
from retropath2 import run
from itertools import combinations
from random import sample
from hashlib import sha256
from pathlib import Path


# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
# 'Test_' prefix is mandatory
class Test_RR(TestCase):

    def __init__(self, testname):
        super(Test_RR, self).__init__(testname)
        self.diameters = ['2','4','6','8','10','12','14','16']

    # 'test_' prefix is mandatory
    def test_RetroRules__BadRuleTypeArgument(self):
        for rule_type in ['', 'test', 'reto']:
            with self.subTest(rule_type=rule_type):
                outfile = rules(rule_type, 'out', '2')
                self.assertEqual(outfile, False)

    def test_RetroRules__BadDiametersArgument(self):
        for diam in ['3']:
            with self.subTest(diam=diam):
                outfile = rules('retro', 'out', diam)
                self.assertEqual(stat(outfile).st_size, 135)

    def test_RetroRules__OneDiameter(self):
        for diam in ['2']:
            with self.subTest(diam=diam):
                outfile = rules('retro', 'out', diam)
                self.assertEqual(sha256(Path(outfile).read_bytes()).hexdigest(), '68cca7d6b890676d62ef0d950db3ce9a1ca5f991e54d91932e551b4fb42ff709')

    def test_RetroRules__MiscDiametersArgument(self):
        for diam in ['2-']:
            with self.subTest(diam=diam):
                outfile = rules('retro', 'out', diam)
                self.assertEqual(stat(outfile).st_size, 135)

    def test_RetroRules__AllTypes_RandomDiam(self):
        for rule_type in ['all', 'retro', 'forward']:
            for i in range(len(self.diameters)):
                diams = list(combinations(self.diameters,i+1))
                sub_diams = sample(diams,1)
                for diam in sub_diams:
                    with self.subTest(rule_type=rule_type, diam=diam):
                        outfile = rules(rule_type, 'out', ','.join(diam))
                        self.assertGreater(stat(outfile).st_size, 135)

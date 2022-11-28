"""
Created on Jul 15 2020

@author: Joan Hérisson
"""
import os
import tempfile

from retropath2_wrapper.preference import Preference
from tests.main_test import Main_test


class TestPreference(Main_test):
    def test_init(self):
        pref = Preference(path=os.getcwd(), rdkit_timeout_minutes=50, rdkit="test")
        self.assertEqual(pref.path, os.getcwd())
        self.assertEqual(pref.rdkit_timeout_minutes, 50)
        with self.assertRaises(Exception):
            pref.rdkit

    def test_to_file(self):
        pref = Preference(rdkit_timeout_minutes=10)
        pref.to_file()
        with open(pref.path) as fid:
            res = fid.read().splitlines()
        with open(self.preference) as fid:
            the = fid.read().splitlines()
        self.assertEqual(res[1:], the[1:])

    def test_is_init(self):
        pref = Preference()
        self.assertFalse(pref.is_init())
        pref = Preference(rdkit_timeout_minutes=10)
        self.assertTrue(pref.is_init())


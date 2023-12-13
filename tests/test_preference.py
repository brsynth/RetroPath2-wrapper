"""
Created on Jul 15 2020

@author: Joan Hérisson
"""
import os

import pytest
from retropath2_wrapper.preference import Preference


class TestPreference:
    def test_init(self):
        pref = Preference(path=os.getcwd(), rdkit_timeout_minutes=50, rdkit="test")
        assert pref.path == os.getcwd()
        assert pref.rdkit_timeout_minutes == 50
        with pytest.raises(Exception):
            pref.rdkit

    def test_to_file(self, preference_path):
        pref = Preference(rdkit_timeout_minutes=10)
        pref.to_file()
        with open(pref.path) as fid:
            res = fid.read().splitlines()
        with open(preference_path) as fid:
            the = fid.read().splitlines()
        assert res[1:] == the[1:]

    def test_is_init(self):
        pref = Preference()
        assert pref.is_init() is False
        pref = Preference(rdkit_timeout_minutes=10)
        assert pref.is_init() is True

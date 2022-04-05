# -*- coding: utf-8 -*-

import pytest
import academic_tracker
print(academic_tracker.__file__)
from academic_tracker import __main__
print(__main__.__file__)

@pytest.fixture(autouse=True)
def set_verbose_and_silent(monkeypatch):
    monkeypatch.setattr(__main__, "SILENT", False)
    monkeypatch.setattr(__main__, "VERBOSE", True)


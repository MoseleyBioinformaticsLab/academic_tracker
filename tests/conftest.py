# -*- coding: utf-8 -*-

import pytest

from academic_tracker import __main__

@pytest.fixture(autouse=True)
def set_verbose_and_silent(monkeypatch):
    monkeypatch.setattr(__main__, "SILENT", False)
    monkeypatch.setattr(__main__, "VERBOSE", True)


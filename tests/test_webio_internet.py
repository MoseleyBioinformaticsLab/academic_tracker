# -*- coding: utf-8 -*-


import pytest
from academic_tracker.webio import check_pubmed_for_grants





@pytest.mark.network_access
def test_check_pubmed_for_grants_has_grant():
    grants = check_pubmed_for_grants("33830777", ["P42 ES007380"])
    
    assert grants == set(["P42 ES007380"])

@pytest.mark.network_access
def test_check_pubmed_for_grants_no_grant():
    grants = check_pubmed_for_grants("34352431", ["P42 123412341234"])
    
    assert grants == set()




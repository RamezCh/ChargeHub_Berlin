import pytest
from chargehub.malfunction.infrastructure.repositories.report_repository import ReportRepository, StoredReport

def test_report_repository_methods():
    repo = ReportRepository()
    
    # Test initial state
    assert len(repo.all_reports()) == 0
    assert len(repo.get_affected_station_ids()) == 0
    
    # Test save_report
    count = repo.save_report(101, "Issue 1")
    assert count == 1
    assert len(repo.all_reports()) == 1
    assert repo.has_report(101, "Issue 1") is True
    
    # Test save more
    repo.save_report(101, "Issue 2")
    count = repo.save_report(102, "Issue A")
    
    assert count == 1 # first for 102
    assert repo.count_reports(101) == 2
    
    # Test all_reports
    all_reps = repo.all_reports()
    assert len(all_reps) == 3
    
    # Test get_affected_station_ids
    ids = repo.get_affected_station_ids()
    assert 101 in ids
    assert 102 in ids
    assert len(ids) == 2
    
    # Test clear_reports
    repo.clear_reports(101)
    assert repo.count_reports(101) == 0
    assert repo.count_reports(102) == 1
    assert 101 not in repo.get_affected_station_ids()

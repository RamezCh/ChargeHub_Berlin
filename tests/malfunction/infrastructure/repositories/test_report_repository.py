from chargehub.malfunction.infrastructure.repositories.report_repository import ReportRepositoryImpl

def test_report_repository_methods():
    repo = ReportRepositoryImpl()
    
    # Test initial state
    assert len(repo.all_reports()) == 0
    assert len(repo.get_affected_station_ids()) == 0
    
    # Test save_report
    report_id = repo.save_report(101, "Issue 1")
    assert report_id is not None
    assert len(repo.all_reports()) == 1
    assert repo.has_report(101, "Issue 1") is True
    
    # Test save more
    repo.save_report(101, "Issue 2")
    repo.save_report(102, "Issue A")
    
    # count_reports only counts APPROVED reports, so it should be 0 for pending
    assert repo.count_reports(101) == 0
    
    # Test all_reports
    all_reps = repo.all_reports()
    assert len(all_reps) == 3
    
    # Test get_affected_station_ids (only approved > 0)
    ids = repo.get_affected_station_ids()
    assert len(ids) == 0
    
    # Test clear_reports
    repo.clear_reports(101)
    
    # Check that reports for 101 are gone
    remaining = repo.all_reports()
    # We had 3 reports total (101: Issue 1, 101: Issue 2, 102: Issue A)
    # After clearing 101, we should have 1 report (for 102)
    assert len(remaining) == 1
    assert remaining[0].station_id == 102
    
    # 102 should still be there (but count is 0 as it is pending)
    assert repo.count_reports(102) == 0

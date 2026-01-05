from chargehub.malfunction.domain.events.malfunction_report_acknowledged import MalfunctionReportAcknowledgedEvent

def test_malfunction_report_acknowledged_event():
    event = MalfunctionReportAcknowledgedEvent(station_id=456)
    assert event.station_id == 456

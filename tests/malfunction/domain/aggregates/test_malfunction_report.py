from chargehub.malfunction.domain.aggregates.malfunction_report import MalfunctionReportAggregate
from chargehub.malfunction.domain.value_objects.report_text import ReportText

def test_malfunction_report_creation():
    report_text = ReportText("Broken charger")
    aggregate = MalfunctionReportAggregate(
        station_id=123,
        report=report_text,
        acknowledged=False
    )
    
    assert aggregate.station_id == 123
    assert aggregate.report == report_text
    assert aggregate.acknowledged is False
    
def test_malfunction_report_acknowledged_default():
    report_text = ReportText("Broken charger")
    aggregate = MalfunctionReportAggregate(
        station_id=123,
        report=report_text
    )
    assert aggregate.acknowledged is False

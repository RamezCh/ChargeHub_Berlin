# Domain Model (ChargeHub Berlin)

This documentation reflects the DDD artifacts (Use Case, Event Storming, Bounded Contexts, Workflow, Sequence Diagrams).

## Bounded Contexts
- Charging Station Discovery
- Station Malfunction Management

## Ubiquitous Language
- PostalCode / PLZ
- ChargingStation
- Availability (AVAILABLE / UNAVAILABLE)
- MalfunctionReport

## Domain Events
Discovery:
- StationSearchInitiatedEvent
- PostalCodeValidatedEvent / PostalCodeFailedEvent
- StationsFoundEvent / NoStationsFoundEvent

Malfunction:
- MalfunctionReportFiledEvent
- AdministratorNotifiedEvent
- ReportCounterIncrementedEvent
- MalfunctionReportThresholdReachedEvent
- StationStatusChangedEvent
- RepairCompletedEvent

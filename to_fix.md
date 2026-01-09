# ChargeHub Berlin – Project Documentation

## Team Information

**Team:** Team 2  
**Git Repository:** https://github.com/RamezCh/ChargeHub_Berlin  

**Team Members:**
- 110308 Ramez Chreide  
- 824145 Volkan Korunan  
- 111935 Jawad Ahmed  
- 110478 Ali Ahmadi  

---

## 1. Introduction to the Topic and Selected Use Cases

### 1.1 Project Overview

ChargeHub Berlin is an interactive platform designed to streamline the electric vehicle (EV) charging experience for Berlin residents.  
The platform focuses on two core functionalities:

- Discovering available EV charging infrastructure
- Reporting and tracking charging station malfunctions

Users can search for charging stations by postal code using real-time filters that display only currently available charging plugs. Additionally, users contribute to system reliability by reporting malfunctions, improving overall charging infrastructure quality.

---

### 1.2 Problem Statement

Despite the increasing number of EV charging stations in Berlin, several challenges hinder seamless electromobility adoption:

- **Lack of Real-Time Transparency**  
  Existing tools often provide static data that does not reflect real-time availability.

- **Maintenance Gaps**  
  Malfunctioning stations are frequently not reported or updated promptly.

- **Insufficient Data Integration**  
  Community feedback is not effectively integrated into infrastructure planning.

- **Geographic Imbalance**  
  Certain districts lack sufficient charging capacity or reliable data.

---

### 1.3 Objectives

The main objectives of ChargeHub Berlin are:

- Provide transparent, structured access to charging station data by postal code
- Enable users to report malfunctions and track resolution status
- Reuse real-world datasets from Part 1 within a clean architecture
- Apply DDD, TDD, UML, and SOLID principles
- Demonstrate transformation of data-driven insights into production-ready software

---

### 1.4 Selected Use Cases

Based on domain analysis, event storming, and modeling activities, two core use cases were fully implemented:

#### Charging Station Discovery by Postal Code

Allows EV drivers to search for charging stations within a specific postal code.

**Business Rules:**
- Postal code must be numeric
- Exactly five digits
- Must start with `10`, `12`, or `13`

The system retrieves matching stations and displays their availability and utilization status.

#### Malfunction Report for Charging Stations

Enables users to report malfunctioning charging stations.

**Workflow:**
- Report validation
- Storage and administrator review
- Threshold-based status change to *Unavailable*
- Status restoration after repair completion

Both use cases were modeled using:
- UML Use Case Diagrams
- Workflow Diagrams
- Sequence Diagrams
- Domain Event Flow Diagrams

---

## 2. Technology Stack

The project was fully implemented in Python using a clean, Domain-Driven Design inspired architecture.

### Core Technologies

- **Programming Language:** Python 3
- **Backend Architecture:** Domain-Driven Design (DDD)
- **Web UI:** Streamlit
- **Testing Framework:** PyTest
- **Persistence:** In-memory structures & CSV datasets
- **Modeling Tools:** UML, Miro, Mermaid, Draw.io
- **IDE:** VS Code / PyCharm
- **Version Control:** Git & GitHub
- **LLM Support:** ChatGPT

Streamlit was chosen to rapidly prototype and visualize workflows while maintaining clear separation between layers.

---

## 3. Project Development Documentation

### 3.1 Domain Modeling and Event Structure (DDD)

Domain-Driven Design (DDD) was used to structure the system around core business concepts.  
Event storming identified commands, aggregates, domain events, and rules.

#### Bounded Contexts

- **Charging Station Discovery Context**  
  Searching and locating charging stations by postal code and availability.

- **Malfunction Management Context**  
  Reporting, reviewing, and resolving malfunctions.

#### Aggregates

- **ChargingStationAggregate**
  - Postal code validation
  - Station lookup
  - Availability checks
  - Status updates

- **MalfunctionAggregate**
  - Report validation
  - Report counting
  - Admin approval
  - Threshold handling

#### Key Domain Events

- PostalCodeSubmitted  
- PostalCodeValidated  
- LocateChargingStationsByPostalCode  
- SearchDataFetched  
- DisplaySearchResults  

- MalfunctionReportFiled  
- AdministratorNotified  
- AdministratorRejectsOrApproves  
- ReportCountIncrementedIfApproved  
- MalfunctionReportThresholdReached  
- StationStatusUpdatedToUnavailable  
- MalfunctionReportAcknowledged  
- RepairCompleted  
- StationStatusUpdatedToAvailable  

Each aggregate strictly follows separation into:
- Domain Layer
- Application Layer
- Infrastructure Layer

---

### 3.2 Test-Driven Development (TDD)

The project strictly followed Test-Driven Development principles.

#### Development Approach

- Red–Green–Refactor cycle
- Tests written before production code
- Each business rule implemented as a unit test first

#### Test Structure

- **Unit Tests:**  
  - Domain logic
  - Value objects
  - Aggregates
  - Domain events

Test structure mirrors production modules (`discovery`, `malfunction`) for traceability.

#### Test Coverage

- ~99% target coverage achieved
- Full coverage of:
  - Validation rules
  - Threshold logic
  - State transitions

Coverage monitored using PyTest and IDE tools.

---

### 3.3 Integration of Explored Datasets

- CSV-based charging station data integrated into discovery context
- Repository interfaces abstract data access
- Existing logic retested after integration
- Infrastructure concerns isolated from domain layer

---

### 3.4 LLM Integration

LLMs were used selectively to support development:

- DDD modeling guidance
- Diagram best practices
- Mermaid code generation
- UI implementation guidance

Engineering decisions always remained human-driven.

---

## 4. Technical Challenges

### Challenge 1: Maintaining Strict TDD Discipline

**Solution:**  
Clear task separation and regular code reviews ensured compliance.

### Challenge 2: Structuring the Domain Model

**Solution:**  
Iterative refinement of bounded contexts and continuous DDD alignment.

---

## 5. Project Completion and Reflection

### 5.1 Milestones Achieved

- Two core use cases implemented
- Domain-driven architecture established
- Test coverage close to 80%+ target

### 5.2 Not Achieved

- Advanced demand visualization
- Full gamification features

### 5.3 Lessons Learned

- TDD significantly improves maintainability
- DDD helps manage system complexity
- LLMs add value when used selectively

---

## 6. Conclusion

ChargeHub Berlin demonstrates how modern software engineering practices can be applied to a socially relevant problem.  
The project provides a strong foundation for future extensions and potential real-world deployment.

---

## 7. Architectural & Process Implementation (Examples)

This section provides concrete examples of the architectural principles and processes applied in the project, demonstrating strict adherence to SOLID and DDD.

### 7.1 Explicit Value Objects
In our Domain Layer, we ensure that concepts like `PostalCode` are not just strings but strict Value Objects with validation logic.

**Example Code (`src/chargehub/discovery/domain/value_objects/postal_code.py`):**
```python
@dataclass(frozen=True)
class PostalCode:
    value: str

    def __post_init__(self):
        if not self.value.isdigit() or len(self.value) != 5:
            raise ValueError("Postal code must be exactly 5 digits.")
        if not self.value.startswith(("10", "12", "13")):
            raise ValueError("Postal code is outside Berlin operating area.")
```

### 7.2 TDD Process (Red-Green-Refactor)
We followed a strict TDD cycle. Here is the concrete code evolution for the **Malfunction Threshold Logic**:

#### 1. RED (Write Fail Test)
We write a test asserting that a station becomes `UNAVAILABLE` after the 5th approved report. At this stage, the test fails because the logic doesn't exist.

```python
# tests/malfunction/unit/application/test_malfunction_service.py
def test_threshold_marks_station_unavailable():
    # Setup: ...
    
    # Action: Approve 5th report
    events = service.approve_report(report_id)
    
    # Assert: Station status should be False (Unavailable)
    station = charging_repo.get_all()[0]
    assert station.available is False  # FAILS -> Algorithm not implemented yet
```

#### 2. GREEN (Make it Pass - Naive Implementation)
We implement the simplest code to pass the test. We directly manipulate the repository without concern for domain events or clean separation.

```python
# src/chargehub/malfunction/application/malfunction_service.py
def approve_report(self, report_id):
    # ... approval logic ...
    
    count = self.report_repository.count_reports(station_id)
    if count >= 5:
        # NAIVE: Direct side-effect, hard dependency, no event record
        self.charging_station_repository.update_station_status(station_id, False) 
```

#### 3. REFACTOR (Clean Code & DDD)
We refactor to ensure logic is explicit, decoupled, and observable via Domain Events.

```python
# src/chargehub/malfunction/application/malfunction_service.py (Refactored)
def approve_report(self, report_id: str) -> Sequence[object]:
    # ...
    
    if current_count >= self.threshold:
        # 1. Raise Event for Side Effects / Logging
        events.append(MalfunctionReportThresholdReachedEvent(
            station_id=station_id, threshold=self.threshold, current_count=current_count
        ))
        
        # 2. Update Status explicitely
        self.charging_station_repository.update_station_status(station_id=station_id, status=False)
        events.append(StationStatusChangedEvent(station_id=station_id, status="UNAVAILABLE"))
        
    return events
```

### 7.3 SOLID Principles (Dependency Inversion & Interface Segregation)
We avoid hard dependencies on concrete repository classes within the Domain Layer. Instead, we define strict interfaces.

**Interface (Domain Layer - `src/chargehub/discovery/domain/interfaces/charging_station_repository.py`)**
```python
class ChargingStationRepository(ABC):
    @abstractmethod
    def locate_charging_stations(self, postal_code: PostalCode) -> List[ChargingStationAggregate]:
        pass

    @abstractmethod
    def update_station_status(self, station_id: int, status: bool) -> None:
        pass
```

**Implementation (Infrastructure Layer - `src/chargehub/discovery/infrastructure/repositories/charging_station_csv_repository.py`):**
```python
class ChargingStationCSVRepository(ChargingStationRepository):
    def locate_charging_stations(self, postal_code: PostalCode):
        # Implementation details hidden from Domain
        return [s for s in self._stations if s.postal_code == postal_code.value]
```

### 7.4 Clean Code Standards
-   **KISS (Keep It Simple Stupid)**: Methods are focused and small.
    ```python
    def save_report(self, station_id: int, report_text: str) -> UUID:
        report_id = uuid4()
        self._reports.append(StoredReport(..., status=ReportStatus.PENDING))
        return report_id
    ```
-   **DRY (Don't Repeat Yourself)**: Shared logic like `event_to_dict` is extracted into utilities or base classes.
-   **Naming**: Explicit and verbose method names e.g., `file_malfunction_report` instead of `report()`.
-   **Error Handling**: We use explicit Exceptions for domain errors (e.g., `ValueError` for invalid input) rather than returning None or False.

---

## 8. Domain Visualization

### 8.1 Use Case: Charging Station Discovery

**Domain Event Flow**
![Search Station Event Flow](docs/diagrams/charging_station_search/SearchStation_Domain_Event_Flow.drawio.png)

**Sequence Diagram**
![Search Station Sequence Diagram](docs/diagrams/charging_station_search/Search_Station_Sequence_Diagram.svg)

### 8.2 Use Case: Malfunction Reporting

**Domain Event Flow**
![Malfunction Report Event Flow](docs/diagrams/malfunction_report/MalfunctionReport_Domain_Event_Flow.drawio.png)

**Sequence Diagram**
![Malfunction Report Sequence Diagram](docs/diagrams/malfunction_report/Station_Malfunction_Report_Sequence_Diagram.svg)

---

## 9. Architecture & Boundaries

The system is architected as a **Modular Monolith** using **Domain-Driven Design (DDD)** and **Clean Architecture** principles. This ensures strict separation of concerns while maintaining the simplicity of a single deployment unit.

### 9.1 Scaffold & Dependency Rule
The code is organized into concentric layers (represented by folders):
1.  **Domain (Inner Layer)**: Contains Aggregates (`ChargingStation`, `MalfunctionReport`), Value Objects (`PostalCode`), Domain Events, and Repository Interfaces. *Depends on nothing.*
2.  **Application (Middle Layer)**: Contains Services (`ChargingStationService`, `MalfunctionService`) that orchestrate domain logic. *Depends only on Domain.*
3.  **Infrastructure (Outer Layer)**: Contains Repository Implementations (`CSVRepository`, `InMemoryRepository`). *Depends on Domain Interfaces.*
4.  **Presentation (Outermost Layer)**: Contains Streamlit Views. *Depends on Application Services.*

### 9.2 Bounded Contexts & Separation
The system is divided into two distinct **Bounded Contexts**, each reflecting a specific subdomain:

#### Context A: `chargehub.discovery`
-   **Responsibility**: Finding and displaying charging stations.
-   **Key Model**: `ChargingStation` (Aggregate Root).
-   **Boundaries**: Completely isolated domain logic for validation and search.

#### Context B: `chargehub.malfunction`
-   **Responsibility**: Reporting issues and managing station health.
-   **Key Model**: `MalfunctionReport` (Aggregate Root).
-   **Boundaries**: Owns the lifecycle of a report (Pending -> Approved).

### 9.3 Communication Between Boundaries
While the contexts are separated, they need to communicate. In our architecture:

1.  **Service-to-Interface Communication**:
    The `MalfunctionService` (Context B) needs to update the status of a station (Context A). It does this strictly via the **Repository Interface** defined in Context A.
    -   *Code*: `MalfunctionService` holds a reference to `ChargingStationRepository` (Interface).
    -   *Logic*: When a report threshold is reached, `MalfunctionService` calls `repo.update_station_status()`.

2.  **Event-Driven Communication (Conceptual)**:
    We use Domain Events (e.g., `StationStatusChangedEvent`) to decouple the side effects.
    -   Current Implementation: The Service generates events for the UI to consume (to show balloons/toasts or update logs).
    -   Future Extension: These events could be published to a bus to allow Context A to react asynchronously without Context B knowing about it.

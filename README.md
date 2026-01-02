# ChargeHub Berlin

ChargeHub Berlin is an interactive platform to streamline the EV charging experience for Berliners by focusing on two core functions:

1) **Charging Station Discovery**: Search charging stations by **postal code** and display **only currently available plugs**.
2) **Station Malfunction Management**: Report malfunctions to improve local charging reliability. When a report-count threshold is reached, the station can be marked unavailable.

This repo follows **DDD (Domain-Driven Design)** and is implemented with **TDD (Test-Driven Development)**.

## Quickstart

### Install
```bash
pip install -r requirements.txt
```

### Run tests
```bash
pytest
```

### Run Streamlit UI
```bash
streamlit run main.py
```

## Project Structure (Bounded Contexts)

- `src/chargehub/discovery/`  → **Charging Station Discovery**
- `src/chargehub/malfunction/` → **Station Malfunction Management**
- `tests/` → pytest test suite (happy path + edge/error cases)
- `data/` → optional datasets (CSV); the app also runs with in-memory demo data.

## Business Rules

### Postal Code (Value Object)
- Numeric only
- Exactly 5 digits
- Starts with 10, 12, or 13 (Berlin area)

### Malfunction Report (Value Object)
- Not empty
- Max 200 characters
- Threshold logic (default): mark station UNAVAILABLE when report count reaches 5

## Bounded Context Communication
**Strategy: Option (2) - Event-Driven Architecture**. 

The Malfunction Context communicates with the Discovery Context by publishing **Domain Events** (e.g., `StationStatusChangedEvent`, `StationRestoredEvent`).

**Why this strategy?**
1.  **Decoupling**: The *Discovery* context (optimized for reading/searching) doesn't need to know the complex internal logic of *Malfunction* (thresholds, duplicate checks, admin workflows). It simply reacts to "Status Changed" facts.
2.  **Scalability**: Writing reports (high write volume potentially) is separated from searching stations (high read volume). In a real system, these could be separate microservices.
3.  **Resilience**: If the Malfunction service goes down, users can still search for stations (even if status updates are delayed).

**Implementation Details**:
- `Service Layer` in Malfunction emits events.
- `Repository Layer` in Discovery accepts status updates.
- In this monolithic prototype, the "Bus" is synchronous for simplicity, but the design boundaries are respected.

## Notes for ASE submission
- Domain events are represented as immutable dataclasses inside `domain/events/`.
- Services orchestrate use cases; repositories isolate data access.
- InMemory repositories are used for simplicity (can be swapped with DB later).

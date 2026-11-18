# Phase 6.5: Kernel Telemetry Tab (`KernelView.tsx` & `TelemetryFeed.tsx`)

## Objective
Provide an unfiltered, high-throughput audit stream of all filesystem events intercepted by the Apple Silicon FSEvents kernel sensor, equipped with search and filtering capabilities.

## Implementation Details
- **Component**: [`frontend/src/components/views/KernelView.tsx`](file:///Users/akhouriprakhar/Downloads/Hack-a-Sol%205.0/frontend/src/components/views/KernelView.tsx)
- **Feed Component**: [`frontend/src/components/TelemetryFeed.tsx`](file:///Users/akhouriprakhar/Downloads/Hack-a-Sol%205.0/frontend/src/components/TelemetryFeed.tsx)
- **Features**:
  - Live ring buffer holding the most recent 100 filesystem events.
  - Quick Category Filters:
    - `ALL`: Complete audit trail.
    - `CANARY`: Honeyfile tripwires only.
    - `HIGH ENTROPY`: Encrypted mutations ($H(X) \ge 7.50$).
    - `WRITES`: `FILE_MODIFY` events.
  - Text Search: Filters by file name, PID, or event type.
  - Clear Stream button to purge in-memory view.

## Verification & Proof
- Verified rapid event ingestion without UI lag or memory leaks.
- Verified search filtering operates instantaneously in-memory.

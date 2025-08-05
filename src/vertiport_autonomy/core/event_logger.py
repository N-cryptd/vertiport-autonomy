import csv
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class EventType(Enum):
    MISSION_STARTED = "mission_started"
    MISSION_COMPLETED = "mission_completed"
    LOS_DETECTED = "los_detected"
    COLLISION_DETECTED = "collision_detected"
    CLEARANCE_GRANTED = "clearance_granted"
    FATO_OCCUPIED = "fato_occupied"
    FATO_VACATED = "fato_vacated"
    HOLDING_POINT_REACHED = "holding_point_reached"
    UNAUTHORIZED_LANDING = "unauthorized_landing"


class EventLogger:
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.filename = f"event_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    def log_event(
        self,
        event_type: EventType,
        drone_id: Optional[int] = None,
        timestamp: Optional[float] = None,
        details: Optional[str] = None,
    ):
        """Logs an event with timestamp and optional details."""
        event = {
            "timestamp": timestamp or datetime.now().timestamp(),
            "event_type": event_type.value,
            "drone_id": drone_id,
            "details": details,
        }
        self.events.append(event)

    def save_to_csv(self):
        """Saves all logged events to a CSV file."""
        if not self.events:
            return

        fieldnames = ["timestamp", "event_type", "drone_id", "details"]
        with open(self.filename, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.events)

    def get_events(self) -> List[Dict[str, Any]]:
        """Returns all logged events."""
        return self.events

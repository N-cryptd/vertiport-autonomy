from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, confloat, conint


class TrafficProfileType(str, Enum):
    STEADY_FLOW = "steady_flow"
    SUDDEN_INFLUX = "sudden_influx"
    PEAK_HOURS = "peak_hours"


class Point3D(BaseModel):
    x: float
    y: float
    z: float


class FATO(BaseModel):
    id: str
    position: Point3D
    approach_path: List[Point3D]


class HoldingPoint(BaseModel):
    id: str
    position: Point3D
    associated_fato: str  # FATO ID this holding point serves


class Gate(BaseModel):
    id: str
    position: Point3D
    is_entry: bool
    is_exit: bool


class TrafficProfile(BaseModel):
    profile_type: TrafficProfileType
    arrival_rate: confloat(gt=0)  # λ for Poisson distribution
    max_drones: conint(gt=0)
    spawn_interval: conint(gt=0)  # Steps between spawn attempts


class VertiportLayout(BaseModel):
    fatos: List[FATO]
    holding_points: List[HoldingPoint]
    gates: List[Gate]
    operational_altitude: confloat(gt=0) = 50.0  # Default altitude


class ScenarioConfig(BaseModel):
    vertiport: VertiportLayout
    traffic: TrafficProfile
    simulation: Dict[str, float] = {
        "time_step": 0.1,
        "drone_speed": 5.0,
        "drone_radius": 0.5,
        "min_separation": 6.0,
    }

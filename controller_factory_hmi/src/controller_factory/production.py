from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
import random
from typing import Deque, Dict, List, Tuple

COMPONENTS = ["PCB", "Buttons", "Shell", "Triggers", "Battery", "Sticks"]
STATIONS = [
    "Component Feed", "PCB Test", "Button Fit", "Shell Press",
    "Trigger Assembly", "Stick Calibration", "Final QC", "Packaging"
]

@dataclass
class ControllerUnit:
    serial: int
    stage: int = 0
    progress: float = 0.0
    defective: bool = False
    issue: str = ""

@dataclass
class FactoryStats:
    produced: int = 0
    passed: int = 0
    rejected: int = 0
    packed: int = 0
    alarms: int = 0
    uptime_ticks: int = 0
    station_counts: Dict[str, int] = field(default_factory=lambda: {s: 0 for s in STATIONS})
    component_stock: Dict[str, int] = field(default_factory=lambda: {c: 25 for c in COMPONENTS})
    component_used: Dict[str, int] = field(default_factory=lambda: {c: 0 for c in COMPONENTS})

class ControllerFactory:
    def __init__(self, seed: int | None = None):
        self.random = random.Random(seed)
        self.serial_counter = 1000
        self.units: Deque[ControllerUnit] = deque()
        self.finished: List[ControllerUnit] = []
        self.rejected: List[ControllerUnit] = []
        self.stats = FactoryStats()
        self.running = True
        self.speed = 1.0
        self.alarm_message = "System OK"
        self.log: Deque[str] = deque(maxlen=9)
        self._spawn_timer = 0

    def reset(self):
        seed = self.random.randint(1, 999999)
        self.__init__(seed=seed)

    def toggle(self):
        self.running = not self.running
        self.alarm_message = "Line paused" if not self.running else "System OK"
        self.log_event("LINE", self.alarm_message)

    def set_speed(self, value: float):
        self.speed = max(0.5, min(3.0, value))

    def log_event(self, station: str, message: str):
        self.log.appendleft(f"{station}: {message}")

    def restock(self):
        for c in COMPONENTS:
            self.stats.component_stock[c] += 20
        self.alarm_message = "Restocked components"
        self.log_event("WAREHOUSE", "all component bins +20")

    def _has_parts(self) -> bool:
        return all(self.stats.component_stock[c] > 0 for c in COMPONENTS)

    def _spawn_unit(self):
        if not self._has_parts():
            self.alarm_message = "ALARM: low component stock"
            self.stats.alarms += 1
            self.log_event("FEED", "cannot start controller, missing parts")
            return
        for c in COMPONENTS:
            self.stats.component_stock[c] -= 1
            self.stats.component_used[c] += 1
        self.serial_counter += 1
        unit = ControllerUnit(serial=self.serial_counter)
        self.units.append(unit)
        self.stats.produced += 1
        self.stats.station_counts[STATIONS[0]] += 1
        self.log_event("FEED", f"controller #{unit.serial} entered line")

    def tick(self):
        if not self.running:
            return
        self.stats.uptime_ticks += 1
        self._spawn_timer += 1
        spawn_every = max(5, int(16 / self.speed))
        if self._spawn_timer >= spawn_every and len(self.units) < 12:
            self._spawn_timer = 0
            self._spawn_unit()

        for unit in list(self.units):
            unit.progress += 0.035 * self.speed
            if unit.progress >= 1.0:
                unit.progress = 0.0
                self._process_station(unit)

    def _process_station(self, unit: ControllerUnit):
        station = STATIONS[unit.stage]
        defect_rates = {
            "PCB Test": 0.04,
            "Button Fit": 0.03,
            "Shell Press": 0.025,
            "Trigger Assembly": 0.035,
            "Stick Calibration": 0.045,
            "Final QC": 0.06,
        }
        if station in defect_rates and self.random.random() < defect_rates[station]:
            unit.defective = True
            unit.issue = f"failed at {station}"
            self.units.remove(unit)
            self.rejected.append(unit)
            self.stats.rejected += 1
            self.stats.alarms += 1
            self.alarm_message = f"Reject #{unit.serial}: {unit.issue}"
            self.log_event(station, self.alarm_message)
            return

        self.stats.station_counts[station] += 1
        if station == "Packaging":
            self.units.remove(unit)
            self.finished.append(unit)
            self.stats.passed += 1
            self.stats.packed += 1
            self.alarm_message = "System OK"
            self.log_event("PACK", f"controller #{unit.serial} boxed")
            return

        unit.stage += 1

    def snapshot(self) -> Dict[str, object]:
        return {
            "units": list(self.units),
            "finished": list(self.finished[-8:]),
            "rejected": list(self.rejected[-8:]),
            "stats": self.stats,
            "running": self.running,
            "speed": self.speed,
            "alarm": self.alarm_message,
            "log": list(self.log),
        }

    def quality_rate(self) -> float:
        total = self.stats.passed + self.stats.rejected
        return 100.0 if total == 0 else (self.stats.passed / total) * 100

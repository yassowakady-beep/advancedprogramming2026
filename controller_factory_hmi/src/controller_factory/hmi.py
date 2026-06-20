from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from pathlib import Path
import sys

# Works when run as: python run_hmi.py, python src/controller_factory/hmi.py, or python -m controller_factory.hmi
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from controller_factory.production import ControllerFactory, COMPONENTS, STATIONS

BG = "#0b1220"
PANEL = "#111827"
PANEL2 = "#172033"
TEXT = "#e5e7eb"
MUTED = "#94a3b8"
GREEN = "#22c55e"
RED = "#ef4444"
YELLOW = "#f59e0b"
BLUE = "#38bdf8"
PURPLE = "#a78bfa"

class ControllerFactoryHMI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Controller Production Line HMI")
        self.geometry("1220x760")
        self.minsize(1050, 680)
        self.configure(bg=BG)
        self.factory = ControllerFactory(seed=42)
        self.station_positions = []
        self._build_layout()
        self.after(80, self._loop)

    def _build_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        top = tk.Frame(self, bg=BG)
        top.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))
        top.columnconfigure(1, weight=1)

        title = tk.Label(top, text="GAME CONTROLLER PRODUCTION LINE", fg=TEXT, bg=BG,
                         font=("Segoe UI", 22, "bold"))
        title.grid(row=0, column=0, sticky="w")
        subtitle = tk.Label(top, text="Live HMI | Stations • Conveyor • Reject Bin • Packaging • Counters", fg=MUTED, bg=BG,
                            font=("Segoe UI", 10))
        subtitle.grid(row=1, column=0, sticky="w")

        controls = tk.Frame(top, bg=BG)
        controls.grid(row=0, column=1, rowspan=2, sticky="e")
        self.btn_run = tk.Button(controls, text="PAUSE", command=self._toggle, bg=YELLOW, fg="#111827",
                                 font=("Segoe UI", 10, "bold"), width=10, relief="flat")
        self.btn_run.pack(side="left", padx=4)
        tk.Button(controls, text="RESET", command=self._reset, bg=PURPLE, fg="#111827",
                  font=("Segoe UI", 10, "bold"), width=10, relief="flat").pack(side="left", padx=4)
        tk.Button(controls, text="RESTOCK", command=self.factory.restock, bg=BLUE, fg="#111827",
                  font=("Segoe UI", 10, "bold"), width=10, relief="flat").pack(side="left", padx=4)
        tk.Label(controls, text="Speed", fg=TEXT, bg=BG).pack(side="left", padx=(16, 4))
        self.speed = tk.DoubleVar(value=1.0)
        tk.Scale(controls, from_=0.5, to=3.0, resolution=0.5, orient="horizontal", variable=self.speed,
                 command=lambda v: self.factory.set_speed(float(v)), length=150, bg=BG, fg=TEXT,
                 troughcolor=PANEL, highlightthickness=0).pack(side="left")

        main = tk.Frame(self, bg=BG)
        main.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=0)
        main.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(main, bg="#0f172a", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.canvas.bind("<Configure>", lambda e: self._draw_static())

        side = tk.Frame(main, bg=BG, width=310)
        side.grid(row=0, column=1, sticky="ns")
        side.grid_propagate(False)

        self.kpi_labels = {}
        self._panel(side, "LINE STATUS", 0)
        for key in ["Produced", "Passed", "Rejected", "Packed", "Quality", "Alarm"]:
            lbl = tk.Label(side, text=f"{key}: --", fg=TEXT, bg=PANEL, anchor="w", font=("Segoe UI", 10, "bold"))
            lbl.pack(fill="x", padx=10, pady=3)
            self.kpi_labels[key] = lbl

        self._panel(side, "COMPONENT STOCK", 1)
        self.stock_labels = {}
        for c in COMPONENTS:
            lbl = tk.Label(side, text=f"{c}: --", fg=TEXT, bg=PANEL, anchor="w", font=("Segoe UI", 10))
            lbl.pack(fill="x", padx=10, pady=2)
            self.stock_labels[c] = lbl

        self._panel(side, "EVENT LOG", 2)
        self.log_box = tk.Text(side, height=10, bg=PANEL, fg=TEXT, insertbackground=TEXT,
                               relief="flat", font=("Consolas", 9), wrap="word")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=(2, 10))

    def _panel(self, parent, title, number):
        frame = tk.Frame(parent, bg=PANEL)
        frame.pack(fill="x", pady=(0 if number == 0 else 12, 0))
        tk.Label(frame, text=title, bg=PANEL, fg=BLUE, font=("Segoe UI", 11, "bold"), anchor="w").pack(fill="x", padx=10, pady=8)

    def _toggle(self):
        self.factory.toggle()
        self.btn_run.config(text="RUN" if not self.factory.running else "PAUSE")

    def _reset(self):
        self.factory.reset()
        self.btn_run.config(text="PAUSE")

    def _draw_static(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100:
            return
        # floor grid
        for x in range(0, w, 40):
            self.canvas.create_line(x, 0, x, h, fill="#132036")
        for y in range(0, h, 40):
            self.canvas.create_line(0, y, w, y, fill="#132036")

        self.canvas.create_text(22, 22, anchor="w", text="Controller Assembly Cell", fill=TEXT, font=("Segoe UI", 16, "bold"))

        y = h * 0.46
        left = 80
        right = w - 80
        self.canvas.create_rectangle(left, y-26, right, y+26, fill="#273449", outline="#3b4a64", width=2)
        for x in range(int(left), int(right), 46):
            self.canvas.create_oval(x, y-18, x+28, y+10, fill="#6b7280", outline="#9ca3af")

        n = len(STATIONS)
        self.station_positions = []
        for i, name in enumerate(STATIONS):
            x = left + i * ((right-left) / (n-1))
            self.station_positions.append((x, y))
            self._draw_station(x, y-105, name, i)

        # bins
        self.canvas.create_rectangle(55, h-145, 220, h-55, fill="#2f1a1a", outline=RED, width=2)
        self.canvas.create_text(137, h-126, text="REJECT BIN", fill=RED, font=("Segoe UI", 12, "bold"))
        self.canvas.create_rectangle(w-240, h-145, w-55, h-55, fill="#10281a", outline=GREEN, width=2)
        self.canvas.create_text(w-148, h-126, text="PACKED GOODS", fill=GREEN, font=("Segoe UI", 12, "bold"))

    def _draw_station(self, x, y, name, index):
        color = [BLUE, PURPLE, GREEN, YELLOW][index % 4]
        self.canvas.create_rectangle(x-58, y-36, x+58, y+36, fill=PANEL2, outline=color, width=2)
        self.canvas.create_rectangle(x-38, y+36, x+38, y+64, fill="#1f2937", outline="#475569")
        self.canvas.create_oval(x-8, y-50, x+8, y-34, fill=color, outline="")
        self.canvas.create_text(x, y-8, text=name, fill=TEXT, font=("Segoe UI", 8, "bold"), width=105)
        self.canvas.create_text(x, y+18, text=f"S{index+1}", fill=MUTED, font=("Segoe UI", 8))

    def _draw_controller(self, x, y, serial, bad=False):
        fill = "#1d4ed8" if not bad else RED
        self.canvas.create_oval(x-22, y-12, x+22, y+12, fill=fill, outline="#dbeafe", width=2)
        self.canvas.create_oval(x-34, y-9, x-10, y+15, fill=fill, outline="#dbeafe", width=2)
        self.canvas.create_oval(x+10, y-9, x+34, y+15, fill=fill, outline="#dbeafe", width=2)
        self.canvas.create_oval(x-9, y-3, x-3, y+3, fill="#111827", outline="")
        self.canvas.create_oval(x+3, y-3, x+9, y+3, fill="#111827", outline="")
        self.canvas.create_text(x, y+27, text=f"#{serial}", fill=TEXT, font=("Consolas", 8, "bold"))

    def _render_dynamic(self):
        self.canvas.delete("dynamic")
        if not self.station_positions:
            return
        snap = self.factory.snapshot()
        for unit in snap["units"]:
            sx, sy = self.station_positions[unit.stage]
            if unit.stage < len(self.station_positions)-1:
                nx, ny = self.station_positions[unit.stage+1]
                x = sx + (nx-sx) * unit.progress
            else:
                x = sx + 40 * unit.progress
            self._draw_controller_tagged(x, sy, unit.serial, unit.defective)

        w = self.canvas.winfo_width(); h = self.canvas.winfo_height()
        self.canvas.create_text(137, h-93, text=str(self.factory.stats.rejected), fill=TEXT, font=("Segoe UI", 24, "bold"), tags="dynamic")
        self.canvas.create_text(w-148, h-93, text=str(self.factory.stats.packed), fill=TEXT, font=("Segoe UI", 24, "bold"), tags="dynamic")
        alarm = snap["alarm"]
        alarm_color = RED if "ALARM" in alarm or "Reject" in alarm else GREEN if alarm == "System OK" else YELLOW
        self.canvas.create_rectangle(22, 52, min(w-22, 560), 88, fill="#111827", outline=alarm_color, width=2, tags="dynamic")
        self.canvas.create_text(35, 70, anchor="w", text=alarm, fill=alarm_color, font=("Segoe UI", 12, "bold"), tags="dynamic")

    def _draw_controller_tagged(self, x, y, serial, bad=False):
        # same as _draw_controller but with tag so it can animate cleanly
        fill = "#1d4ed8" if not bad else RED
        for item in [
            self.canvas.create_oval(x-22, y-12, x+22, y+12, fill=fill, outline="#dbeafe", width=2, tags="dynamic"),
            self.canvas.create_oval(x-34, y-9, x-10, y+15, fill=fill, outline="#dbeafe", width=2, tags="dynamic"),
            self.canvas.create_oval(x+10, y-9, x+34, y+15, fill=fill, outline="#dbeafe", width=2, tags="dynamic"),
            self.canvas.create_oval(x-9, y-3, x-3, y+3, fill="#111827", outline="", tags="dynamic"),
            self.canvas.create_oval(x+3, y-3, x+9, y+3, fill="#111827", outline="", tags="dynamic"),
            self.canvas.create_text(x, y+27, text=f"#{serial}", fill=TEXT, font=("Consolas", 8, "bold"), tags="dynamic")
        ]:
            pass

    def _update_side(self):
        s = self.factory.stats
        q = self.factory.quality_rate()
        values = {
            "Produced": s.produced,
            "Passed": s.passed,
            "Rejected": s.rejected,
            "Packed": s.packed,
            "Quality": f"{q:.1f}%",
            "Alarm": s.alarms,
        }
        for k, v in values.items():
            self.kpi_labels[k].config(text=f"{k}: {v}")
        for c in COMPONENTS:
            stock = s.component_stock[c]
            color = RED if stock <= 3 else YELLOW if stock <= 8 else TEXT
            self.stock_labels[c].config(text=f"{c}: {stock} left", fg=color)
        self.log_box.delete("1.0", "end")
        for line in self.factory.log:
            self.log_box.insert("end", line + "\n")

    def _loop(self):
        self.factory.tick()
        self._render_dynamic()
        self._update_side()
        self.after(80, self._loop)

def main():
    app = ControllerFactoryHMI()
    app.mainloop()

if __name__ == "__main__":
    main()

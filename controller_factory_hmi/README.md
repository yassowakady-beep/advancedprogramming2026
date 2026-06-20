# Controller Production Line HMI

This is a standalone working production-line simulation for a game controller factory.

## What it includes

- Real HMI window using Tkinter
- Production line conveyor
- Component feed station
- PCB test station
- Button fitting station
- Shell press station
- Trigger assembly station
- Stick calibration station
- Final quality control
- Packaging station
- Reject bin and packed goods bin
- Live counters, stock levels, alarms, and event log

## How to run

### Option 1: double click
Double click:

```text
run_hmi.bat
```

### Option 2: PowerShell
Open PowerShell inside this folder and run:

```powershell
python run_hmi.py
```

If `python` does not work, use:

```powershell
py run_hmi.py
```

## Important

Do not run files from inside `src` manually. Use `run_hmi.py` or `run_hmi.bat`.
This version does not use relative imports, so it avoids the old error:

```text
ImportError: attempted relative import with no known parent package
```

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from controller_factory.hmi import main

if __name__ == "__main__":
    main()

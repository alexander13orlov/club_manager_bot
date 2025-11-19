import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

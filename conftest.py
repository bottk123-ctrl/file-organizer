import sys
from pathlib import Path

# Тесты запускаются из корня проекта без установки пакета.
sys.path.insert(0, str(Path(__file__).resolve().parent))

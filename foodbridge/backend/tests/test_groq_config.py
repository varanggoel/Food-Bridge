import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_env_file_is_loaded_from_backend_directory():
    if 'app.config' in sys.modules:
        del sys.modules['app.config']

    os.chdir(Path(__file__).resolve().parents[1])
    from app.config import settings

    assert hasattr(settings, 'GEMINI_MODEL')
    assert settings.GEMINI_MODEL

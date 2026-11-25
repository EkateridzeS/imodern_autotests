import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')
DATA = json.loads((ROOT / 'data/cases.json').read_text(encoding='utf-8'))

@dataclass(frozen=True)
class Config:
    base_url: str = os.getenv('BASE_URL', 'https://imodern.ru').rstrip('/')
    auth_path: str = os.getenv('AUTH_PATH', '/personal/profile/')
    profile_path: str = os.getenv('PROFILE_PATH', '/personal/profile/')
    browser: str = os.getenv('BROWSER', 'chromium')
    headless: bool = os.getenv('HEADLESS', 'false').lower() == 'true'
    timeout: int = int(os.getenv('TIMEOUT_MS', '15000'))
    email: str = field(default_factory=lambda: os.getenv('TEST_EMAIL', ''), repr=False)
    password: str = field(default_factory=lambda: os.getenv('TEST_PASSWORD', ''), repr=False)
    name: str = field(default_factory=lambda: os.getenv('TEST_NAME', ''), repr=False)
    phone: str = field(default_factory=lambda: os.getenv('TEST_PHONE', ''), repr=False)
    allow_order: bool = os.getenv('ALLOW_ORDER', 'false').lower() == 'true' and os.getenv('ORDER_APPROVED', 'false').lower() == 'true'

CONFIG = Config()

import base64
import json
from abc import ABC

from services.auth.abc_auth import AbstractAuthService


class BaseAuthService(AbstractAuthService, ABC):
    @staticmethod
    def encode_fingerprint(fingerprint: dict) -> str:
        fingerprint_json = json.dumps(fingerprint)
        fingerprint_base64 = base64.b64encode(fingerprint_json.encode()).decode()
        return fingerprint_base64

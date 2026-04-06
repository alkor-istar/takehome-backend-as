import json
import hashlib


def generate_etag(data: str) -> str:
    payload = json.dumps(data, sort_keys=True).encode()
    return hashlib.md5(payload).hexdigest()

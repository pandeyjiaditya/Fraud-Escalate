import hashlib
import hmac
from config import SECRET_KEY


def hash_data(text: str):

    return hmac.new(
        SECRET_KEY.encode(),
        text.encode(),
        hashlib.sha256
    ).hexdigest()
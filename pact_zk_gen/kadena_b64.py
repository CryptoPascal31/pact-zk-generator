import base64

def _ensure_bytes(x):
    if isinstance(x, str):
        return x.encode('ascii')
    return x

def b64_encode(data):
    data = _ensure_bytes(data)
    encoded = base64.urlsafe_b64encode(data).rstrip(b'=')
    return encoded.decode('ascii')

_PADDING_TABLE = [b"", b"===", b"==", b"="]

def b64_decode(data):
    data = _ensure_bytes(data)
    padding = _PADDING_TABLE[len(data)%4]
    return base64.urlsafe_b64decode(data+padding)

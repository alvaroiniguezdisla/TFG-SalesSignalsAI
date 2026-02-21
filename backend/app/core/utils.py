import hashlib

def hash_url(url: str) -> str:
    """Crea una huella digital para cada URL para evitar duplicados."""
    return hashlib.md5(url.encode('utf-8')).hexdigest()

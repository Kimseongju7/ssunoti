from urllib.parse import urlencode


def build_url(base_url: str, params: dict) -> str:
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}{urlencode(params)}"

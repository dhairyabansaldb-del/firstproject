import json
from functools import lru_cache
from pathlib import Path
from typing import Any


class CatalogLoadError(FileNotFoundError):
    pass


@lru_cache(maxsize=1)
def load_catalog(catalog_file: str) -> list[dict[str, Any]]:
    path = Path(catalog_file)
    if not path.exists():
        raise CatalogLoadError(f"Catalog file not found at: {path}")
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, list):
        raise ValueError("Catalog format invalid: expected JSON list.")
    return payload

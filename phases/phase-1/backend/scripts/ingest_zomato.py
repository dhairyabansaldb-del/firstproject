import hashlib
import json
from pathlib import Path
from typing import Any, Optional

from datasets import load_dataset

SOURCE_DATASET = "ManikaSaini/zomato-restaurant-recommendation"
OUTPUT_PATH = Path("phases/phase-1/backend/data/restaurants.normalized.json")


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "")
        if "/" in cleaned:
            cleaned = cleaned.split("/", maxsplit=1)[0]
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _to_int(value: Any) -> Optional[int]:
    parsed = _to_float(value)
    if parsed is None:
        return None
    return int(parsed)


def _extract_first(row: dict[str, Any], candidate_keys: list[str]) -> Any:
    for key in candidate_keys:
        if key in row and row[key] not in (None, ""):
            return row[key]
    return None


def _normalize_cuisines(raw_value: Any) -> list[str]:
    if raw_value is None:
        return []
    if isinstance(raw_value, list):
        tokens = raw_value
    else:
        text = str(raw_value)
        for separator in ["/", "|", ";"]:
            text = text.replace(separator, ",")
        tokens = [t.strip() for t in text.split(",")]
    cleaned: list[str] = []
    seen: set[str] = set()
    for token in tokens:
        if not token:
            continue
        canonical = token.title().strip()
        key = canonical.lower()
        if key not in seen:
            seen.add(key)
            cleaned.append(canonical)
    return cleaned


import re

def _build_restaurant_id(name: str, city: str, location: str) -> str:
    n = re.sub(r'[^a-z0-9]', '', name.lower())
    c = re.sub(r'[^a-z0-9]', '', city.lower())
    l = re.sub(r'[^a-z0-9]', '', location.lower())
    digest = hashlib.sha1(f"{n}|{c}|{l}".encode("utf-8")).hexdigest()
    return digest[:16]


def normalize_row(row: dict[str, Any]) -> Optional[dict[str, Any]]:
    name = _extract_first(row, ["restaurant_name", "name", "Restaurant Name", "res_name"])
    city = _extract_first(row, ["city", "City", "listed_in(city)"])
    location = _extract_first(row, ["location", "Locality", "address"])
    cuisines_raw = _extract_first(row, ["cuisines", "Cuisine", "cuisine"])
    rating_raw = _extract_first(
        row, ["rating", "aggregate_rating", "Aggregate rating", "rate"]
    )
    votes_raw = _extract_first(row, ["votes", "Votes"])
    cost_raw = _extract_first(
        row,
        [
            "average_cost_for_two",
            "Average Cost for two",
            "avg_cost_for_two",
            "cost_for_two",
            "approx_cost(for two people)",
        ],
    )
    currency = _extract_first(row, ["currency", "Currency"])

    if not name or not city:
        return None

    name = str(name).strip()
    city = str(city).strip().title()
    location = str(location).strip() if location else city

    cuisines = _normalize_cuisines(cuisines_raw)
    rating = _to_float(rating_raw)
    if rating is not None and (rating < 0 or rating > 5):
        rating = None

    record = {
        "restaurant_id": _build_restaurant_id(name=name, city=city, location=location),
        "name": name,
        "location": location,
        "city": city,
        "cuisines": cuisines,
        "average_cost_for_two": _to_float(cost_raw),
        "currency": str(currency).strip() if currency else None,
        "rating": rating,
        "votes": _to_int(votes_raw),
        "source_dataset": SOURCE_DATASET,
    }
    return record


def run_ingestion() -> None:
    print(f"Loading dataset: {SOURCE_DATASET}")
    dataset = load_dataset(SOURCE_DATASET)

    if "train" in dataset:
        rows = dataset["train"]
    else:
        split_name = next(iter(dataset.keys()))
        rows = dataset[split_name]

    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    dropped_missing = 0
    dropped_duplicates = 0

    for row in rows:
        record = normalize_row(dict(row))
        if record is None:
            dropped_missing += 1
            continue
        if record["restaurant_id"] in seen_ids:
            dropped_duplicates += 1
            continue
        seen_ids.add(record["restaurant_id"])
        normalized.append(record)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(normalized, file, indent=2, ensure_ascii=True)

    print(f"Saved normalized catalog: {OUTPUT_PATH}")
    print(f"Total kept: {len(normalized)}")
    print(f"Dropped missing required fields: {dropped_missing}")
    print(f"Dropped duplicates: {dropped_duplicates}")


if __name__ == "__main__":
    run_ingestion()

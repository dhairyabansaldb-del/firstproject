import hashlib
import json
from pathlib import Path
from typing import Any, Optional

from datasets import load_dataset

SOURCE_DATASET = "ManikaSaini/zomato-restaurant-recommendation"
CATALOG_OUTPUT_PATH = Path("phases/phase-2/backend/data/restaurants.normalized.json")
REPORT_OUTPUT_PATH = Path("phases/phase-2/backend/data/ingestion.report.json")


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


def _extract_first(row: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return row[key]
    return None


def _normalize_cuisines(raw_value: Any) -> list[str]:
    if raw_value is None:
        return []
    text = str(raw_value)
    for sep in ["/", "|", ";"]:
        text = text.replace(sep, ",")
    parts = [part.strip() for part in text.split(",")]
    normalized: list[str] = []
    seen: set[str] = set()
    for part in parts:
        if not part:
            continue
        canonical = part.title()
        k = canonical.lower()
        if k not in seen:
            seen.add(k)
            normalized.append(canonical)
    return normalized


def _build_restaurant_id(name: str, city: str, location: str) -> str:
    hash_input = f"{name}|{city}|{location}"
    return hashlib.sha1(hash_input.encode("utf-8")).hexdigest()[:16]


def normalize_row(row: dict[str, Any]) -> tuple[Optional[dict[str, Any]], bool]:
    name = _extract_first(row, ["name", "restaurant_name", "Restaurant Name"])
    city = _extract_first(row, ["city", "City", "listed_in(city)"])
    location = _extract_first(row, ["location", "Locality", "address"])
    cuisines_raw = _extract_first(row, ["cuisines", "Cuisine", "cuisine"])
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
    rating_raw = _extract_first(
        row, ["rating", "aggregate_rating", "Aggregate rating", "rate"]
    )
    votes_raw = _extract_first(row, ["votes", "Votes"])
    currency = _extract_first(row, ["currency", "Currency"])

    if not name or not city:
        return None, False

    name_s = str(name).strip()
    city_s = str(city).strip().title()
    location_s = str(location).strip() if location else city_s
    cuisines = _normalize_cuisines(cuisines_raw)

    rating = _to_float(rating_raw)
    invalid_rating = bool(rating is not None and (rating < 0.0 or rating > 5.0))
    if invalid_rating:
        rating = None

    record = {
        "restaurant_id": _build_restaurant_id(name_s, city_s, location_s),
        "name": name_s,
        "location": location_s,
        "city": city_s,
        "cuisines": cuisines,
        "average_cost_for_two": _to_float(cost_raw),
        "currency": str(currency).strip() if currency else None,
        "rating": rating,
        "votes": _to_int(votes_raw),
        "source_dataset": SOURCE_DATASET,
    }
    return record, invalid_rating


def run_ingestion() -> None:
    print(f"Loading dataset: {SOURCE_DATASET}")
    dataset = load_dataset(SOURCE_DATASET)
    rows = dataset["train"] if "train" in dataset else dataset[next(iter(dataset.keys()))]

    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    dropped_missing_required = 0
    dropped_duplicates = 0
    dropped_invalid_rating = 0

    for row in rows:
        record, invalid_rating = normalize_row(dict(row))
        if record is None:
            dropped_missing_required += 1
            continue
        if invalid_rating:
            dropped_invalid_rating += 1
        rid = record["restaurant_id"]
        if rid in seen_ids:
            dropped_duplicates += 1
            continue
        seen_ids.add(rid)
        normalized.append(record)

    CATALOG_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CATALOG_OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(normalized, file, indent=2, ensure_ascii=True)

    report = {
        "source_dataset": SOURCE_DATASET,
        "total_input_rows": len(rows),
        "total_kept_rows": len(normalized),
        "dropped_missing_required": dropped_missing_required,
        "dropped_duplicates": dropped_duplicates,
        "dropped_invalid_rating": dropped_invalid_rating,
    }
    with REPORT_OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=True)

    print(f"Saved normalized catalog: {CATALOG_OUTPUT_PATH}")
    print(f"Saved ingestion report: {REPORT_OUTPUT_PATH}")
    print(f"Total kept: {len(normalized)}")
    print(f"Dropped missing required: {dropped_missing_required}")
    print(f"Dropped duplicates: {dropped_duplicates}")
    print(f"Dropped invalid rating: {dropped_invalid_rating}")


if __name__ == "__main__":
    run_ingestion()

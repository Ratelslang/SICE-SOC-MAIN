#!/usr/bin/env python3
"""SICE SOC MAIN to War Room bridge.

Runs on the Linux SICE host. It reads the existing server-side SOC MAIN mirror
and sends only changed snapshots to the protected War Room webhook.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WEBHOOK_URL = os.environ.get("SICE_WAR_ROOM_WEBHOOK_URL", "").strip()
API_KEY = os.environ.get("SICE_WAR_ROOM_API_KEY", "").strip()
STATUS_FILE = Path(os.environ.get("SICE_SOC_MAIN_STATUS_FILE", "data/soc_main/status.json"))


def load_status(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"incidents": [], "threats": [], "movements": [], "comms": {}, "updated_at": None}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("SOC MAIN status mirror must contain a JSON object")
    return data


def text(value: Any, fallback: str = "") -> str:
    return value.strip() if isinstance(value, str) and value.strip() else fallback


def stable_id(category: str, record: dict[str, Any], index: int) -> str:
    source_id = text(record.get("id") or record.get("ref") or record.get("uuid"))
    if source_id:
        return f"{category}:{source_id}"
    digest = hashlib.sha256(json.dumps(record, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:24]
    return f"{category}:{index}:{digest}"


def event_timestamp(record: dict[str, Any], fallback: Any) -> str | None:
    raw = text(record.get("occurredAt") or record.get("timestamp") or record.get("ts") or fallback)
    if raw:
        return raw
    if text(record.get("date")):
        return f"{record['date']}T{text(record.get('time'), '00:00')}:00"
    return None


def normalise_records(status: dict[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    updated_at = status.get("updated_at")

    def records_for(category: str) -> list[dict[str, Any]]:
        records = status.get(category, [])
        return [record for record in records if isinstance(record, dict)] if isinstance(records, list) else []

    def building_code(record: dict[str, Any]) -> str:
        warehouse = text(record.get("wh") or record.get("building")).lower()
        return {"sic": "sice", "sice": "sice", "aps": "aps", "u13": "unit13", "unit13": "unit13"}.get(warehouse, "sice")

    for index, record in enumerate(records_for("activity_log")):
        events.append({
            "externalId": stable_id("activity", record, index),
            "eventType": "activity",
            "occurredAt": event_timestamp(record, updated_at),
            "actor": text(record.get("actor") or record.get("by"), "SICE SOC MAIN"),
            "data": {
                "module": text(record.get("module") or record.get("page"), "SOC MAIN"),
                "summary": text(record.get("summary") or record.get("msg"), "SOC MAIN activity update"),
                "type": text(record.get("type") or record.get("severity"), "info"),
                "zoneCode": text(record.get("ref_id") or record.get("location") or record.get("loc"), "fire-safety"),
            },
        })

    for category in ("incidents", "threats", "movements"):
        for index, record in enumerate(records_for(category)):
            summary = text(record.get("summary") or record.get("desc") or record.get("type"), f"SOC MAIN {category[:-1]} update")
            events.append({
                "externalId": stable_id(category, record, index),
                "eventType": "activity",
                "occurredAt": event_timestamp(record, updated_at),
                "actor": text(record.get("by") or record.get("officer"), "SICE SOC MAIN"),
                "data": {
                    "module": "SOC MAIN",
                    "summary": summary,
                    "type": "incident" if category == "incidents" else text(record.get("severity") or record.get("level") or record.get("status"), "info"),
                    "zoneCode": text(record.get("zoneCode") or record.get("location") or record.get("loc"), "fire-safety"),
                },
            })

    for index, record in enumerate(records_for("patrols")):
        events.append({
            "externalId": stable_id("patrol", record, index),
            "eventType": "patrol",
            "occurredAt": event_timestamp(record, updated_at),
            "actor": text(record.get("officer") or record.get("by"), "SICE SOC MAIN"),
            "data": {"building": building_code(record), "zoneCode": text(record.get("location") or record.get("loc"), "fire-safety"), "checkpoint": text(record.get("checkpoint") or record.get("route"), "SOC MAIN patrol checkpoint"), "notes": text(record.get("notes") or record.get("result"))},
        })

    for index, record in enumerate(records_for("hazards")):
        events.append({
            "externalId": stable_id("hazard", record, index),
            "eventType": "hazard",
            "occurredAt": event_timestamp(record, updated_at),
            "actor": text(record.get("by") or record.get("reportedBy"), "SICE SOC MAIN"),
            "data": {"building": building_code(record), "zoneCode": text(record.get("location") or record.get("loc"), "fire-safety"), "title": text(record.get("desc") or record.get("title"), "SOC MAIN hazard"), "severity": text(record.get("risk") or record.get("severity"), "medium"), "mitigation": text(record.get("mitigation"))},
        })

    for index, record in enumerate(records_for("inspections")):
        passed = record.get("overallPass")
        events.append({
            "externalId": stable_id("inspection", record, index),
            "eventType": "inspection",
            "occurredAt": event_timestamp(record, updated_at),
            "actor": text(record.get("inspector") or record.get("by"), "SICE SOC MAIN"),
            "data": {"building": building_code(record), "zoneCode": text(record.get("location") or record.get("loc"), "fire-safety"), "result": "clear" if passed is True else "fail", "notes": text(record.get("overallNotes") or record.get("notes"))},
        })

    for index, record in enumerate(records_for("key_assets")):
        raw_status = text(record.get("status"), "in").lower()
        events.append({
            "externalId": stable_id("key_asset", record, index),
            "eventType": "key_asset",
            "occurredAt": event_timestamp(record, updated_at),
            "actor": text(record.get("by") or record.get("officer"), "SICE SOC MAIN"),
            "data": {"assetCode": text(record.get("ref") or record.get("assetCode") or record.get("id"), f"SOC-KEY-{index + 1}"), "label": text(record.get("name") or record.get("label"), "SOC MAIN key asset"), "area": text(record.get("location") or record.get("loc")), "status": "out" if raw_status in ("out", "issued", "checked_out") else "in", "currentHolder": text(record.get("to") or record.get("holder"))},
        })
    return events


def post_batch(events: list[dict[str, Any]]) -> dict[str, Any]:
    if not WEBHOOK_URL or not API_KEY:
        raise RuntimeError("Set SICE_WAR_ROOM_WEBHOOK_URL and SICE_WAR_ROOM_API_KEY in the systemd environment file")
    body = json.dumps({"source": "sice-soc-main", "events": events}).encode("utf-8")
    request = urllib.request.Request(
        WEBHOOK_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-SICE-API-Key": API_KEY,
            "User-Agent": "SICE-SOC-MAIN-Bridge/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
        if not payload.get("ok"):
            raise RuntimeError(payload.get("error", "War Room rejected the sync batch"))
        return payload


def sync_once(status_file: Path) -> int:
    status = load_status(status_file)
    events = normalise_records(status)
    if not events:
        print("No SOC MAIN incident, threat, or movement records to synchronize.")
        return 0
    response = post_batch(events)
    processed = sum(1 for result in response.get("results", []) if result.get("status") == "processed")
    duplicates = sum(1 for result in response.get("results", []) if result.get("status") == "duplicate")
    print(f"SOC MAIN sync accepted: {processed} processed, {duplicates} already synchronized.")
    return 0


def watch(status_file: Path, interval: float) -> int:
    previous_marker: tuple[int, int] | None = None
    while True:
        try:
            stat = status_file.stat()
            marker = (stat.st_mtime_ns, stat.st_size)
            if marker != previous_marker:
                sync_once(status_file)
                previous_marker = marker
        except FileNotFoundError:
            print(f"Waiting for SOC MAIN status mirror: {status_file}", file=sys.stderr)
        except (OSError, ValueError, urllib.error.URLError, urllib.error.HTTPError, RuntimeError) as error:
            print(f"SOC MAIN sync warning: {error}", file=sys.stderr)
        time.sleep(interval)


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchronize the Linux SOC MAIN status mirror with SICE War Room")
    parser.add_argument("--status-file", type=Path, default=STATUS_FILE)
    parser.add_argument("--watch", action="store_true", help="Watch for local status-file changes and synchronize them")
    parser.add_argument("--interval", type=float, default=2.0, help="Local file check interval in seconds when watching")
    args = parser.parse_args()
    if args.watch:
        return watch(args.status_file, max(0.5, args.interval))
    return sync_once(args.status_file)


if __name__ == "__main__":
    raise SystemExit(main())

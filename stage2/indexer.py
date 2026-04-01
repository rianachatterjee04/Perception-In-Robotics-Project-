from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS object_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_filename TEXT NOT NULL,
    json_filename TEXT NOT NULL,
    object_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    color TEXT,
    size TEXT,
    location TEXT,
    attributes_json TEXT NOT NULL,
    boundaries_json TEXT NOT NULL,
    confidence REAL NOT NULL,
    position_x REAL,
    position_y REAL,
    orientation_yaw REAL,
    sequence_number INTEGER,
    object_text TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_object_type ON object_index(type);
CREATE INDEX IF NOT EXISTS idx_object_image ON object_index(image_filename);
"""


def iter_detection_files(detection_dir: Path) -> Iterable[Path]:
    yield from sorted(detection_dir.glob("*_detected.json"))


def build_index(detection_dir: Path, db_path: Path) -> int:
    detection_dir = Path(detection_dir)
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript(SCHEMA_SQL)
    cur.execute("DELETE FROM object_index")

    row_count = 0
    for json_path in iter_detection_files(detection_dir):
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        base_metadata = {
            "image_filename": payload.get("image_filename", json_path.name.replace("_detected.json", ".jpg")),
            "json_filename": json_path.name,
            "position_x": payload.get("position_x"),
            "position_y": payload.get("position_y"),
            "orientation_yaw": payload.get("orientation_yaw"),
            "sequence_number": payload.get("sequence_number"),
        }
        for obj in payload.get("objects_detected", []):
            attributes = obj.get("attributes", {}) or {}
            boundaries = obj.get("boundaries", {}) or {}
            object_text = " ".join(
                str(x) for x in [
                    obj.get("type", ""),
                    attributes.get("description", ""),
                    attributes.get("color", ""),
                    attributes.get("size", ""),
                    attributes.get("location", ""),
                ] if x
            )
            cur.execute(
                """
                INSERT INTO object_index (
                    image_filename, json_filename, object_id, type, description, color, size, location,
                    attributes_json, boundaries_json, confidence, position_x, position_y,
                    orientation_yaw, sequence_number, object_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    base_metadata["image_filename"],
                    base_metadata["json_filename"],
                    obj.get("object_id"),
                    obj.get("type"),
                    attributes.get("description"),
                    attributes.get("color"),
                    attributes.get("size"),
                    attributes.get("location"),
                    json.dumps(attributes),
                    json.dumps(boundaries),
                    float(obj.get("confidence", 0.0)),
                    base_metadata["position_x"],
                    base_metadata["position_y"],
                    base_metadata["orientation_yaw"],
                    base_metadata["sequence_number"],
                    object_text,
                ),
            )
            row_count += 1

    conn.commit()
    conn.close()
    return row_count

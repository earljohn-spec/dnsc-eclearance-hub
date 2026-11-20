import csv
import json
import xml.etree.ElementTree as ET
from io import StringIO
from typing import Dict, Any, List
from app.database import get_db_connection
from app.models.schemas import HoldType, HoldStatus

def parse_csv_data(content_str: str) -> List[Dict[str, Any]]:
    reader = csv.DictReader(StringIO(content_str))
    return [row for row in reader]

def parse_json_data(content_str: str) -> List[Dict[str, Any]]:
    data = json.loads(content_str)
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "records" in data:
        return data["records"]
    return [data]

def parse_xml_data(content_str: str) -> List[Dict[str, Any]]:
    root = ET.fromstring(content_str)
    records = []
    for elem in root.findall(".//record"):
        item = {}
        for child in elem:
            item[child.tag] = child.text
        records.append(item)
    return records

def process_import_file(
    source_system: str,
    file_bytes: bytes,
    filename: str,
    imported_by: str
) -> Dict[str, Any]:
    content_str = file_bytes.decode("utf-8")
    ext = filename.split(".")[-1].lower()

    if ext == "csv":
        rows = parse_csv_data(content_str)
    elif ext == "json":
        rows = parse_json_data(content_str)
    elif ext == "xml":
        rows = parse_xml_data(content_str)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

    successful = 0
    failed = 0
    errors = []

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        for idx, row in enumerate(rows, start=1):
            try:
                student_id = row.get("student_id") or row.get("studentNo") or row.get("id")
                hold_type = row.get("hold_type") or row.get("type") or HoldType.ACADEMIC.value
                description = row.get("description") or row.get("reason") or "Institutional clearance hold"
                
                raw_amount = str(row.get("amount_due") or row.get("amount") or "0").replace(",", "").strip()
                amount_due = float(raw_amount) if raw_amount else 0.0

                if not student_id:
                    raise ValueError("Missing required student identifier")

                cursor.execute(
                    """
                    INSERT INTO clearance_holds (student_id, source_system, hold_type, description, amount_due, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (student_id, source_system, hold_type, description, amount_due, HoldStatus.ACTIVE.value),
                )
                successful += 1
            except Exception as e:
                failed += 1
                errors.append({"row": idx, "data": row, "error": str(e)})

        cursor.execute(
            """
            INSERT INTO import_logs (source_system, records_processed, records_successful, records_failed, errors_json, imported_by)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (source_system, len(rows), successful, failed, json.dumps(errors), imported_by),
        )

        conn.commit()
    except Exception as fatal_e:
        conn.rollback()
        raise fatal_e
    finally:
        conn.close()

    return {
        "source_system": source_system,
        "total": len(rows),
        "successful": successful,
        "failed": failed,
        "errors": errors,
    }

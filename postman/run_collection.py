"""Postman Collection Automated Test Runner for PayPilot.

Parses postman/PayPilot.postman_collection.json and validates all endpoints
using FastAPI TestClient or live HTTP server.
"""

import json
import os
import sys
from typing import Any, Dict, List
from fastapi.testclient import TestClient

# Ensure backend package is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.main import app


def run_postman_collection(collection_path: str) -> bool:
    """Execute all items in the Postman collection against FastAPI TestClient."""
    with open(collection_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    client = TestClient(app)
    env: Dict[str, Any] = {
        "baseUrl": "",
        "test_product_id": "prod_1",
    }

    total_requests = 0
    passed_requests = 0
    failures: List[str] = []

    def process_items(items: list):
        nonlocal total_requests, passed_requests
        for item in items:
            if "item" in item:
                print(f"\n📂 Folder: {item['name']}")
                process_items(item["item"])
            elif "request" in item:
                total_requests += 1
                req = item["request"]
                method = req["method"]
                url_raw = req["url"]["raw"]
                
                # Replace template variables
                url = url_raw.replace("{{baseUrl}}", "")
                for k, v in env.items():
                    url = url.replace(f"{{{{{k}}}}}", str(v))

                body = None
                if "body" in req and req["body"].get("mode") == "raw":
                    body_raw = req["body"]["raw"]
                    for k, v in env.items():
                        body_raw = body_raw.replace(f"{{{{{k}}}}}", str(v))
                    try:
                        body = json.loads(body_raw)
                    except Exception:
                        body = None

                headers = {}
                for h in req.get("header", []):
                    headers[h["key"]] = h["value"]

                # Add auth header for demo user isolation
                headers["x-demo-user-id"] = "user_postman_test"

                try:
                    if method == "GET":
                        resp = client.get(url, headers=headers)
                    elif method == "POST":
                        resp = client.post(url, json=body, headers=headers)
                    elif method == "PUT":
                        resp = client.put(url, json=body, headers=headers)
                    elif method == "DELETE":
                        resp = client.delete(url, headers=headers)
                    else:
                        resp = client.request(method, url, headers=headers)

                    if resp.status_code in (200, 201, 202):
                        passed_requests += 1
                        print(f"  ✓ [{resp.status_code}] {item['name']} ({method} {url})")
                        # Capture environment variables if present
                        res_json = resp.json()
                        if isinstance(res_json, dict) and "items" in res_json and len(res_json["items"]) > 0:
                            env["test_product_id"] = res_json["items"][0]["id"]
                        elif isinstance(res_json, list) and len(res_json) > 0:
                            env["test_product_id"] = res_json[0]["id"]
                    else:
                        fail_msg = f"  ✗ [{resp.status_code}] {item['name']} ({method} {url}) - Response: {resp.text}"
                        print(fail_msg)
                        failures.append(fail_msg)
                except Exception as exc:
                    fail_msg = f"  ✗ [EXC] {item['name']} ({method} {url}) - Error: {exc}"
                    print(fail_msg)
                    failures.append(fail_msg)

    process_items(data.get("item", []))

    print("\n" + "=" * 60)
    print(f"Postman Collection Execution: {passed_requests}/{total_requests} Passed.")
    print("=" * 60)

    if failures:
        print("\nFailures:")
        for f in failures:
            print(f)
        return False
    return True


if __name__ == "__main__":
    col_path = os.path.join(os.path.dirname(__file__), "PayPilot.postman_collection.json")
    success = run_postman_collection(col_path)
    sys.exit(0 if success else 1)


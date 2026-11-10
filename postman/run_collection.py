"""Postman Collection Automated Test Runner for PayPilot.

Parses postman/PayPilot.postman_collection.json and validates all endpoints
using FastAPI TestClient, evaluating pm.test assertions against live responses.
"""

import json
import os
import re
import sys
from typing import Any, Dict, List, Tuple
from fastapi.testclient import TestClient

# Ensure backend package is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.main import app


def evaluate_pm_tests(script_lines: List[str], resp: Any) -> Tuple[int, int, List[str]]:
    """Parse and execute pm.test assertions from Postman test script against HTTP response."""
    full_script = "\n".join(script_lines)
    test_matches = re.findall(r"pm\.test\(\s*['\"]([^'\"]+)['\"]\s*,\s*function\s*\(\)\s*\{([^}]+)\}\s*\);?", full_script)

    passed = 0
    total = len(test_matches)
    errors: List[str] = []

    res_json = None
    try:
        res_json = resp.json()
    except Exception:
        res_json = None

    for test_name, test_body in test_matches:
        test_ok = True
        err_msg = ""

        # Status code check
        status_match = re.search(r"pm\.response\.to\.have\.status\((\d+)\)", test_body)
        if status_match:
            expected_status = int(status_match.group(1))
            if resp.status_code != expected_status:
                test_ok = False
                err_msg = f"Expected status {expected_status}, got {resp.status_code}"

        # JSON equality check: pm.expect(json.prop).to.eql('val')
        eql_matches = re.findall(r"pm\.expect\((?:json\.|pm\.response\.json\(\)\.)?([a-zA-Z0-9_]+)\)\.to\.eql\(['\"]([^'\"]+)['\"]\)", test_body)
        for prop, expected_val in eql_matches:
            if isinstance(res_json, dict):
                actual_val = str(res_json.get(prop, ""))
                if actual_val != expected_val:
                    test_ok = False
                    err_msg = f"Expected {prop}='{expected_val}', got '{actual_val}'"

        if test_ok:
            passed += 1
            print(f"      ✓ pm.test: {test_name}")
        else:
            errors.append(f"{test_name} failed: {err_msg}")
            print(f"      ✗ pm.test: {test_name} ({err_msg})")

    return passed, total, errors


def run_postman_collection(collection_path: str) -> bool:
    """Execute all items in the Postman collection and assert responses."""
    with open(collection_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    client = TestClient(app)
    env: Dict[str, Any] = {
        "baseUrl": "",
        "test_product_id": "prod_1",
    }

    total_requests = 0
    passed_requests = 0
    total_assertions = 0
    passed_assertions = 0
    failures: List[str] = []

    def process_items(items: list):
        nonlocal total_requests, passed_requests, total_assertions, passed_assertions
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

                        # Evaluate pm.test script assertions
                        events = item.get("event", [])
                        for ev in events:
                            if ev.get("listen") == "test":
                                script_lines = ev.get("script", {}).get("exec", [])
                                if script_lines:
                                    p_ast, t_ast, ast_errs = evaluate_pm_tests(script_lines, resp)
                                    passed_assertions += p_ast
                                    total_assertions += t_ast
                                    for e in ast_errs:
                                        failures.append(f"{item['name']} assertion error: {e}")

                        # Capture environment variables if present
                        try:
                            res_json = resp.json()
                            if isinstance(res_json, dict) and "items" in res_json and len(res_json["items"]) > 0:
                                env["test_product_id"] = res_json["items"][0]["id"]
                            elif isinstance(res_json, list) and len(res_json) > 0:
                                env["test_product_id"] = res_json[0]["id"]
                        except Exception:
                            pass
                    else:
                        fail_msg = f"  ✗ [{resp.status_code}] {item['name']} ({method} {url}) - Response: {resp.text}"
                        print(fail_msg)
                        failures.append(fail_msg)
                except Exception as exc:
                    fail_msg = f"  ✗ [EXC] {item['name']} ({method} {url}) - Error: {exc}"
                    print(fail_msg)
                    failures.append(fail_msg)

    process_items(data.get("item", []))

    print("\n" + "=" * 65)
    print(f"Postman Collection Execution: {passed_requests}/{total_requests} Requests Passed.")
    if total_assertions > 0:
        print(f"Postman pm.test Assertions: {passed_assertions}/{total_assertions} Assertions Verified.")
    print("=" * 65)

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



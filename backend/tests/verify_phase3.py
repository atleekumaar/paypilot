import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=== 1. NATURAL LANGUAGE DISCOVERY ===")
search_res = client.post("/api/discovery/search", json={"query": "Find me a laptop under 1200 for AI development with good battery life."})
assert search_res.status_code == 200
top_pick = search_res.json()["recommendations"][0]
prod_id = top_pick["product"]["id"]
print(f"Top recommendation: {top_pick['product']['name']} ({prod_id}) - ${top_pick['product']['price']}")

print("\n=== 2. FORMULATE PURCHASE PLAN ===")
plan_res = client.post("/api/purchase-plans", json={"product_id": prod_id, "quantity": 1, "unit_price": 1.0})
assert plan_res.status_code == 201
plan = plan_res.json()
print(f"Purchase Plan created: {plan['id']} | Authoritative Total: ${plan['total_amount']} {plan['currency']} | Status: {plan['status']}")
assert plan["total_amount"] == top_pick["product"]["price"]

print("\n=== 3. UNAPPROVED ORDER CREATION ATTEMPT ===")
unapproved_res = client.post("/api/payments/paypal/create-order", json={"purchase_plan_id": plan["id"]})
assert unapproved_res.status_code == 400
print("Correctly rejected unapproved plan order creation (HTTP 400)")

print("\n=== 4. EXPLICIT USER APPROVAL ===")
approve_res = client.post(f"/api/purchase-plans/{plan['id']}/approve")
assert approve_res.status_code == 200
print(f"User approved plan. Status: {approve_res.json()['status']}")

print("\n=== 5. CREATE PAYPAL SANDBOX ORDER ===")
order_res = client.post("/api/payments/paypal/create-order", json={"purchase_plan_id": plan["id"]})
assert order_res.status_code == 201
order_data = order_res.json()
paypal_order_id = order_data["paypal_order_id"]
print(f"PayPal Sandbox Order created: {paypal_order_id} | Status: {order_data['status']}")

print("\n=== 6. MISMATCH ORDER CAPTURE ATTEMPT ===")
mismatch_res = client.post("/api/payments/paypal/capture", json={"purchase_plan_id": plan["id"], "paypal_order_id": "WRONG_ID"})
assert mismatch_res.status_code == 400
print("Correctly rejected order mismatch (HTTP 400)")

print("\n=== 7. AUTHORIZED PAYPAL CAPTURE & VERIFICATION ===")
capture_res = client.post("/api/payments/paypal/capture", json={"purchase_plan_id": plan["id"], "paypal_order_id": paypal_order_id})
assert capture_res.status_code == 200
payment = capture_res.json()
print(f"Verified Payment: Status={payment['status']}, Amount=${payment['amount']}, CaptureID={payment['capture_id']}")

print("\n=== 8. IDEMPOTENT DUPLICATE CAPTURE GUARD ===")
dup_res = client.post("/api/payments/paypal/capture", json={"purchase_plan_id": plan["id"], "paypal_order_id": paypal_order_id})
assert dup_res.status_code == 200
assert dup_res.json()["id"] == payment["id"]
print("Duplicate capture safely returned existing payment record without double-billing")

print("\n=== 9. FINAL PURCHASE PLAN VERIFICATION ===")
final_plan = client.get(f"/api/purchase-plans/{plan['id']}").json()
print(f"Final Plan Status: {final_plan['status']}")
assert final_plan["status"] == "COMPLETED"

print("\n>>> ALL PHASE 3 VERIFICATION GATES PASSED! <<<")

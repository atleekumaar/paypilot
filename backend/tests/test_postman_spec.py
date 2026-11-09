"""Tests validating Postman collection and environment specification."""

import json
import os
import pytest
from postman.run_collection import run_postman_collection


def test_postman_collection_structure():
    col_path = os.path.join(os.path.dirname(__file__), "..", "..", "postman", "PayPilot.postman_collection.json")
    assert os.path.exists(col_path)

    with open(col_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "info" in data
    assert data["info"]["name"] == "PayPilot Agentic Commerce API"
    assert len(data.get("item", [])) >= 8  # 8 major endpoint folders


def test_postman_environment_structure():
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", "postman", "PayPilot.postman_environment.json")
    assert os.path.exists(env_path)

    with open(env_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["name"] == "PayPilot Local & Render Environment"
    var_names = [v["key"] for v in data.get("values", [])]
    assert "baseUrl" in var_names
    assert "renderUrl" in var_names


def test_postman_collection_execution():
    col_path = os.path.join(os.path.dirname(__file__), "..", "..", "postman", "PayPilot.postman_collection.json")
    success = run_postman_collection(col_path)
    assert success is True


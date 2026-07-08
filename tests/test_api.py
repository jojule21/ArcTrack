import importlib
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Fresh app + temporary database per test (init_db seeds demo data)."""
    monkeypatch.chdir(tmp_path)  # DB_PATH is relative, so the db lands in tmp
    import app as app_module
    importlib.reload(app_module)
    app_module.init_db()
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


def test_add_and_list_equipment(client):
    baseline = len(client.get("/api/equipment").get_json())
    r = client.post("/api/equipment", json={"name": "Hoyt Satori", "type": "bow", "brand": "Hoyt"})
    assert r.status_code == 201
    items = client.get("/api/equipment").get_json()
    assert len(items) == baseline + 1
    assert any(i["name"] == "Hoyt Satori" for i in items)


def test_create_session_and_log_ends(client):
    r = client.post("/api/sessions", json={"date": "2026-07-01", "location": "Range A", "distance_m": 18})
    assert r.status_code == 201
    sid = r.get_json()["id"]

    for score in (52, 48):
        r = client.post(f"/api/sessions/{sid}/ends", json={"score": score, "grouping_cm": 12.5})
        assert r.status_code == 201

    ends = client.get(f"/api/sessions/{sid}/ends").get_json()
    assert [e["end_number"] for e in ends] == [1, 2]  # auto-numbered per session
    assert ends[0]["arrows"] == 6  # default arrow count


def test_session_list_aggregates(client):
    sid = client.post("/api/sessions", json={"date": "2026-07-01"}).get_json()["id"]
    client.post(f"/api/sessions/{sid}/ends", json={"score": 50})
    client.post(f"/api/sessions/{sid}/ends", json={"score": 40})

    sessions = client.get("/api/sessions").get_json()
    mine = next(s for s in sessions if s["id"] == sid)
    assert mine["end_count"] == 2
    assert mine["total_score"] == 90


def test_stats_reflect_new_data(client):
    before = client.get("/api/stats").get_json()["totals"]

    sid = client.post("/api/sessions", json={"date": "2026-07-01", "location": "Range A"}).get_json()["id"]
    client.post(f"/api/sessions/{sid}/ends", json={"score": before["best_end"] + 1, "grouping_cm": 1.0})

    after = client.get("/api/stats").get_json()["totals"]
    assert after["total_sessions"] == before["total_sessions"] + 1
    assert after["total_ends"] == before["total_ends"] + 1
    assert after["best_end"] == before["best_end"] + 1  # new personal best
    assert after["best_grouping"] <= 1.0


def test_delete_session(client):
    sid = client.post("/api/sessions", json={"date": "2026-07-01"}).get_json()["id"]
    assert client.delete(f"/api/sessions/{sid}").status_code == 200
    assert all(s["id"] != sid for s in client.get("/api/sessions").get_json())

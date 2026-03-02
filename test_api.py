"""Quick test script for all AgroFix API endpoints."""
import httpx
import json
import random
import sys

BASE = "http://127.0.0.1:8000"
FID = None


def test_health():
    r = httpx.get(f"{BASE}/api/health")
    print(f"[HEALTH] {r.status_code}: {r.json()}")
    return r.status_code == 200


def test_create_farmer():
    global FID
    r = httpx.post(
        f"{BASE}/api/farmers/",
        json={
            "name": "Rajesh Kumar",
            "phone": f"9{random.randint(100000000, 999999999)}",
            "location": "Punjab, India",
            "language": "en",
        },
    )
    data = r.json()
    FID = data.get("id")
    print(f"[FARMER CREATE] {r.status_code}: id={FID}, name={data.get('name')}")
    return r.status_code == 200


def test_get_farmer():
    r = httpx.get(f"{BASE}/api/farmers/{FID}")
    print(f"[FARMER GET] {r.status_code}: {r.json().get('name')}")
    return r.status_code == 200


def test_list_farmers():
    r = httpx.get(f"{BASE}/api/farmers/")
    farmers = r.json()
    print(f"[FARMER LIST] {r.status_code}: {len(farmers)} farmers")
    return r.status_code == 200


def test_esg_action():
    r = httpx.post(
        f"{BASE}/api/esg/action",
        json={
            "farmer_id": FID,
            "action_type": "organic_fertilizer",
            "details": {"quantity": "5 tonnes"},
        },
    )
    data = r.json()
    print(f"[ESG ACTION] {r.status_code}: score={data.get('overall_score')}, trend={data.get('trend')}")
    return r.status_code == 200


def test_esg_score():
    r = httpx.get(f"{BASE}/api/esg/score/{FID}")
    data = r.json()
    print(f"[ESG SCORE] {r.status_code}: overall={data.get('overall_score')}, E={data.get('environmental')}, S={data.get('social')}, G={data.get('governance')}")
    return r.status_code == 200


def test_digital_twin_update():
    r = httpx.post(
        f"{BASE}/api/digital-twin/update",
        json={
            "farmer_id": FID,
            "lat": 30.7333,
            "lng": 76.7794,
            "zone_type": "soil",
            "risk_level": "yellow",
            "details": {"note": "Low organic carbon"},
        },
    )
    data = r.json()
    print(f"[DIGITAL TWIN UPDATE] {r.status_code}: overall_risk={data.get('overall_risk')}, zones={len(data.get('zones', []))}")
    return r.status_code == 200


def test_digital_twin_map():
    r = httpx.get(f"{BASE}/api/digital-twin/map/{FID}")
    data = r.json()
    print(f"[DIGITAL TWIN MAP] {r.status_code}: overall_risk={data.get('overall_risk')}, zones={len(data.get('zones', []))}")
    return r.status_code == 200


def test_shc(timeout=30):
    r = httpx.post(
        f"{BASE}/api/shc/fetch",
        json={"farmer_id": FID, "shc_id": "SHC-2024-001"},
        timeout=timeout,
    )
    data = r.json()
    soil = data.get("soil_parameters", {})
    advice = str(data.get("fertilizer_advice", ""))[:150]
    print(f"[SHC] {r.status_code}: N={soil.get('N')}, P={soil.get('P')}, K={soil.get('K')}, pH={soil.get('ph')}")
    print(f"  Advice: {advice}...")
    return r.status_code == 200


def test_rag(timeout=30):
    r = httpx.post(
        f"{BASE}/api/rag/query",
        json={
            "farmer_id": FID,
            "question": "What fertilizer should I use for wheat in Punjab?",
        },
        timeout=timeout,
    )
    data = r.json()
    rec = str(data.get("recommendation", ""))[:200]
    print(f"[RAG] {r.status_code}: risk={data.get('risk_level')}")
    print(f"  Recommendation: {rec}...")
    print(f"  Citations: {len(data.get('citations', []))}")
    return r.status_code == 200


def test_harvest(timeout=30):
    r = httpx.post(
        f"{BASE}/api/harvest/analyze",
        json={
            "farmer_id": FID,
            "crop": "wheat",
            "location": "Punjab",
            "current_maturity_pct": 85.0,
        },
        timeout=timeout,
    )
    data = r.json()
    scenarios = data.get("scenarios", [])
    best = data.get("recommended_scenario", "N/A")
    print(f"[HARVEST] {r.status_code}: {len(scenarios)} scenarios, best={best}")
    for s in scenarios:
        print(f"  {s['label']}: profit={s['net_profit']}, risk={s['weather_risk']}")
    return r.status_code == 200


def test_report(timeout=30):
    r = httpx.post(
        f"{BASE}/api/report/generate",
        json={
            "farmer_id": FID,
            "include_sections": ["soil", "chemicals", "esg"],
        },
        timeout=timeout,
    )
    data = r.json()
    print(f"[REPORT] {r.status_code}: pdf={data.get('pdf_url')}")
    return r.status_code == 200


def test_orchestrator(timeout=30):
    r = httpx.post(
        f"{BASE}/api/orchestrator/chat",
        json={
            "farmer_id": FID,
            "message": "My wheat crop has yellow spots on leaves, what should I do?",
        },
        timeout=timeout,
    )
    data = r.json()
    print(f"[ORCHESTRATOR] {r.status_code}: intent={data.get('intent')}, module={data.get('module')}")
    resp = data.get("response", {})
    if isinstance(resp, dict):
        rec = str(resp.get("recommendation", ""))[:150]
        if rec:
            print(f"  Response: {rec}...")
    return r.status_code == 200


if __name__ == "__main__":
    print("=" * 60)
    print("AgroFix API Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Local-only tests (no AI needed)
    print("\n--- Local Endpoints (no AI) ---")
    results["health"] = test_health()
    results["farmer_create"] = test_create_farmer()
    results["farmer_get"] = test_get_farmer()
    results["farmer_list"] = test_list_farmers()
    results["esg_action"] = test_esg_action()
    results["esg_score"] = test_esg_score()
    results["digital_twin_update"] = test_digital_twin_update()
    results["digital_twin_map"] = test_digital_twin_map()
    
    # AI-powered tests (need Gemini API key)
    print("\n--- AI-Powered Endpoints (Gemini) ---")
    try:
        results["shc"] = test_shc()
    except Exception as e:
        print(f"[SHC] FAILED: {e}")
        results["shc"] = False
    
    try:
        results["rag"] = test_rag()
    except Exception as e:
        print(f"[RAG] FAILED: {e}")
        results["rag"] = False
    
    try:
        results["harvest"] = test_harvest()
    except Exception as e:
        print(f"[HARVEST] FAILED: {e}")
        results["harvest"] = False
    
    try:
        results["report"] = test_report()
    except Exception as e:
        print(f"[REPORT] FAILED: {e}")
        results["report"] = False
    
    try:
        results["orchestrator"] = test_orchestrator()
    except Exception as e:
        print(f"[ORCHESTRATOR] FAILED: {e}")
        results["orchestrator"] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    for name, ok in results.items():
        status = "PASS" if ok else "FAIL"
        print(f"  {status} | {name}")
    print(f"\n{passed}/{total} tests passed")

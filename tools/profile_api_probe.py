"""Small, read-only test of Instagram's public profile-info response.

This does not establish username registration availability.
Stops immediately on access restrictions, and does not use proxies or credentials.
"""
import json
import time
import urllib.error
import urllib.parse
import urllib.request

CASES = (
    ("instagram", "known_existing"),
    ("unlikely_nonexistent_zzqv_739182", "expected_missing"),
)
URL = "https://www.instagram.com/api/v1/users/web_profile_info/?username="


def probe(name):
    request = urllib.request.Request(
        URL + urllib.parse.quote(name),
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; ReadOnlyProfileProbe/1.0)",
            "Accept": "application/json",
            "X-IG-App-ID": "936619743392459",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            status = response.status
            body = response.read(65536)
    except urllib.error.HTTPError as error:
        status = error.code
        body = b""
    except (urllib.error.URLError, TimeoutError) as error:
        return {"http_status": None, "verdict": "network_error", "reason": type(error).__name__}

    if status in (403, 429):
        return {"http_status": status, "verdict": "blocked", "reason": "stop_testing"}
    if status == 404:
        return {"http_status": status, "verdict": "no_public_profile", "reason": "not_a_claimability_check"}
    if status != 200:
        return {"http_status": status, "verdict": "unknown", "reason": "unexpected_status"}
    try:
        payload = json.loads(body)
        user = payload.get("data", {}).get("user")
        if isinstance(user, dict) and user.get("username", "").lower() == name.lower():
            return {"http_status": status, "verdict": "public_profile_found"}
        return {"http_status": status, "verdict": "unknown", "reason": "missing_matching_user_object"}
    except (ValueError, TypeError, AttributeError):
        return {"http_status": status, "verdict": "unknown", "reason": "not_valid_profile_json"}


def main():
    results = []
    for index, (username, label) in enumerate(CASES):
        if index:
            time.sleep(5)
        result = probe(username)
        result.update({"username": username, "case": label})
        results.append(result)
        print(json.dumps(result, ensure_ascii=False))
        if result["verdict"] in ("blocked", "network_error"):
            break
    with open("probe-results.json", "w", encoding="utf-8") as handle:
        json.dump(results, handle, ensure_ascii=False, indent=2)
    existing = next((r for r in results if r["case"] == "known_existing"), None)
    missing = next((r for r in results if r["case"] == "expected_missing"), None)
    valid = bool(
        existing and existing["verdict"] == "public_profile_found"
        and missing and missing["verdict"] == "no_public_profile"
    )
    print("PUBLIC_PROFILE_PROBE_VALIDATED=" + str(valid).lower())
    print("This test does NOT confirm that any username can be registered.")


if __name__ == "__main__":
    main()

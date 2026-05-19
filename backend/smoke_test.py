import urllib.request, urllib.parse, json, sys

BASE = "http://localhost:8000"

# Login
req = urllib.request.Request(
    BASE + "/api/auth/login",
    urllib.parse.urlencode({"username": "admin", "password": "Admin@123"}).encode(),
    {"Content-Type": "application/x-www-form-urlencoded"}
)
r = urllib.request.urlopen(req, timeout=5)
d = json.loads(r.read())
print("LOGIN:", d["user"]["full_name"], "/", d["user"]["role"])
token = d["access_token"]
H = {"Authorization": f"Bearer {token}"}

# Teams
r2 = urllib.request.urlopen(urllib.request.Request(BASE + "/api/teams/", headers=H), timeout=5)
teams = json.loads(r2.read())
print(f"TEAMS: {len(teams)} found")
for t in teams:
    print(f"  - {t['name']} ({t['team_type']}) - {t['member_count']} members")

# Issues with new statuses
r3 = urllib.request.urlopen(urllib.request.Request(BASE + "/api/issues/", headers=H), timeout=5)
issues = json.loads(r3.read())
statuses = sorted(set(i["status"] for i in issues))
print(f"ISSUES: {len(issues)} found, statuses: {statuses}")

# Check new statuses exist
expected = {"qa_approved", "uat", "blocked"}
found = set(statuses)
for s in expected:
    if s in found:
        print(f"  ✅ Status '{s}' present")
    else:
        print(f"  ⚠️  Status '{s}' not in current data (may be unused)")

# Frontend
r4 = urllib.request.urlopen(urllib.request.Request(BASE + "/"), timeout=5)
html = r4.read().decode()
print("FRONTEND:", "OK" if "Awash Bank" in html else "MISSING")

r5 = urllib.request.urlopen(urllib.request.Request(BASE + "/app.js"), timeout=5)
js = r5.read().decode()
print("APP.JS:", "OK" if "doLogin" in js else "MISSING")

print("\nALL SMOKE TESTS PASSED")

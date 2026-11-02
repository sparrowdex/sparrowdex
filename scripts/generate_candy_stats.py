"""Fill the candy-wrapper stat SVGs with live GitHub numbers.

Uses only the standard library so it runs on a bare Actions runner.

  GITHUB_TOKEN=... python scripts/generate_candy_stats.py <username> <out_dir>

Templates are images/candy_wrapper_{contribs,streak,record}.svg -- the big
number in each is swapped for the real value and written to <out_dir>.
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.request

API = "https://api.github.com/graphql"
QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    createdAt
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
  }
}"""


def gql(token, **variables):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if "errors" in body:
        sys.exit(f"GraphQL error: {body['errors']}")
    return body["data"]["user"]


def fetch_days(login, token):
    """Every calendar day since the account was created -> {date: count}."""
    now = dt.datetime.now(dt.timezone.utc)
    first = gql(token, login=login, **{"from": (now - dt.timedelta(days=364)).isoformat(), "to": now.isoformat()})
    created = dt.datetime.fromisoformat(first["createdAt"].replace("Z", "+00:00"))

    days = {}
    end = now
    while end > created:  # the API allows at most one year per query
        start = max(created, end - dt.timedelta(days=364))
        user = gql(token, login=login, **{"from": start.isoformat(), "to": end.isoformat()})
        for week in user["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for d in week["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
        end = start - dt.timedelta(seconds=1)
    return days


def compute_stats(days, today):
    dates = sorted(days)
    total = sum(days.values())

    longest = run = 0
    for d in dates:
        run = run + 1 if days[d] > 0 else 0
        longest = max(longest, run)

    # Current streak: today not having a contribution *yet* doesn't break it.
    current = 0
    cursor = dt.date.fromisoformat(today)
    if days.get(today, 0) == 0:
        cursor -= dt.timedelta(days=1)
    while days.get(cursor.isoformat(), 0) > 0:
        current += 1
        cursor -= dt.timedelta(days=1)

    return {"contribs": total, "streak": current, "record": longest}


NUMBER_RE = re.compile(r'(font-size="32"[^>]*>)[^<]*(</text>)')


def render(stats, out_dir, template_dir="images"):
    os.makedirs(out_dir, exist_ok=True)
    for key, value in stats.items():
        with open(os.path.join(template_dir, f"candy_wrapper_{key}.svg"), encoding="utf-8") as f:
            svg = f.read()
        svg, n = NUMBER_RE.subn(rf"\g<1>{value:,}\g<2>", svg, count=1)
        if n != 1:
            sys.exit(f"Could not find the number slot in candy_wrapper_{key}.svg")
        with open(os.path.join(out_dir, f"candy_{key}.svg"), "w", encoding="utf-8") as f:
            f.write(svg)


if __name__ == "__main__":
    login, out_dir = sys.argv[1], sys.argv[2]
    token = os.environ.get("GITHUB_TOKEN") or sys.exit("GITHUB_TOKEN is not set")
    days = fetch_days(login, token)
    stats = compute_stats(days, dt.datetime.now(dt.timezone.utc).date().isoformat())
    render(stats, out_dir)
    print(json.dumps(stats))

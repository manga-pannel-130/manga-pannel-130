import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

USERNAME = "manga-pannel-130"
OUTPUT = Path("assets/github/streak.svg")

GITHUB_API = "https://api.github.com/graphql"


def github_query(query, variables):
    token = os.environ["GITHUB_TOKEN"]

    data = json.dumps({
        "query": query,
        "variables": variables,
    }).encode("utf-8")

    request = urllib.request.Request(
        GITHUB_API,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "github-actions-streak-generator",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))

    if "errors" in result:
        raise RuntimeError(result["errors"])

    return result["data"]


def get_contribution_data():
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """

    return github_query(query, {"login": USERNAME})


def calculate_streak(calendar):
    days = []

    for week in calendar["weeks"]:
        for day in week["contributionDays"]:
            days.append({
                "date": datetime.strptime(
                    day["date"], "%Y-%m-%d"
                ).date(),
                "count": day["contributionCount"],
            })

    days.sort(key=lambda x: x["date"])

    if not days:
        return 0, 0

    longest = 0
    current = 0

    for day in days:
        if day["count"] > 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0

    today = datetime.now(timezone.utc).date()

    current_streak = 0

    for day in reversed(days):
        if day["date"] > today:
            continue

        if day["count"] > 0:
            current_streak += 1
        else:
            break

    return current_streak, longest


def escape_xml(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def create_svg(total, current, longest):
    return f"""<svg xmlns="http://www.w3.org/2000/svg"
    width="720"
    height="230"
    viewBox="0 0 720 230">

  <rect
    width="720"
    height="230"
    rx="18"
    fill="#0d1117"/>

  <text
    x="40"
    y="48"
    font-family="Arial, sans-serif"
    font-size="26"
    font-weight="bold"
    fill="#ffffff">
    GitHub Streak
  </text>

  <text
    x="40"
    y="76"
    font-family="Arial, sans-serif"
    font-size="15"
    fill="#8b949e">
    @{escape_xml(USERNAME)}
  </text>

  <line
    x1="40"
    y1="98"
    x2="680"
    y2="98"
    stroke="#30363d"/>

  <text
    x="40"
    y="130"
    font-family="Arial, sans-serif"
    font-size="13"
    fill="#8b949e">
    Total Contributions
  </text>

  <text
    x="40"
    y="160"
    font-family="Arial, sans-serif"
    font-size="24"
    font-weight="bold"
    fill="#58a6ff">
    {escape_xml(total)}
  </text>

  <text
    x="270"
    y="130"
    font-family="Arial, sans-serif"
    font-size="13"
    fill="#8b949e">
    Current Streak
  </text>

  <text
    x="270"
    y="160"
    font-family="Arial, sans-serif"
    font-size="24"
    font-weight="bold"
    fill="#3fb950">
    {escape_xml(current)} days
  </text>

  <text
    x="500"
    y="130"
    font-family="Arial, sans-serif"
    font-size="13"
    fill="#8b949e">
    Longest Streak
  </text>

  <text
    x="500"
    y="160"
    font-family="Arial, sans-serif"
    font-size="24"
    font-weight="bold"
    fill="#ffffff">
    {escape_xml(longest)} days
  </text>

  <text
    x="40"
    y="200"
    font-family="Arial, sans-serif"
    font-size="13"
    fill="#8b949e">
    GitHub contribution activity
  </text>

</svg>
"""


def main():
    data = get_contribution_data()

    user = data.get("user")

    if not user:
        raise RuntimeError("GitHub user not found.")

    calendar = user["contributionsCollection"]["contributionCalendar"]

    total = calendar["totalContributions"]
    current, longest = calculate_streak(calendar)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        create_svg(total, current, longest),
        encoding="utf-8",
    )

    print(f"Total contributions: {total}")
    print(f"Current streak: {current}")
    print(f"Longest streak: {longest}")
    print(f"Generated: {OUTPUT}")


if __name__ == "__main__":
    main()

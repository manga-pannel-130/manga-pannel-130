import json
import urllib.request
from pathlib import Path

USERNAME = "Madhav63"
OUTPUT = Path("assets/coding/leetcode.svg")

GRAPHQL_URL = "https://leetcode.com/graphql/"


QUERY = """
query getUserStats($username: String!) {
  matchedUser(username: $username) {
    username
    profile {
      ranking
      reputation
    }
    submitStats: submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
      }
    }
    userContestRanking {
      rating
      globalRanking
      attendedContestsCount
    }
  }

  allQuestionsCount {
    difficulty
    count
  }
}
"""


def fetch_data():
    payload = json.dumps({
        "query": QUERY,
        "variables": {
            "username": USERNAME
        }
    }).encode("utf-8")

    request = urllib.request.Request(
        GRAPHQL_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "Chrome/151.0.0.0 Safari/537.36"
            ),
            "Referer": "https://leetcode.com/",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(
            response.read().decode("utf-8")
        )

    if "errors" in result:
        raise RuntimeError(
            "LeetCode GraphQL error: "
            + str(result["errors"])
        )

    return result["data"]


def get_submission_counts(data):
    user = data.get("matchedUser")

    if not user:
        raise RuntimeError(
            f"LeetCode user '{USERNAME}' was not found."
        )

    counts = {
        "All": 0,
        "Easy": 0,
        "Medium": 0,
        "Hard": 0,
    }

    for item in user["submitStats"]["acSubmissionNum"]:
        difficulty = item["difficulty"]
        counts[difficulty] = item["count"]

    return counts


def escape_xml(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def create_svg(data):
    user = data["matchedUser"]

    counts = get_submission_counts(data)

    total_solved = counts["All"]
    easy = counts["Easy"]
    medium = counts["Medium"]
    hard = counts["Hard"]

    ranking = user["profile"]["ranking"]

    contest = user.get("userContestRanking")

    if contest:
        contest_rating = round(contest["rating"])
        global_ranking = contest["globalRanking"]
        contests = contest["attendedContestsCount"]
    else:
        contest_rating = "—"
        global_ranking = "—"
        contests = 0

    return f"""<svg xmlns="http://www.w3.org/2000/svg"
    width="720"
    height="280"
    viewBox="0 0 720 280">

  <rect
    width="720"
    height="280"
    rx="18"
    fill="#0d1117"/>

  <text
    x="40"
    y="48"
    font-family="Arial, sans-serif"
    font-size="26"
    font-weight="bold"
    fill="#ffffff">
    LeetCode
  </text>

  <text
    x="40"
    y="75"
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

  <!-- Row 1 -->

  <text
    x="40"
    y="130"
    font-family="Arial, sans-serif"
    font-size="13"
    fill="#8b949e">
    Problems Solved
  </text>

  <text
    x="40"
    y="158"
    font-family="Arial, sans-serif"
    font-size="24"
    font-weight="bold"
    fill="#3fb950">
    {escape_xml(total_solved)}
  </text>

  <text
    x="240"
    y="130"
    font-family="Arial, sans-serif"
    font-size="13"
    fill="#8b949e">
    Easy
  </text>

  <text
    x="240"
    y="158"
    font-family="Arial, sans-serif"
    font-size="22"
    font-weight="bold"
    fill="#3fb950">
    {escape_xml(easy)}
  </text>

  <text
    x="390"
    y="130"
    font-family="Arial, sans-serif"
    font-size="13"
    fill="#8b949e">
    Medium
  </text>

  <text
    x="390"
    y="158"
    font-family="Arial, sans-serif"
    font-size="22"
    font-weight="bold"
    fill="#d29922">
    {escape_xml(medium)}
  </text>

  <text
    x="540"
    y="130"
    font-family="Arial, sans-serif"
    font-size="13"
    fill="#8b949e">
    Hard
  </text>

  <text
    x="540"
    y="158"
    font-family="Arial, sans-serif"
    font-size="22"
    font-weight="bold"
    fill="#f85149">
    {escape_xml(hard)}
  </text>

  <!-- Row 2 -->

  <text
    x="40"
    y="195"
    font-family="Arial, sans-serif"
    font-size="13"
    fill="#8b949e">
    Global Rank
  </text>

  <text
    x="40"
    y="222"
    font-family="Arial, sans-serif"
    font-size="20"
    font-weight="bold"
    fill="#ffffff">
    {escape_xml(ranking)}
  </text>

  <text
    x="250"
    y="195"
    font-family="Arial, sans-serif"
    font-size="13"
    fill="#8b949e">
    Contest Rating
  </text>

  <text
    x="250"
    y="222"
    font-family="Arial, sans-serif"
    font-size="20"
    font-weight="bold"
    fill="#58a6ff">
    {escape_xml(contest_rating)}
  </text>

  <text
    x="450"
    y="195"
    font-family="Arial, sans-serif"
    font-size="13"
    fill="#8b949e">
    Contests
  </text>

  <text
    x="450"
    y="222"
    font-family="Arial, sans-serif"
    font-size="20"
    font-weight="bold"
    fill="#ffffff">
    {escape_xml(contests)}
  </text>

  <text
    x="40"
    y="255"
    font-family="Arial, sans-serif"
    font-size="13"
    fill="#8b949e">
    LeetCode problem-solving profile
  </text>

</svg>
"""


def main():
    print(f"Fetching LeetCode profile: {USERNAME}")

    data = fetch_data()

    svg = create_svg(data)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(svg, encoding="utf-8")

    counts = get_submission_counts(data)

    print(f"Problems solved: {counts['All']}")
    print(f"Easy: {counts['Easy']}")
    print(f"Medium: {counts['Medium']}")
    print(f"Hard: {counts['Hard']}")
    print(f"Generated: {OUTPUT}")


if __name__ == "__main__":
    main()

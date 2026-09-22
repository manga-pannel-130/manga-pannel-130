import json
import urllib.request
from pathlib import Path


HANDLE = "madhav63"

API_URL = f"https://codeforces.com/api/user.info?handles={HANDLE}"
RATING_URL = f"https://codeforces.com/api/user.rating?handle={HANDLE}"
STATUS_URL = f"https://codeforces.com/api/user.status?handle={HANDLE}&from=1&count=10000"


def get_json(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def get_user_info():
    data = get_json(API_URL)

    if data["status"] != "OK":
        raise RuntimeError(data.get("comment", "Codeforces API error"))

    return data["result"][0]


def get_rating_history():
    data = get_json(RATING_URL)

    if data["status"] != "OK":
        raise RuntimeError(data.get("comment", "Codeforces API error"))

    return data["result"]


def get_submissions():
    data = get_json(STATUS_URL)

    if data["status"] != "OK":
        raise RuntimeError(data.get("comment", "Codeforces API error"))

    return data["result"]


def count_solved_problems(submissions):
    solved = set()

    for submission in submissions:
        if submission.get("verdict") == "OK":
            problem = submission.get("problem", {})

            contest_id = problem.get("contestId")
            index = problem.get("index")

            if contest_id is not None and index:
                solved.add(f"{contest_id}-{index}")

    return len(solved)


def create_svg(user, solved):
    rating = user.get("rating", 0)
    max_rating = user.get("maxRating", 0)
    rank = user.get("rank", "Unrated")
    max_rank = user.get("maxRank", "Unrated")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="720" height="250" viewBox="0 0 720 250">
  <rect width="720" height="250" rx="18" fill="#0d1117"/>

  <text x="40" y="50"
        font-family="Arial, sans-serif"
        font-size="26"
        font-weight="bold"
        fill="#ffffff">
    Codeforces
  </text>

  <text x="40" y="78"
        font-family="Arial, sans-serif"
        font-size="15"
        fill="#8b949e">
    @{HANDLE}
  </text>

  <line x1="40" y1="100" x2="680" y2="100"
        stroke="#30363d"/>

  <text x="40" y="135"
        font-family="Arial, sans-serif"
        font-size="14"
        fill="#8b949e">
    Rating
  </text>

  <text x="40" y="165"
        font-family="Arial, sans-serif"
        font-size="24"
        font-weight="bold"
        fill="#58a6ff">
    {rating}
  </text>

  <text x="190" y="135"
        font-family="Arial, sans-serif"
        font-size="14"
        fill="#8b949e">
    Max Rating
  </text>

  <text x="190" y="165"
        font-family="Arial, sans-serif"
        font-size="24"
        font-weight="bold"
        fill="#58a6ff">
    {max_rating}
  </text>

  <text x="370" y="135"
        font-family="Arial, sans-serif"
        font-size="14"
        fill="#8b949e">
    Rank
  </text>

  <text x="370" y="165"
        font-family="Arial, sans-serif"
        font-size="22"
        font-weight="bold"
        fill="#ffffff">
    {rank}
  </text>

  <text x="530" y="135"
        font-family="Arial, sans-serif"
        font-size="14"
        fill="#8b949e">
    Solved
  </text>

  <text x="530" y="165"
        font-family="Arial, sans-serif"
        font-size="24"
        font-weight="bold"
        fill="#3fb950">
    {solved}
  </text>

  <text x="40" y="215"
        font-family="Arial, sans-serif"
        font-size="13"
        fill="#8b949e">
    Max Rank: {max_rank}
  </text>
</svg>
"""

    return svg


def main():
    user = get_user_info()
    submissions = get_submissions()

    solved = count_solved_problems(submissions)

    svg = create_svg(user, solved)

    output = Path("assets/coding/codeforces.svg")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding="utf-8")

    print(f"Updated Codeforces card for @{HANDLE}")
    print(f"Rating: {user.get('rating', 0)}")
    print(f"Max Rating: {user.get('maxRating', 0)}")
    print(f"Rank: {user.get('rank', 'Unrated')}")
    print(f"Solved: {solved}")


if __name__ == "__main__":
    main()

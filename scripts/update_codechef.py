import re
import urllib.request
from html import unescape
from pathlib import Path

HANDLE = "gamma_apes_15"
PROFILE_URL = f"https://www.codechef.com/users/{HANDLE}"
OUTPUT = Path("assets/coding/codechef.svg")


def fetch_profile():
    request = urllib.request.Request(
        PROFILE_URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/151.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml",
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def clean_html(value):
    value = re.sub(r"<[^>]+>", " ", value)
    value = unescape(value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def find_first(patterns, html, default="—"):
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        if match:
            value = clean_html(match.group(1))
            if value:
                return value

    return default


def extract_stats(html):
    # Current rating
    rating = find_first(
        [
            r'class="rating-number"[^>]*>\s*([^<]+)',
            r'Rating\s*</[^>]+>\s*<[^>]+>\s*([^<]+)',
        ],
        html,
    )

    # Highest rating
    highest_rating = find_first(
        [
            r'Highest Rating[^<]{0,100}<[^>]*>\s*([^<]+)',
            r'highest-rating[^>]*>.*?<[^>]*>\s*([^<]+)',
        ],
        html,
    )

    # Global rank
    global_rank = find_first(
        [
            r'Global Rank[^<]{0,100}<[^>]*>\s*([^<]+)',
            r'global-rank[^>]*>.*?<[^>]*>\s*([^<]+)',
        ],
        html,
    )

    # Country rank
    country_rank = find_first(
        [
            r'Country Rank[^<]{0,100}<[^>]*>\s*([^<]+)',
            r'country-rank[^>]*>.*?<[^>]*>\s*([^<]+)',
        ],
        html,
    )

    # Division
    division = find_first(
        [
            r'Division\s*([^<]{0,50})',
            r'Division[^<]{0,100}(Div\s*[1-4])',
        ],
        html,
    )

    # Problems solved
    problems_solved = find_first(
        [
            r'Total Problems Solved[^<]{0,150}<[^>]*>\s*([^<]+)',
            r'problems-solved[^>]*>.*?<[^>]*>\s*([^<]+)',
        ],
        html,
    )

    # Contest count
    contests = find_first(
        [
            r'Contests[^<]{0,150}<[^>]*>\s*([^<]+)',
            r'contests-count[^>]*>.*?<[^>]*>\s*([^<]+)',
        ],
        html,
    )

    return {
        "rating": rating,
        "highest_rating": highest_rating,
        "global_rank": global_rank,
        "country_rank": country_rank,
        "division": division,
        "problems_solved": problems_solved,
        "contests": contests,
    }


def escape_xml(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def create_svg(stats):
    rating = escape_xml(stats["rating"])
    highest_rating = escape_xml(stats["highest_rating"])
    global_rank = escape_xml(stats["global_rank"])
    country_rank = escape_xml(stats["country_rank"])
    division = escape_xml(stats["division"])
    problems_solved = escape_xml(stats["problems_solved"])
    contests = escape_xml(stats["contests"])

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
    CodeChef
  </text>

  <text
    x="40"
    y="75"
    font-family="Arial, sans-serif"
    font-size="15"
    fill="#8b949e">
    @{escape_xml(HANDLE)}
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
    Rating
  </text>

  <text
    x="40"
    y="158"
    font-family="Arial, sans-serif"
    font-size="23"
    font-weight="bold"
    fill="#58a6ff">
    {rating}
  </text>

  <text
    x="220"
    y="130"
    font-family="Arial, sans-serif"
    font-size="13"
    fill="#8b949e">
    Highest Rating
  </text>

  <text
    x="220"
    y="158"
    font-family="Arial, sans-serif"
    font-size="23"
    font-weight="bold"
    fill="#58a6ff">
    {highest_rating}
  </text>

  <text
    x="450"
    y="130"
    font-family="Arial, sans-serif"
    font-size="13"
    fill="#8b949e">
    Problems Solved
  </text>

  <text
    x="450"
    y="158"
    font-family="Arial, sans-serif"
    font-size="23"
    font-weight="bold"
    fill="#3fb950">
    {problems_solved}
  </text>

  <!-- Row 2 -->

  <text
    x="40"
    y="195"
    font-family="Arial, sans-serif"
    font-size="13"
    fill="#8b949e">
    Division
  </text>

  <text
    x="40"
    y="222"
    font-family="Arial, sans-serif"
    font-size="20"
    font-weight="bold"
    fill="#ffffff">
    {division}
  </text>

  <text
    x="220"
    y="195"
    font-family="Arial, sans-serif"
    font-size="13"
    fill="#8b949e">
    Global Rank
  </text>

  <text
    x="220"
    y="222"
    font-family="Arial, sans-serif"
    font-size="20"
    font-weight="bold"
    fill="#ffffff">
    {global_rank}
  </text>

  <text
    x="450"
    y="195"
    font-family="Arial, sans-serif"
    font-size="13"
    fill="#8b949e">
    Country Rank
  </text>

  <text
    x="450"
    y="222"
    font-family="Arial, sans-serif"
    font-size="20"
    font-weight="bold"
    fill="#ffffff">
    {country_rank}
  </text>

  <text
    x="40"
    y="255"
    font-family="Arial, sans-serif"
    font-size="13"
    fill="#8b949e">
    Contests: {contests}
  </text>

</svg>
"""


def main():
    print(f"Fetching CodeChef profile: {PROFILE_URL}")

    html = fetch_profile()

    if len(html) < 1000:
        raise RuntimeError("CodeChef returned an unexpectedly small response.")

    stats = extract_stats(html)

    print("CodeChef stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Basic sanity check.
    # If every important field failed, do not overwrite the existing card.
    important = [
        stats["rating"],
        stats["highest_rating"],
        stats["global_rank"],
        stats["problems_solved"],
    ]

    if all(value == "—" for value in important):
        raise RuntimeError(
            "Could not extract CodeChef profile statistics. "
            "The CodeChef page structure may have changed."
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(create_svg(stats), encoding="utf-8")

    print(f"Generated: {OUTPUT}")


if __name__ == "__main__":
    main()

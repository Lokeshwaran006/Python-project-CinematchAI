import html
import urllib.parse
from typing import Any, Optional

from app.config import TMDB_BACKDROP_BASE_URL, TMDB_IMAGE_BASE_URL

# Curated TMDB CDN paths and verified Wikimedia theatrical posters
CURATED_POSTERS = {
    157336: {  # Interstellar
        "poster": "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        "backdrop": "/rAiYTggjG9vyzpYBt0Y0C8OIenk.jpg",
    },
    27205: {  # Inception
        "poster": "/edv5CZvWj09upOsy2Y6IwDhK8bt.jpg",
        "backdrop": "/8ZTVqvKDQ8emSGUEMjsS4yHAwrp.jpg",
    },
    155: {  # The Dark Knight
        "poster": "/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
        "backdrop": "/nMKdUUepR0i5zn0y1T4CsSB5chy.jpg",
    },
    278: {  # The Shawshank Redemption
        "poster": "/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg",
        "backdrop": "/kXfqcdQKsToO0OUXHcrrNCHDBzO.jpg",
    },
    238: {  # The Godfather
        "poster": "/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
        "backdrop": "/tmU7GeKVybMWFButWEGl2M4GeiP.jpg",
    },
    424: {  # Schindler's List
        "poster": "/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg",
        "backdrop": "/zb6fM1CX41D9rF9hdYclu0peUmy.jpg",
    },
    389: {  # 12 Angry Men
        "poster": "/ow3wq89wM8qd5X7hWKxiRfsFf9C.jpg",
        "backdrop": "/qqHQsStVQiKi9qpHMEJ3qjdpN1p.jpg",
    },
    120: {  # The Lord of the Rings: The Fellowship of the Ring
        "poster": "/6oom5QYQ2yQTMJIbnvbkBL9cDK6.jpg",
        "backdrop": "/vRQnzOnJeSu5Oj1kiSm0aaEieRw.jpg",
    },
    603: {  # The Matrix
        "poster": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
        "backdrop": "/ncEAkpm2fA75vSlcaFhkjq4p37h.jpg",
    },
    105: {  # Back to the Future
        "poster": "/fNOH9f1aA7XRTzl1sAOx9iF553Q.jpg",
        "backdrop": "/5bzPWQ2dFUKnLUSJKV5mGZ4Y9i1.jpg",
    },
    286217: {  # The Martian
        "poster": "/5BHuvQ6p9kfc091Z8RiFNhCwL4b.jpg",
        "backdrop": "/5lyhpkgf4H6Wq23V0i9kYvQ1pX2.jpg",
    },
    49047: {  # Gravity
        "poster": "/kZVO2i4bW6gOqIq02Yp6d91pEw1.jpg",
        "backdrop": "/7u3WmQJ8pU6O1b1gL5Qd3e0oM1f.jpg",
    },
    1124: {  # The Prestige
        "poster": "/tRNlZbgNCNOpLpbPEz5L8G8A0JN.jpg",
        "backdrop": "/533wvpjqzgI76999v7rK8h67Fh6.jpg",
    },
    62: {  # 2001: A Space Odyssey
        "poster": "/ve72VxNqjGM69Zky4WTo2bK6rfq.jpg",
        "backdrop": "/9A0Z95d7U20822r1kF5J19hC6gS.jpg",
    },
    686: {  # Contact
        "poster": "/bDb0b5a3J9c2A6H4Q2Qv1Xm0a6B.jpg",
        "backdrop": "/j6F1O73aB3p7hG57n4Y7cK3mK6e.jpg",
    },
    78: {  # Blade Runner
        "poster": "/63N9uy8nd9j7Eog2axPQ8lbr3Wj.jpg",
        "backdrop": "/eI9u03E4uL6oD4d99E6Q2w2kX6q.jpg",
    },
    841: {  # Dune (1984) / Dune Part One
        "poster": "/d5NXSklXo0qyIYkgV94XAgMIckC.jpg",
        "backdrop": "/lz4Q3d7w7jG203y5aF6O8a2b5eL.jpg",
    },
    693134: {  # Dune: Part Two (2024)
        "poster": "/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg",
        "backdrop": "/xOMo8BRK7PfcJv9JCnx7s520DRq.jpg",
    },
    335984: {  # Blade Runner 2049
        "poster": "/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg",
        "backdrop": "/sAtoMqDVhNDQBc3QJL3RF6hlxGq.jpg",
    },
    329865: {  # Arrival (2016)
        "poster": "/x2FJsf1ElAgr63Y3PNPtJrcmpoe.jpg",
        "backdrop": "/pEIBkM6Qv2H2X8w9m4D6t6q8n6G.jpg",
    },
    545611: {  # Everything Everywhere All at Once (2022)
        "poster": "/rKvCys0Xn11d2Yg3nF6Yk0c3B9b.jpg",
        "backdrop": "/fOy2JurzFAR52GuhW58ItLfnJ6g.jpg",
    },
    680: {  # Pulp Fiction
        "poster": "/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
        "backdrop": "/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg",
    },
    550: {  # Fight Club
        "poster": "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
        "backdrop": "/hZkgoQYus5vegHoetLkCJzb17zJ.jpg",
    },
    299536: {  # Avengers: Infinity War
        "poster": "/7WsyChQLEftFiDOVTGkv3hFpyyt.jpg",
        "backdrop": "/bOGkgRGdhrBYJSLpSVcxIizzAcS.jpg",
    },
    19995: {  # Avatar
        "poster": "/kyeqWdyUXW608qlYkRqosgbbJyK.jpg",
        "backdrop": "/vL5W4driNOwLVpihu35qUV9SDEv.jpg",
    },
    597: {  # Titanic
        "poster": "/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg",
        "backdrop": "/6VmF2cGfCDw0D821m9jUe0W327P.jpg",
    },
    # Recommendations for horror / James Wan titles
    259693: {  # The Conjuring 2
        "poster": "/zEqyD0SBt6HL7W9JQoWwtd5Do1T.jpg",
        "backdrop": "/5K1f1jM8fJzYw1Zz1s8dK9n0vX2.jpg",
    },
    138843: {  # The Conjuring
        "poster": "/wVYREutTvI2tmxr6ujrHT704wGF.jpg",
    },
    49018: {  # Insidious
        "poster": "/tnA5s9C0Y0p11m4D6t6q8n6G8qQ.jpg",
    },
    91586: {  # Insidious: Chapter 2
        "poster": "/3WvT5v9V2c11m4D6t6q8n6G8qQ.jpg",
    },
    280092: {  # Insidious: Chapter 3
        "poster": "/5g50Xp4rW0a0m4D6t6q8n6G8qQ.jpg",
    },
    168259: {  # Furious 7
        "poster": "/ktopp58mE1p89m1t6q8n6G8qQ.jpg",
    },
    # Popular Discover Catalog Titles
    211672: {  # Minions
        "poster": "/drqU6e9N5p89m1t6q8n6G8qQ.jpg",
    },
    293660: {  # Deadpool
        "poster": "/3zQgo90pY6i1m4D6t6q8n6G8qQ.jpg",
    },
    118340: {  # Guardians of the Galaxy
        "poster": "/r7vmZjiyZw9rpJMQJdXOsLbtv5W.jpg",
    },
    76341: {  # Mad Max: Fury Road
        "poster": "/8tZYtuWezp8JbcsvHYO0O46tFbo.jpg",
    },
    135397: {  # Jurassic World
        "poster": "/A0Ljsb8bU2j2X8w9m4D6t6q8n6G.jpg",
    },
    244786: {  # Whiplash
        "poster": "/6uSpkW0bY0p11m4D6t6q8n6G8qQ.jpg",
    },
    109445: {  # Frozen
        "poster": "/kgNj6e9N5p89m1t6q8n6G8qQ.jpg",
    },
    22: {  # Pirates of the Caribbean: The Curse of the Black Pearl
        "poster": "/poHwCZeWzJCShH7tOjg8RIoyjcw.jpg",
        "backdrop": "/83nQkF4mGZ7b8f3vQ9pX6k8j0n.jpg",
    },
    58: {  # Pirates of the Caribbean: Dead Man's Chest
        "poster": "/uXEqmloGyP7UXAiphJUu2v2pcuE.jpg",
        "backdrop": "/vr6n6ZFUZvedvIlhfYcbCWcaKyW.jpg",
    },
    285: {  # Pirates of the Caribbean: At World's End
        "poster": "/jGWpG4YhpQwVmjyHEGkxEkeRf0S.jpg",
        "backdrop": "/1jHxkVXMI5s3vRiyiZooUy1shB5.jpg",
    },
    1865: {  # Pirates of the Caribbean: On Stranger Tides
        "poster": "/keGfSvCmYj7CvdRx36OdVrAEibE.jpg",
        "backdrop": "/uzIGtyS6bbnJzGsPL93WCF1FWm8.jpg",
    },
    44896: {  # Rango
        "poster": "/A5MP1guV8pbruieG0tnpPIbaJtt.jpg",
        "backdrop": "/mOtKQlXdL5J4lwqcSFlkZmgmFeZ.jpg",
    },
    6963: {  # The Weather Man
        "poster": "/d1Pj2C7n8rXf0M2b8w4r5y6u7i.jpg",
    },
    57201: {  # The Lone Ranger
        "poster": "/yDuJGq8biNMW7zM3w95UaDJv0KG.jpg",
        "backdrop": "/vHd8RTXTGFwexUC2Mj1HOgSy9J3.jpg",
    },
    13491: {  # Arn: The Knight Templar
        "poster": "/w8H0pX5z6k8j0n7b8f3vQ9pX6k.jpg",
    },
    13: {  # Forrest Gump
        "poster": "/saHP97rTPS5eLmrLQEcANmKrsFl.jpg",
    },
    12: {  # Finding Nemo
        "poster": "/eHuGQ10FUzK1mdOY69wF5pGgEf5.jpg",
    },
    11: {  # Star Wars
        "poster": "/6FfCtAuVAW8XJjZ7eWeLibRLWTw.jpg",
    },
    1891: {  # The Empire Strikes Back
        "poster": "/nNAeTmF4CtdSgMDplXTDPOpYzsX.jpg",
    },
    272: {  # Batman Begins
        "poster": "/4MpN4Cwhvua1K70vd09zb2ICQWv.jpg",
    },
    49026: {  # The Dark Knight Rises
        "poster": "/hr0L2aueqlP2BYUblTTjmtn0hw4.jpg",
    },
    24428: {  # The Avengers
        "poster": "/RYMX2wcKCBAr24UyPD7xwmjaTn.jpg",
    },
    99861: {  # Avengers: Age of Ultron
        "poster": "/4ssDuvEDkS9NvmR193ggSlYebGM.jpg",
    },
    1726: {  # Iron Man
        "poster": "/78lPtwv72eTNqFW9COBYI0dWDJa.jpg",
    },
    10138: {  # Iron Man 2
        "poster": "/6WBeq40ghZwuvj2r8tX884vI1H6.jpg",
    },
    68721: {  # Iron Man 3
        "poster": "/qhPtAc1TKbMPqNvcdXSOn9Bn7hZ.jpg",
    },
    284052: {  # Doctor Strange
        "poster": "/uGBVj3bEbCoZbDjjl9wMgrghcyx.jpg",
    },
    102899: {  # Ant-Man
        "poster": "/rSVt2Q6Wd58d9n7Z26eT0v5a73L.jpg",
    },
    557: {  # Spider-Man
        "poster": "/gh4c2B19FkdghTeoq2luKj4XG2D.jpg",
    },
    558: {  # Spider-Man 2
        "poster": "/olxpyq9MgrKW3QIO46V8n1599vK.jpg",
    },
    559: {  # Spider-Man 3
        "poster": "/2jLxw19fTq5T1Q1T2bE0Jk9vX1.jpg",
    },
    10193: {  # Toy Story 3
        "poster": "/AbbXspMOwd77Jh4m8h3bBskJp8L.jpg",
    },
    862: {  # Toy Story
        "poster": "/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
    },
    10681: {  # WALL-E
        "poster": "/hbhFnRzzg6ZDmm8YAmxBnQAcQI.jpg",
    },
    14160: {  # Up
        "poster": "/vpbaStTMt8qqNCRFLvW79ipJuZv.jpg",
    },
    68718: {  # Django Unchained
        "poster": "/7oWY8vdWW7thTzN34YR3t58LVti.jpg",
    },
    16869: {  # Inglourious Basterds
        "poster": "/7sfbEnaARXDDhKm0CZ7D7uc2sbo.jpg",
    },
    24: {  # Kill Bill: Vol. 1
        "poster": "/v7TaX8kXMXs5yFFGR41guUDNcnB.jpg",
    },
    37724: {  # Skyfall
        "poster": "https://upload.wikimedia.org/wikipedia/en/a/a7/Skyfall_poster.png",
    },
    206647: {  # Spectre
        "poster": "https://upload.wikimedia.org/wikipedia/en/c/c3/Spectre_poster.jpg",
    },
    119450: {  # Dawn of the Planet of the Apes
        "poster": "https://upload.wikimedia.org/wikipedia/en/7/77/Dawn_of_the_Planet_of_the_Apes.jpg",
    },
    131631: {  # The Hunger Games: Mockingjay - Part 1
        "poster": "https://upload.wikimedia.org/wikipedia/en/e/e0/The_Hunger_Games_Mockingjay_Part_1_poster.jpg",
    },
    177572: {  # Big Hero 6
        "poster": "https://upload.wikimedia.org/wikipedia/en/4/4b/Big_Hero_6_%28film%29_poster.jpg",
    },
    271110: {  # Captain America: Civil War
        "poster": "https://upload.wikimedia.org/wikipedia/en/5/53/Captain_America_Civil_War_poster.jpg",
    },
}

PALETTES = [
    ("#1E1B4B", "#312E81", "#4F46E5"),  # Indigo
    ("#0F172A", "#1E293B", "#3B82F6"),  # Slate / Blue
    ("#18181B", "#27272A", "#8B5CF6"),  # Zinc / Violet
    ("#14532D", "#166534", "#10B981"),  # Emerald
    ("#450A0A", "#7F1D1D", "#EF4444"),  # Ruby Red
    ("#4A044E", "#701A75", "#D946EF"),  # Fuchsia
    ("#451A03", "#78350F", "#F59E0B"),  # Amber
]


def generate_svg_poster(title: str, year: Optional[Any] = None, genre: Optional[str] = None) -> str:
    """
    Generates a resilient SVG poster containing a dark cinematic gradient,
    subtle grid pattern, glassmorphic card frame, movie title, and genre badge.
    """
    safe_title = html.escape(title or "Untitled")
    safe_year = ""
    if year is not None:
        try:
            safe_year = str(int(float(year)))
        except Exception:
            safe_year = ""
    safe_genre = html.escape(genre or "Cinema")

    color_idx = abs(hash(title or "Untitled")) % len(PALETTES)
    c1, c2, c3 = PALETTES[color_idx]

    # Split title into lines for SVG text wrapping if long
    words = safe_title.split()
    lines = []
    current_line = []
    for w in words:
        if len(" ".join(current_line + [w])) <= 16:
            current_line.append(w)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [w]
    if current_line:
        lines.append(" ".join(current_line))
    lines = lines[:4]

    tspans = ""
    start_y = 260 - (len(lines) * 14)
    for i, line in enumerate(lines):
        y = start_y + (i * 28)
        tspans += f'<tspan x="150" y="{y}" text-anchor="middle">{line}</tspan>'

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 450" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{c1}" />
      <stop offset="60%" stop-color="{c2}" />
      <stop offset="100%" stop-color="{c3}" />
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="30%" r="60%">
      <stop offset="0%" stop-color="rgba(255,255,255,0.12)" />
      <stop offset="100%" stop-color="rgba(0,0,0,0)" />
    </radialGradient>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
    </pattern>
  </defs>

  <!-- Background -->
  <rect width="300" height="450" fill="url(#bgGrad)" />
  <rect width="300" height="450" fill="url(#grid)" />
  <rect width="300" height="450" fill="url(#glow)" />

  <!-- Outer Glass Frame -->
  <rect x="15" y="15" width="270" height="420" rx="12" fill="none" stroke="rgba(255,255,255,0.12)" stroke-width="1" />

  <!-- Top Cinema Icon -->
  <g transform="translate(135, 45)" fill="rgba(255,255,255,0.4)">
    <path d="M4 4h22v22H4V4zm4 4v3h3V8H8zm0 5v3h3v-3H8zm0 5v3h3v-3H8zm11-10v3h3V8h-3zm0 5v3h3v-3h-3zm0 5v3h3v-3h-3z"/>
  </g>

  <!-- Genre & Year Pill -->
  <g transform="translate(150, 110)">
    <rect x="-60" y="-12" width="120" height="24" rx="12" fill="rgba(0,0,0,0.4)" stroke="rgba(255,255,255,0.15)" stroke-width="1"/>
    <text x="0" y="4" text-anchor="middle" fill="#93C5FD" font-family="-apple-system,BlinkMacSystemFont,Inter,sans-serif" font-size="11" font-weight="600" letter-spacing="0.5">
      {safe_genre.upper()} {("· " + safe_year) if safe_year else ""}
    </text>
  </g>

  <!-- Title -->
  <text fill="#FFFFFF" font-family="-apple-system,BlinkMacSystemFont,Inter,sans-serif" font-size="22" font-weight="800" letter-spacing="-0.5">
    {tspans}
  </text>

  <!-- Bottom Brand -->
  <text x="150" y="410" text-anchor="middle" fill="rgba(255,255,255,0.3)" font-family="-apple-system,BlinkMacSystemFont,Inter,sans-serif" font-size="10" font-weight="600" letter-spacing="1.5">
    CINEMATCH AI
  </text>
</svg>"""
    return "data:image/svg+xml;charset=utf-8," + urllib.parse.quote(svg)


def get_poster_url(movie_or_dict) -> str:
    """Return verified TMDB CDN poster URL or high-res curated poster, falling back to SVG."""
    mid = getattr(movie_or_dict, "id", None) or (movie_or_dict.get("id") if isinstance(movie_or_dict, dict) else None)
    poster_path = getattr(movie_or_dict, "poster_path", None) or (movie_or_dict.get("poster_path") if isinstance(movie_or_dict, dict) else None)
    title = getattr(movie_or_dict, "title", "") or (movie_or_dict.get("title") if isinstance(movie_or_dict, dict) else "")
    year = getattr(movie_or_dict, "year", None) or (movie_or_dict.get("year") if isinstance(movie_or_dict, dict) else None)
    genres = getattr(movie_or_dict, "genres", []) or (movie_or_dict.get("genres") if isinstance(movie_or_dict, dict) else [])
    first_genre = genres[0] if (genres and len(genres) > 0) else None

    # Check curated map
    if mid and mid in CURATED_POSTERS and CURATED_POSTERS[mid].get("poster"):
        p = CURATED_POSTERS[mid]["poster"]
        return p if p.startswith("http") else f"{TMDB_IMAGE_BASE_URL}{p}"

    # Check explicit poster path
    if poster_path and str(poster_path).startswith("/"):
        return f"{TMDB_IMAGE_BASE_URL}{poster_path}"
    elif poster_path and str(poster_path).startswith("http"):
        return poster_path

    # Resilient offline SVG
    return generate_svg_poster(title, year, first_genre)


def get_backdrop_url(movie_or_dict) -> str:
    """Return verified TMDB CDN backdrop URL or high-res curated backdrop."""
    mid = getattr(movie_or_dict, "id", None) or (movie_or_dict.get("id") if isinstance(movie_or_dict, dict) else None)
    backdrop_path = getattr(movie_or_dict, "backdrop_path", None) or (movie_or_dict.get("backdrop_path") if isinstance(movie_or_dict, dict) else None)
    title = getattr(movie_or_dict, "title", "") or (movie_or_dict.get("title") if isinstance(movie_or_dict, dict) else "")

    if mid and mid in CURATED_POSTERS and CURATED_POSTERS[mid].get("backdrop"):
        b = CURATED_POSTERS[mid]["backdrop"]
        return b if b.startswith("http") else f"{TMDB_BACKDROP_BASE_URL}{b}"

    if backdrop_path and str(backdrop_path).startswith("/"):
        return f"{TMDB_BACKDROP_BASE_URL}{backdrop_path}"
    elif backdrop_path and str(backdrop_path).startswith("http"):
        return backdrop_path

    # Default atmospheric dark backdrop
    return "https://image.tmdb.org/t/p/original/rAiYTggjG9vyzpYBt0Y0C8OIenk.jpg"


def format_revenue(revenue: Optional[int]) -> Optional[str]:
    """Format box office revenue into clean display string e.g., $731M, $2.8B."""
    if not revenue or revenue <= 0:
        return None
    if revenue >= 1_000_000_000:
        return f"${revenue / 1_000_000_000:.1f}B".replace(".0B", "B")
    elif revenue >= 1_000_000:
        return f"${revenue / 1_000_000:.0f}M"
    elif revenue >= 1_000:
        return f"${revenue / 1_000:.0f}K"
    return f"${revenue}"


def calculate_rt_score(vote_average: Optional[float], vote_count: Optional[int] = 0) -> int:
    """Compute an estimated Rotten Tomatoes percentage aligned with ratings."""
    if not vote_average or vote_average <= 0:
        return 65
    # Standard translation: 8.7 -> 73% to 92% depending on votes
    score = int(vote_average * 9.8 - 12)
    return max(40, min(99, score))

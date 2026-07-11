from __future__ import annotations

from . import (
    aside_instagram,
    aside_linkedin,
    aside_pinterest,
    aside_threads,
    aside_tiktok,
    aside_x,
    bluesky,
    github_issues,
    hackernews,
    polymarket,
    reddit_keyless,
    web_ddg,
    youtube_ytdlp,
)


SOURCES = {
    "bluesky": bluesky.search,
    "github": github_issues.search,
    "hackernews": hackernews.search,
    "instagram": aside_instagram.search,
    "linkedin": aside_linkedin.search,
    "pinterest": aside_pinterest.search,
    "polymarket": polymarket.search,
    "reddit": reddit_keyless.search,
    "threads": aside_threads.search,
    "tiktok": aside_tiktok.search,
    "web": web_ddg.search,
    "x": aside_x.search,
    "youtube": youtube_ytdlp.search,
}

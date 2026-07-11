"""DataUpdateCoordinator for Wikipedia integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    DATA_FEATURED_ARTICLE,
    DATA_IMAGE_OF_DAY,
    DATA_ON_THIS_DAY,
    DATA_MOST_READ,
    DATA_IN_THE_NEWS,
    CONF_LANGUAGE,
    CONF_FEATURED_ARTICLE,
    CONF_IMAGE_OF_DAY,
    CONF_ON_THIS_DAY,
    CONF_ON_THIS_DAY_COUNT,
    CONF_MOST_READ,
    CONF_IN_THE_NEWS,
    CONF_IN_THE_NEWS_COUNT,
    DEFAULT_ON_THIS_DAY_COUNT,
    DEFAULT_IN_THE_NEWS_COUNT,
    SUPPORTED_LANGUAGES,
)

_LOGGER = logging.getLogger(__name__)

USER_AGENT = (
    "ha-wikipedia/1.0 (Home Assistant Integration; "
    "https://github.com/DevAvalanche/ha-wikipedia)"
)

REQUEST_TIMEOUT = 20
MAX_EXTRACT_CHARS = 800
MAX_STORY_CHARS = 300

_SAFE_URL_SCHEMES = ("https://", "http://")


def _safe_url(url: Any) -> str:
    if not isinstance(url, str):
        return ""
    if url.startswith(_SAFE_URL_SCHEMES):
        return url
    return ""


def _safe_str(value: Any, max_len: int = 255) -> str:
    if value is None:
        return ""
    return str(value)[:max_len]


def _strip_html(text: str) -> str:
    from html.parser import HTMLParser

    class _S(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self._p: list[str] = []

        def handle_data(self, data: str) -> None:
            self._p.append(data)

        def get_text(self) -> str:
            return "".join(self._p).strip()

    s = _S()
    s.feed(text)
    return s.get_text()


class WikipediaDataUpdateCoordinator(DataUpdateCoordinator):
    """Fetch Wikipedia daily content once per update cycle."""

    def __init__(self, hass: HomeAssistant, update_interval: timedelta, options: dict) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)
        self.options = options
        raw = options.get(CONF_LANGUAGE, "en")
        self.language = raw if raw in SUPPORTED_LANGUAGES else "en"

    async def _async_update_data(self) -> dict[str, Any]:
        now = datetime.utcnow()
        y, m, d = now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")
        result: dict[str, Any] = {}

        try:
            async with async_timeout.timeout(REQUEST_TIMEOUT):
                async with aiohttp.ClientSession(headers={"User-Agent": USER_AGENT}) as session:
                    feed = await self._get(session,
                        f"https://api.wikimedia.org/feed/v1/wikipedia/{self.language}/featured/{y}/{m}/{d}"
                    )

                    if self.options.get(CONF_FEATURED_ARTICLE, False):
                        self._tfa(feed, result)

                    if self.options.get(CONF_IMAGE_OF_DAY, True):
                        self._image(feed, result)

                    if self.options.get(CONF_MOST_READ, False):
                        self._mostread(feed, result)

                    if self.options.get(CONF_IN_THE_NEWS, True):
                        count = int(self.options.get(CONF_IN_THE_NEWS_COUNT, DEFAULT_IN_THE_NEWS_COUNT))
                        self._news(feed, result, count)

                    if self.options.get(CONF_ON_THIS_DAY, True):
                        count = int(self.options.get(CONF_ON_THIS_DAY_COUNT, DEFAULT_ON_THIS_DAY_COUNT))
                        otd = await self._get(session,
                            f"https://{self.language}.wikipedia.org/api/rest_v1/feed/onthisday/events/{m}/{d}"
                        )
                        self._onthisday(otd, m, d, count, result)

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Wikipedia API error: {err}") from err
        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err

        return result

    def _tfa(self, feed: dict, result: dict) -> None:
        tfa = feed.get("tfa")
        if not isinstance(tfa, dict):
            return
        thumb = tfa.get("thumbnail") or {}
        urls = tfa.get("content_urls") or {}
        result[DATA_FEATURED_ARTICLE] = {
            "title": _safe_str(tfa.get("title")),
            "displaytitle": _safe_str(tfa.get("displaytitle") or tfa.get("title")),
            "description": _safe_str(tfa.get("description")),
            "extract": _safe_str(tfa.get("extract"), MAX_EXTRACT_CHARS),
            "url": _safe_url((urls.get("desktop") or {}).get("page")),
            "thumbnail_url": _safe_url(thumb.get("source")),
        }

    def _image(self, feed: dict, result: dict) -> None:
        img = feed.get("image")
        if not isinstance(img, dict):
            return
        full = img.get("image") or {}
        thumb = img.get("thumbnail") or {}
        result[DATA_IMAGE_OF_DAY] = {
            "title": _safe_str(img.get("title")).replace("File:", "").replace("_", " "),
            "description": _safe_str((img.get("description") or {}).get("en"), 400),
            "image_url": _safe_url(full.get("source")),
            "thumbnail_url": _safe_url(thumb.get("source")),
            "credit": _safe_str((img.get("credit") or {}).get("text")),
            "license": _safe_str((img.get("license") or {}).get("type"), 50),
            "file_page": _safe_url(img.get("file_page")),
        }

    def _mostread(self, feed: dict, result: dict) -> None:
        mr = feed.get("mostread") or {}
        articles = mr.get("articles")
        if not isinstance(articles, list) or not articles:
            return
        top = articles[0] if isinstance(articles[0], dict) else {}
        result[DATA_MOST_READ] = {
            "top_title": _safe_str(top.get("title")),
            "top_views": int(top.get("views") or 0),
            "top_url": _safe_url((top.get("content_urls") or {}).get("desktop", {}).get("page")),
            "top_thumbnail": _safe_url((top.get("thumbnail") or {}).get("source")),
            "top_description": _safe_str(top.get("description")),
            "date": _safe_str(mr.get("date"), 30),
            "articles": [
                {
                    "rank": i + 1,
                    "title": _safe_str(a.get("title")),
                    "views": int(a.get("views") or 0),
                    "description": _safe_str(a.get("description")),
                    "url": _safe_url((a.get("content_urls") or {}).get("desktop", {}).get("page")),
                    "thumbnail": _safe_url((a.get("thumbnail") or {}).get("source")),
                }
                for i, a in enumerate(articles[:3])
                if isinstance(a, dict)
            ],
        }

    def _news(self, feed: dict, result: dict, count: int = 3) -> None:
        news = feed.get("news")
        if not isinstance(news, list) or not news:
            return
        result[DATA_IN_THE_NEWS] = {
            "count": min(len(news), count),
            "stories": [
                {
                    "story": _strip_html(_safe_str(s.get("story"), MAX_STORY_CHARS)),
                    "url": _safe_url(
                        ((s.get("links") or [{}])[0].get("content_urls") or {})
                        .get("desktop", {}).get("page")
                    ),
                    "thumbnail": _safe_url(
                        ((s.get("links") or [{}])[0].get("thumbnail") or {}).get("source")
                    ),
                }
                for s in news[:count]
                if isinstance(s, dict)
            ],
        }

    def _onthisday(self, otd: dict, month: str, day: str, count: int, result: dict) -> None:
        events = otd.get("events")
        if not isinstance(events, list) or not events:
            return
        historical = [
            e for e in events
            if isinstance(e, dict) and int(e.get("year", 9999)) < 1990
        ]
        sliced = historical[:count]
        result[DATA_ON_THIS_DAY] = {
            "count": len(sliced),
            "date": f"{int(day):02d}/{int(month):02d}",
            "events": [
                {
                    "year": _safe_str(e.get("year"), 10),
                    "text": _safe_str(e.get("text"), 300),
                    "url": _safe_url(
                        ((e.get("pages") or [{}])[0].get("content_urls") or {})
                        .get("desktop", {}).get("page")
                    ),
                    "thumbnail": _safe_url(
                        ((e.get("pages") or [{}])[0].get("thumbnail") or {}).get("source")
                    ),
                }
                for e in sliced
                if isinstance(e, dict)
            ],
        }

    async def _get(self, session: aiohttp.ClientSession, url: str) -> dict:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json(content_type=None)
                _LOGGER.warning("Wikipedia API HTTP %s for %s", resp.status, url)
                return {}
        except Exception as err:
            _LOGGER.warning("Failed to fetch %s: %s", url, err)
            return {}

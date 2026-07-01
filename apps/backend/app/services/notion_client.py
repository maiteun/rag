from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

import httpx

from app.core.errors import AppError


@dataclass
class NotionPageContent:
    page_id: str
    title: str
    url: str | None
    text: str
    parent_page_id: str | None = None
    child_page_ids: list[str] = field(default_factory=list)


class NotionClient:
    def __init__(self, token: str, notion_version: str):
        self.token = token
        self.notion_version = notion_version
        self.base_url = "https://api.notion.com/v1"

    def iter_accessible_page_ids(self, max_pages: int) -> Iterator[str]:
        cursor = None
        yielded = 0
        while yielded < max_pages:
            payload: dict[str, Any] = {"filter": {"property": "object", "value": "page"}, "page_size": 100}
            if cursor:
                payload["start_cursor"] = cursor
            data = self._request("POST", "/search", json=payload)
            for item in data.get("results", []):
                if item.get("object") == "page" and item.get("id"):
                    yield item["id"]
                    yielded += 1
                    if yielded >= max_pages:
                        return
            if not data.get("has_more"):
                return
            cursor = data.get("next_cursor")

    def retrieve_page_content(self, page_id: str) -> NotionPageContent:
        page = self._request("GET", f"/pages/{page_id}")
        title = self._page_title(page) or "Untitled Notion page"
        lines = [f"# {title}"]
        child_page_ids: list[str] = []

        for block in self._iter_block_children(page_id):
            text = self._block_text(block)
            if text:
                lines.append(text)
            if block.get("type") == "child_page" and block.get("id"):
                child_page_ids.append(block["id"])

        parent = page.get("parent") or {}
        parent_page_id = parent.get("page_id") if parent.get("type") == "page_id" else None
        return NotionPageContent(
            page_id=page_id,
            title=title,
            url=page.get("url"),
            text="\n".join(lines).strip(),
            parent_page_id=parent_page_id,
            child_page_ids=child_page_ids,
        )

    def _iter_block_children(self, block_id: str) -> Iterator[dict[str, Any]]:
        cursor = None
        while True:
            params: dict[str, Any] = {"page_size": 100}
            if cursor:
                params["start_cursor"] = cursor
            data = self._request("GET", f"/blocks/{block_id}/children", params=params)
            for block in data.get("results", []):
                yield block
                if block.get("has_children") and block.get("type") != "child_page":
                    yield from self._iter_block_children(block["id"])
            if not data.get("has_more"):
                return
            cursor = data.get("next_cursor")

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": self.notion_version,
        }
        try:
            response = httpx.request(method, f"{self.base_url}{path}", headers=headers, timeout=30, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise AppError(
                exc.response.status_code,
                "notion_api_error",
                f"Notion API request failed: {exc.response.text}",
            ) from exc
        except httpx.HTTPError as exc:
            raise AppError(502, "notion_api_unavailable", str(exc)) from exc

    @classmethod
    def _page_title(cls, page: dict[str, Any]) -> str | None:
        for prop in (page.get("properties") or {}).values():
            if prop.get("type") == "title":
                title = cls._rich_text_plain(prop.get("title") or [])
                if title:
                    return title
        return None

    @classmethod
    def _block_text(cls, block: dict[str, Any]) -> str | None:
        block_type = block.get("type")
        value = block.get(block_type or "") or {}
        if block_type == "child_page":
            title = value.get("title")
            return f"## {title}" if title else None
        if block_type == "to_do":
            checked = "x" if value.get("checked") else " "
            text = cls._rich_text_plain(value.get("rich_text") or [])
            return f"- [{checked}] {text}" if text else None
        if block_type in {"bulleted_list_item", "numbered_list_item"}:
            text = cls._rich_text_plain(value.get("rich_text") or [])
            return f"- {text}" if text else None
        if block_type in {"paragraph", "heading_1", "heading_2", "heading_3", "quote", "callout", "toggle"}:
            text = cls._rich_text_plain(value.get("rich_text") or [])
            if not text:
                return None
            if block_type == "heading_1":
                return f"# {text}"
            if block_type == "heading_2":
                return f"## {text}"
            if block_type == "heading_3":
                return f"### {text}"
            return text
        if block_type == "code":
            text = cls._rich_text_plain(value.get("rich_text") or [])
            language = value.get("language") or ""
            return f"```{language}\n{text}\n```" if text else None
        return cls._rich_text_plain(value.get("rich_text") or []) or None

    @staticmethod
    def _rich_text_plain(rich_text: list[dict[str, Any]]) -> str:
        return "".join(item.get("plain_text", "") for item in rich_text).strip()

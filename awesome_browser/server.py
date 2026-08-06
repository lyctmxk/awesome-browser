#!/usr/bin/env python3
"""
MCP Server for Awesome List Browser.
Exposes the curated awesome lists + Hermes ecosystem as MCP tools.
"""
import json
import os
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(DATA_DIR, "data.json"), "r", encoding="utf-8") as f:
    awesome_data = json.load(f)

with open(os.path.join(DATA_DIR, "hermes_data.json"), "r", encoding="utf-8") as f:
    hermes_data = json.load(f)

# Build a flat index of all items for faster search
def build_flat_index(data, source_name, is_hermes=False):
    """Flatten all items into a searchable list."""
    items = []
    if is_hermes:
        for cat in data["categories"]:
            for sub in cat["subsections"]:
                for item in sub["items"]:
                    items.append({
                        "name": item["name"],
                        "url": item["url"],
                        "description": item.get("desc", ""),
                        "tag": item.get("tag", ""),
                        "author": item.get("author", ""),
                        "category": cat["name"],
                        "subcategory": sub["name"] if sub["name"] else cat["name"],
                        "source": source_name,
                    })
    else:
        for cat in data["categories"]:
            for item in cat["items"]:
                _add_item(items, item, cat["name"], source_name)
    return items

def _add_item(items, item, category, source_name, depth=0):
    """Recursively add items and their children."""
    items.append({
        "name": item["name"],
        "url": item.get("url"),
        "description": item.get("desc", ""),
        "category": category,
        "depth": depth,
        "source": source_name,
    })
    for child in item.get("children", []):
        _add_item(items, child, category, source_name, depth + 1)

awesome_flat = build_flat_index(awesome_data, "awesome")
hermes_flat = build_flat_index(hermes_data, "hermes", is_hermes=True)
all_items = awesome_flat + hermes_flat

# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------
mcp = FastMCP("Awesome List Browser")


@mcp.tool()
def search(
    query: str,
    source: str = "all",
    limit: int = 20,
) -> str:
    """Search awesome lists and Hermes ecosystem by keyword.

    Args:
        query: Search keyword (searches name and description).
        source: Which data source to search: 'all', 'awesome', or 'hermes'.
        limit: Maximum results to return (default 20, max 50).

    Returns:
        JSON string with search results.
    """
    q = query.lower()
    results = []
    pool = all_items if source == "all" else (
        awesome_flat if source == "awesome" else hermes_flat
    )

    for item in pool:
        if q in item["name"].lower() or q in item["description"].lower():
            results.append(item)
        elif source in ("all", "hermes") and q in item.get("author", "").lower():
            results.append(item)
        elif source in ("all", "hermes") and q in item.get("tag", "").lower():
            results.append(item)

    # Sort: exact name match > name contains > description contains
    def sort_key(item):
        name = item["name"].lower()
        desc = item["description"].lower()
        if name == q:
            return 0
        if q in name:
            return 1
        if q in desc:
            return 2
        return 3

    results.sort(key=sort_key)
    results = results[:limit]

    return json.dumps({
        "query": query,
        "source": source,
        "count": len(results),
        "total_matches": len([r for r in pool if q in r["name"].lower() or q in r["description"].lower()]),
        "results": results,
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def list_categories(source: str = "all") -> str:
    """List all categories from the awesome lists or Hermes ecosystem.

    Args:
        source: 'all', 'awesome', or 'hermes'.

    Returns:
        JSON string with category list and item counts.
    """
    result = []

    if source in ("all", "awesome"):
        for cat in awesome_data["categories"]:
            n = _count_awesome_items(cat)
            result.append({"name": cat["name"], "items": n, "source": "awesome"})

    if source in ("all", "hermes"):
        for cat in hermes_data["categories"]:
            n = sum(len(s["items"]) for s in cat["subsections"])
            if n > 0:
                result.append({
                    "name": cat["name"],
                    "items": n,
                    "subsections": len([s for s in cat["subsections"] if s["items"]]),
                    "source": "hermes",
                })

    return json.dumps({"source": source, "categories": result}, ensure_ascii=False, indent=2)


@mcp.tool()
def get_category(
    category_name: str,
    source: str = "all",
) -> str:
    """Get all items in a specific category.

    Args:
        category_name: Category name (partial match supported).
        source: 'all', 'awesome', or 'hermes'.

    Returns:
        JSON string with category items.
    """
    name_lower = category_name.lower()
    results = []

    if source in ("all", "awesome"):
        for cat in awesome_data["categories"]:
            if name_lower in cat["name"].lower():
                items = []
                for item in cat["items"]:
                    items.append(_flatten_awesome_item(item))
                results.append({
                    "name": cat["name"],
                    "source": "awesome",
                    "items": items,
                })

    if source in ("all", "hermes"):
        for cat in hermes_data["categories"]:
            if name_lower in cat["name"].lower():
                sections = []
                for sub in cat["subsections"]:
                    if sub["items"]:
                        sections.append({
                            "subcategory": sub["name"] or cat["name"],
                            "items": [
                                {
                                    "name": item["name"],
                                    "url": item["url"],
                                    "description": item.get("desc", ""),
                                    "tag": item.get("tag", ""),
                                    "author": item.get("author", ""),
                                }
                                for item in sub["items"]
                            ],
                        })
                results.append({
                    "name": cat["name"],
                    "source": "hermes",
                    "sections": sections,
                })

    return json.dumps({"category": category_name, "results": results}, ensure_ascii=False, indent=2)


@mcp.tool()
def get_stats() -> str:
    """Get overall statistics about both data sources.

    Returns:
        JSON string with statistics.
    """
    awesome_cats = len(awesome_data["categories"])
    hermes_cats = len(hermes_data["categories"])

    # Hermes tag distribution
    tags = {}
    for cat in hermes_data["categories"]:
        for sub in cat["subsections"]:
            for item in sub["items"]:
                t = item.get("tag", "") or "untagged"
                tags[t] = tags.get(t, 0) + 1

    return json.dumps({
        "awesome": {
            "source": awesome_data["source"],
            "categories": awesome_cats,
            "total_items": awesome_data["total_items"],
        },
        "hermes": {
            "source": hermes_data["source"],
            "categories": hermes_cats,
            "total_items": hermes_data["total_items"],
            "maturity": tags,
        },
        "combined_total": awesome_data["total_items"] + hermes_data["total_items"],
    }, ensure_ascii=False, indent=2)


def _count_awesome_items(cat):
    n = len(cat["items"])
    for item in cat["items"]:
        if item.get("children"):
            n += len(item["children"])
    return n


def _flatten_awesome_item(item):
    result = {
        "name": item["name"],
        "url": item.get("url"),
        "description": item.get("desc", ""),
    }
    if item.get("children"):
        result["children"] = [
            {"name": c["name"], "url": c.get("url"), "description": c.get("desc", "")}
            for c in item["children"]
        ]
    return result


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------
def main():
    """CLI entry point for `awesome-browser` command."""
    mcp.run()

if __name__ == "__main__":
    main()

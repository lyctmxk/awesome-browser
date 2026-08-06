#!/usr/bin/env python3
"""Parse the awesome README.md into structured JSON."""
import re, json

def parse_readme(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    categories = []
    current_cat = None
    # Stack: list of (indent_level, parent_item)
    item_stack = [(-1, None)]  # sentinel

    lines = content.split('\n')
    in_body = False

    for line in lines:
        # Detect category headers: ## CategoryName
        m = re.match(r'^##\s+(.*)', line)
        if m:
            name = m.group(1).strip()
            # Skip non-category headers (Contents, etc.)
            if name in ('Contents',):
                in_body = True
                continue
            if not in_body:
                continue
            current_cat = {
                'name': name,
                'items': []
            }
            categories.append(current_cat)
            item_stack = [(-1, None)]
            continue

        if current_cat is None:
            continue

        # Detect list items: optional whitespace prefix + "- [Name](url)" or just "- Name" (no link, acts as category header for sub-items)
        stripped = line.rstrip()
        # Skip empty lines and HTML
        if not stripped or stripped.startswith('<'):
            continue

        # Match pattern: anything before the first "- [" or "- "
        leading = line[:len(line) - len(line.lstrip())]
        indent = len(leading.replace('\t', '    '))  # normalize tabs to 4 spaces

        # Try link pattern: - [Name](url) - description  OR  - [Name](url)
        link_match = re.match(r'^- \[([^\]]+)\]\(([^)]+)\)(?:\s*-\s*(.*))?', stripped)
        # Try plain text pattern: - Name (no link)
        plain_match = re.match(r'^- (\S.*)', stripped)

        if link_match:
            name = link_match.group(1).strip()
            url = link_match.group(2).strip()
            desc = (link_match.group(3) or '').strip()

            # Determine parent
            parent = None
            while item_stack and item_stack[-1][0] >= indent:
                item_stack.pop()
            if item_stack:
                parent = item_stack[-1][1]

            item = {
                'name': name,
                'url': url,
                'desc': desc,
                'children': []
            }

            if parent is not None:
                parent['children'].append(item)
            else:
                current_cat['items'].append(item)

            item_stack.append((indent, item))

        elif plain_match:
            name = plain_match.group(1).strip()
            # A plain item without a link (like "Linux" or "macOS") acts as a grouping label
            parent = None
            while item_stack and item_stack[-1][0] >= indent:
                item_stack.pop()
            if item_stack:
                parent = item_stack[-1][1]

            item = {
                'name': name,
                'url': None,
                'desc': '',
                'children': []
            }

            if parent is not None:
                parent['children'].append(item)
            else:
                current_cat['items'].append(item)

            item_stack.append((indent, item))

    # Filter out empty categories and count items
    result = []
    for cat in categories:
        if cat['items']:
            result.append(cat)

    total_items = count_items(result)
    return {
        'source': 'https://github.com/sindresorhus/awesome',
        'categories': result,
        'total_items': total_items
    }

def count_items(categories):
    def _count(items):
        total = 0
        for item in items:
            total += 1
            if item.get('children'):
                total += _count(item['children'])
        return total
    return sum(_count(c['items']) for c in categories)

if __name__ == '__main__':
    import sys
    data = parse_readme(sys.argv[1] if len(sys.argv) > 1 else 'README.md')
    with open('C:/Users/TIA/awesome-site/data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Parsed {len(data['categories'])} categories, {data['total_items']} total items")
    for cat in data['categories']:
        n = sum(1 for _ in cat['items'])
        print(f"  {cat['name']}: {n} top-level items")

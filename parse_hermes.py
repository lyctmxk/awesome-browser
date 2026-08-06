#!/usr/bin/env python3
"""Parse the awesome-hermes-agent README into structured JSON."""
import re, json

def parse_hermes_readme(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    categories = []
    current_cat = None
    current_subcat = None
    in_body = False

    for line in lines:
        stripped = line.strip()

        # Skip header area until we hit the first ## section after Contents
        if stripped == '## Contents':
            in_body = True
            continue
        if not in_body:
            continue

        # Top-level category: ## Name
        m2 = re.match(r'^##\s+(.*)', stripped)
        if m2:
            name = m2.group(1).strip()
            # Skip special sections
            if name in ('Contents', 'Where Do I Start?', 'Check the trust boundary',
                        'Contributing', 'License', 'From this repo to a working agent OS'):
                continue
            current_cat = {
                'name': name,
                'subsections': []
            }
            current_subcat = None
            categories.append(current_cat)
            continue

        # Sub-section: ### Name
        m3 = re.match(r'^###\s+(.*)', stripped)
        if m3 and current_cat:
            subname = m3.group(1).strip()
            current_subcat = {
                'name': subname,
                'items': []
            }
            current_cat['subsections'].append(current_subcat)
            continue

        # List items: - **[tag]** [name](url) by [author](url) - desc
        # Or simpler: - [name](url) by [author](url) - desc
        item_match = re.match(
            r'^-\s+(?:\*\*\[([^\]]+)\]\*\*\s+)?'  # optional [tag]
            r'\[([^\]]+)\]\(([^)]+)\)'               # [name](url)
            r'(?:\s+by\s+\[([^\]]+)\]\(([^)]+)\))?'  # optional by [author](url)
            r'(?:\s*[-–—]\s*(.*))?',                  # - description
            stripped
        )

        if item_match and current_cat:
            tag = (item_match.group(1) or '').strip()
            name = item_match.group(2).strip()
            url = item_match.group(3).strip()
            author = (item_match.group(4) or '').strip()
            author_url = (item_match.group(5) or '').strip()
            desc = (item_match.group(6) or '').strip()

            item = {
                'name': name,
                'url': url,
                'tag': tag,
                'author': author,
                'author_url': author_url,
                'desc': desc
            }

            if current_subcat:
                current_subcat['items'].append(item)
            elif current_cat['subsections']:
                # Add to last subsection if exists
                current_cat['subsections'][-1]['items'].append(item)
            else:
                # Create a default subsection
                default_sub = {'name': '', 'items': [item]}
                current_cat['subsections'].append(default_sub)

    # Count items
    total_items = 0
    for cat in categories:
        for sub in cat['subsections']:
            total_items += len(sub['items'])

    return {
        'source': 'https://github.com/0xNyk/awesome-hermes-agent',
        'title': 'Awesome Hermes Agent',
        'categories': categories,
        'total_items': total_items
    }

if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else 'hermes_readme.md'
    data = parse_hermes_readme(path)
    with open('C:/Users/TIA/awesome-site/hermes_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Parsed {len(data['categories'])} categories, {data['total_items']} total items")
    for cat in data['categories']:
        n = sum(len(s['items']) for s in cat['subsections'])
        print(f"  {cat['name']}: {n} items ({len(cat['subsections'])} subsections)")

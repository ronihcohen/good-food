import os
import re

# Directory to scan
CONTENT_DIR = "/Users/ronih/Public/good-food/content/food"

def get_markdown_files(directory):
    md_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                md_files.append(os.path.join(root, file))
    return md_files

def fix_link(match):
    # match.group(0) is the whole link: [Text](url)
    # match.group(1) is Text
    # match.group(2) is url
    text = match.group(1)
    url = match.group(2)

    # Check if it's an external link
    if url.startswith('http') or url.startswith('//') or url.startswith('mailto:'):
        return match.group(0)
    
    # Check if it's already absolute /food/
    if url.startswith('/food/'):
        # Ensure trailing slash if it's a dir-like path (no extension)
        if not url.endswith('/') and not url.endswith('.md'):
             # heuristic: if it doesn't look like a file (no dot after last slash)
             # but "vitamin-d" has no dot. "image.png" has dot.
             # safest is to assume these are posts.
             return f'[{text}]({url}/)'
        return match.group(0)

    # Decode what this relative link points to.
    # It might be: "supplements/vitamin-d" or "../supplements/vitamin-d.md" or "cheese"
    
    # 1. Clean extension if present
    clean_url = url
    if clean_url.endswith('.md'):
        clean_url = clean_url[:-3]
        
    # 2. Try to find the target file in our map
    # The usage of basename is tricky because "vitamin-d" might be unique, but "index" isn't.
    # But usually post slugs are unique enough or we can try to guess.
    
    # If the url contains slashes, e.g. "supplements/vitamin-d", we can try to find "vitamin-d.md"
    basename = os.path.basename(clean_url)
    
    # Try to resolve to a file
    # We'll use a heuristic: match basename to known files.
    # exact match on filename (without .md)
    
    files_matching = [f for f in FILE_MAP.keys() if f == basename + '.md']
    
    target_path = None
    if len(files_matching) == 1:
        target_path = FILE_MAP[files_matching[0]]
    elif len(files_matching) > 1:
        # Ambiguity?
        # e.g. food/apple.md and food/other/apple.md?
        # Use the one that matches the path structure best?
        # For now, just pick the first? Or print warning?
        print(f"Warning: Ambiguous target for {url}: {files_matching}")
        target_path = FILE_MAP[files_matching[0]]
    else:
        # No match found by basename?
        # Maybe it's a tag or something else?
        # Or maybe it IS "cheese" and we have "cheese.md"?
        # Wait, if clean_url is "cheese", basename is "cheese".
        # If we have "cheese.md", we found it.
        pass

    if target_path:
        # Convert target_path to absolute /food/ path
        # target_path: /Users/.../content/food/supplements/vitamin-d.md
        parts = target_path.split(os.sep)
        try:
            content_index = parts.index("content")
            rel_parts = parts[content_index+1:] # food, supplements, vitamin-d.md
            
            if rel_parts[-1].endswith('.md'):
                rel_parts[-1] = rel_parts[-1][:-3]
            
            if rel_parts[-1] == "_index":
                 rel_parts.pop()
                 
            new_url = "/" + "/".join(rel_parts) + "/"
            return f'[{text}]({new_url})'
        except ValueError:
            pass

    # If we couldn't resolve it using the map, we might still want to force absolute if it looks like a relative path under food.
    # e.g. "supplements/vitamin-d" -> "/food/supplements/vitamin-d/"
    # This is a bit risky if it's not actually there.
    # But if it looks like a valid path structure...
    
    # If it starts with supplements/, modify to /food/supplements/
    if clean_url.startswith('supplements/'):
         return f'[{text}](/food/{clean_url}/)'
         
    # If it is just a word "cheese", assume "/food/cheese/" matches content/food/cheese.md
    if '/' not in clean_url and not clean_url.startswith('.'):
         return f'[{text}](/food/{clean_url}/)'

    return match.group(0)

FILE_MAP = {}

def build_file_map(files):
    map = {}
    for f in files:
        basename = os.path.basename(f)
        map[basename] = f
    return map

def main():
    print(f"Scanning {CONTENT_DIR}...")
    files = get_markdown_files(CONTENT_DIR)
    
    global FILE_MAP
    FILE_MAP = build_file_map(files)
    
    # Regex for Markdown links: [text](url)
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    
    count = 0
    for file_path in files:
        changed = False
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = link_pattern.sub(fix_link, content)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed links in {os.path.basename(file_path)}")
            count += 1
            
    print(f"Finished. Fixed files: {count}")

if __name__ == "__main__":
    main()

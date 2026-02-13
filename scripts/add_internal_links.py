import os
import re

import sys

# Default directory
DEFAULT_CONTENT_DIR = "/Users/ronih/Public/good-food/content/food"

def get_markdown_files(directory):
    md_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                md_files.append(os.path.join(root, file))
    return md_files

def parse_frontmatter(content):
    """
    Manually parses basic frontmatter to extract title.
    Returns (frontmatter_string, body_string, title)
    """
    content = content.lstrip()
    if content.startswith('---'):
        try:
            parts = content.split('---', 2)
            if len(parts) >= 3:
                fm = parts[1]
                body = parts[2]
                
                # Extract title from fm
                title = None
                for line in fm.split('\n'):
                    if line.strip().startswith('title:'):
                        # Remove 'title:' and quotes
                        title_val = line.split(':', 1)[1].strip()
                        # Handle quotes
                        if (title_val.startswith('"') and title_val.endswith('"')) or \
                           (title_val.startswith("'") and title_val.endswith("'")):
                            title_val = title_val[1:-1]
                        title = title_val
                        break
                
                return fm, body, title
        except Exception:
            pass
    return None, content, None

def build_term_map(md_files):
    term_map = {}
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            _, _, title = parse_frontmatter(content)
            
            if title:
                title = title.strip()
                # 1. Full title
                if title not in term_map:
                    term_map[title] = file_path
                
                # 2. Handle "Hebrew (English)" format
                # We want to match "Hebrew" and maybe "English"
                if '(' in title and ')' in title:
                    # simplistic check
                    match = re.match(r'(.+?)\s*\((.+?)\)', title)
                    if match:
                        hebrew_part = match.group(1).strip()
                        english_part = match.group(2).strip()
                        
                        if hebrew_part and hebrew_part not in term_map:
                            term_map[hebrew_part] = file_path
                        if english_part and english_part not in term_map:
                            term_map[english_part] = file_path
                            
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    return term_map

def get_root_relative_link(source_file, target_file):
    # Determine the "web path" of the target_file
    # target_file: /Users/ronih/Public/good-food/content/food/apple.md
    # desired: /food/apple/
    
    # We assume standard structure where content root is .../content/
    # But let's be robust: find "content" part of path
    
    parts = target_file.split(os.sep)
    try:
        content_index = parts.index("content")
        # e.g. parts[content_index] is "content"
        # path from content root: check what's after "content"
        rel_parts = parts[content_index+1:] 
    except ValueError:
        # Fallback if not in "content" dir structure (e.g. testing)
        # Just use basename without ext
        rel_parts = [os.path.basename(target_file)]

    # Remove .md extension from last part
    if rel_parts[-1].endswith(".md"):
        rel_parts[-1] = rel_parts[-1][:-3]
        
    # Handle _index special case
    if rel_parts[-1] == "_index":
        rel_parts.pop()
        
    # Build path starting with slash
    return "/" + "/".join(rel_parts) + "/"

def replace_terms_in_content(content, terms, term_map, source_file):
    # Sort by length descending
    sorted_terms = sorted(terms, key=len, reverse=True)
    
    # regex for all terms
    escaped_terms = [re.escape(t) for t in sorted_terms]
    terms_pattern_str = '|'.join(escaped_terms)
    
    # Regex to match: prefix + term + suffix
    # Prefix: [הבלמוכש]? (optional Hebrew prefix)
    # We use lookbehind/lookahead for word boundaries if possible, but simpler is just term matching.
    # Pattern: ([הבלמוכש]?)(TERM)
    regex = re.compile(r'(?<!\w)([הבלמוכש]?)(%s)(?!\w)' % terms_pattern_str)
    
    # Protected zones: code blocks, existing links, HTML tags
    # We want to capture existing links like [title](url) so we don't double link inside them.
    protected_pattern = re.compile(r'(`[^`]+`)|(\[[^\]]+\]\([^\)]+\))|(<[^>]+>)')
    
    parts = []
    last_end = 0
    
    for match in protected_pattern.finditer(content):
        start, end = match.span()
        # Process unprotected text before this match
        unprotected_text = content[last_end:start]
        if unprotected_text:
            processed = process_text_chunk(unprotected_text, regex, term_map, source_file)
            parts.append(processed)
        
        # Append protected text as is
        parts.append(match.group(0))
        last_end = end
        
    # Process remaining text
    if last_end < len(content):
        unprotected_text = content[last_end:]
        processed = process_text_chunk(unprotected_text, regex, term_map, source_file)
        parts.append(processed)
        
    return "".join(parts)

def process_text_chunk(text, regex, term_map, source_file):
    def substitution(match):
        prefix = match.group(1)
        term = match.group(2)
        
        target_path = term_map.get(term)
        if not target_path or target_path == source_file:
            return match.group(0)
            
        rel_link = get_root_relative_link(source_file, target_path)
        return f'{prefix}[{term}]({rel_link})'
        
    return regex.sub(substitution, text)

import argparse

def main():
    parser = argparse.ArgumentParser(description="Add internal links to markdown files.")
    parser.add_argument("--source", help="Directory to scan for terms (default: content/food)", default=DEFAULT_CONTENT_DIR)
    parser.add_argument("--target", help="Directory to update with links (default: same as source)", default=None)
    
    args = parser.parse_args()
    
    source_dir = args.source
    target_dir = args.target if args.target else source_dir
    
    print(f"Scanning for terms in {source_dir}...")
    source_files = get_markdown_files(source_dir)
    term_map = build_term_map(source_files)
    
    print(f"Found {len(term_map)} terms/titles.")
    terms = list(term_map.keys())
    
    print(f"Updating files in {target_dir}...")
    target_files = get_markdown_files(target_dir)
    
    count = 0
    for file_path in target_files:
        try:
            # Skip _index.md files
            if os.path.basename(file_path) == "_index.md":
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            fm, body, title = parse_frontmatter(content)
            
            if fm and body:
                new_body = replace_terms_in_content(body, terms, term_map, file_path)
                
                if new_body != body:
                    new_content = f'---{fm}---{new_body}'
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Updated {os.path.basename(file_path)}")
                    count += 1
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    print(f"Finished. Updated {count} files.")

if __name__ == "__main__":
    main()

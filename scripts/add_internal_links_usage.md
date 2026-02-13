# Auto-Linker Script Usage

The `add_internal_links.py` script automates the creation of internal Markdown links based on page titles. It scans a source directory for page titles and then scans a target directory to link those titles where they appear in the text.

## Features

- **Automatic Term Detection**: Reads `title` from YAML frontmatter in `.md` files.
- **Context-Aware Linking**:
  - Detects exact matches of titles.
  - Supports Hebrew/English format (e.g., `Title (English)` -> links both `Title` and `English`).
  - Ignores existing links, code blocks, and HTML tags.
- **Smart Path Generation**: Creates root-relative paths (e.g., `/food/apple/`) suitable for Hugo/web servers.

## Usage

### 1. Basic Usage (Link Food to Food)
Running without arguments scans `content/food` for terms and updates files in `content/food`.

```bash
python3 scripts/add_internal_links.py
```

### 2. Cross-Linking (Link Compare to Food)
Link terms found in `content/food` (source) within files in `content/compare` (target).

```bash
python3 scripts/add_internal_links.py --source content/food --target content/compare
```

### Arguments

| Argument | Description | Default |
| :--- | :--- | :--- |
| `--source` | Directory to scan for terms/titles. | `content/food` |
| `--target` | Directory to scan and update with links. | Same as `--source` |

## How It Works

1. **Build Term Map**: Scans `--source` directory.
   - Extracts `title: "..."` from frontmatter.
   - Maps the title string to the file path.
   - If title is "Cottage Cheese (גבינת קוטג')", it maps both "Cottage Cheese" and "גבינת קוטג'".
2. **Scan Text**: Scans `.md` files in `--target` directory.
   - Finds all occurrences of mapped terms.
   - Ignores terms that are already linked or inside code blocks.
3. **Rewrite**: Replaces occurrences with `[Term](/path/to/page/)`.
   - Generates absolute paths starting with `/`.
   - Removes `.md` extension.

## Example

**Source File**: `content/food/apple.md`
```yaml
---
title: "תפוח"
---
```

**Target File Before**: `content/food/pie.md`
```markdown
אני אוהב לאכול תפוח בבוקר.
```

**Target File After**: `content/food/pie.md`
```markdown
אני אוהב לאכול [תפוח](/food/apple/) בבוקר.
```

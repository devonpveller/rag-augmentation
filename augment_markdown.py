import argparse
from pathlib import Path
import re

HEADING_RE = re.compile(r'^(#{1,6})\s+(.*)$')
BOLD_HEADING_RE = re.compile(r'^\*\*([^*]+)\*\*\s*$')
COLON_HEADING_RE = re.compile(r'^([A-Z][a-zA-Z\s]{3,}):\s*$')
DATE_HEADING_RE = re.compile(r'^(20\d{2}\s+\d{2}\s+\d{2})$')
NUMBERED_HEADING_RE = re.compile(r'^(\d{1,2})\.\s+([A-Z][a-zA-Z\s]{3,})$')
ALLCAPS_HEADING_RE = re.compile(r'^([A-Z][A-Z\s]{8,})$')

def slug(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def build_header_block(doc_title, rel_path, breadcrumb, aliases):
    # Keep concise; embedding sees these tokens every chunk
    breadcrumb_str = " > ".join(breadcrumb) if breadcrumb else doc_title
    aliases_str = ", ".join(sorted(set(a for a in aliases if a)))[:120]
    lines = [
        f"[DocTitle: {doc_title}]",
        f"[Path: {rel_path}]",
        f"[Section: {breadcrumb_str}]",
    ]
    if aliases_str:
        lines.append(f"[Aliases: {aliases_str}]")
    return "\n".join(lines) + "\n\n"

def guess_aliases_from_heading(text: str):
    # very light heuristic; adjust as needed or plug a custom mapping
    # Remove common markdown formatting and special characters
    base = re.sub(r'[\(\)\[\]\{\}:,\.\"\'*_`]', ' ', text)
    # Remove underline formatting that might be present
    base = re.sub(r'\{\.underline\}', '', base)
    terms = [t for t in base.split() if len(t) >= 3]
    # keep 3–5 hint terms max
    return terms[:5]

def determine_header_level_by_context(breadcrumb, pattern_type, text):
    """
    Determine the appropriate level for different header patterns based on context.
    """
    # Date headers are typically major section dividers (level 1 or 2)
    if pattern_type == "date":
        return 1 if not breadcrumb else 2
    
    # Colon headers (like "Meeting:", "Tasks:") are usually subsections
    if pattern_type == "colon":
        # If text contains common meeting/section keywords, treat as level 2 or 3
        meeting_keywords = ["meeting", "discussion", "call", "update", "task", "notes", "todo"]
        if any(keyword in text.lower() for keyword in meeting_keywords):
            return min(len(breadcrumb) + 1, 3) if breadcrumb else 2
        return 2 if not breadcrumb else min(len(breadcrumb) + 1, 3)
    
    # Numbered headers are usually subsections or list items
    if pattern_type == "numbered":
        return min(len(breadcrumb) + 1, 4) if breadcrumb else 2
    
    # All caps headers are usually major sections
    if pattern_type == "allcaps":
        return 1 if not breadcrumb else 2
    
    # Default for other patterns
    return 2

def determine_bold_header_level(breadcrumb, lines, current_index):
    """
    Determine the appropriate level for a bold header based on context.
    Look at surrounding content to make a better guess.
    """
    # If no breadcrumb exists, treat as level 1
    if not breadcrumb:
        return 1
    
    # Look ahead to see if there's indented content following this bold header
    has_indented_content = False
    for j in range(current_index + 1, min(current_index + 10, len(lines))):
        line = lines[j].strip()
        if not line:
            continue
        if line.startswith('- ') or line.startswith('* ') or line.startswith('  '):
            has_indented_content = True
            break
        if line.startswith('**') or line.startswith('#'):
            break
            
    # If there's indented content, it's likely a section header
    # Use level 2 if we have a title, otherwise level 1
    if has_indented_content:
        return min(len(breadcrumb) + 1, 3)  # Cap at level 3
    
    # Default to level 2 for bold headers when we have existing breadcrumb
    return 2

def check_header_patterns(line):
    """
    Check a line against all header patterns and return match info.
    Returns (pattern_type, heading_text, original_match) or (None, None, None)
    """
    # Check for regular markdown headers first
    m = HEADING_RE.match(line)
    if m:
        return ("markdown", m.group(2).strip(), m)
    
    # Check for bold headers
    m = BOLD_HEADING_RE.match(line)
    if m:
        return ("bold", m.group(1).strip(), m)
    
    # Check for colon headers (but exclude very short ones or obvious lists)
    m = COLON_HEADING_RE.match(line)
    if m:
        text = m.group(1).strip()
        # Filter out obvious non-headers
        if len(text) >= 5 and not text.lower().startswith('http'):
            return ("colon", text, m)
    
    # Check for date headers
    m = DATE_HEADING_RE.match(line)
    if m:
        return ("date", m.group(1).strip(), m)
    
    # Check for numbered headers (but be selective)
    m = NUMBERED_HEADING_RE.match(line)
    if m:
        text = m.group(2).strip()
        # Only treat as header if it looks like a section title
        if len(text) >= 5:
            return ("numbered", f"{m.group(1)}. {text}", m)
    
    # Check for all caps headers (but be very selective)
    m = ALLCAPS_HEADING_RE.match(line)
    if m:
        text = m.group(1).strip()
        # Filter out obvious non-headers and be more restrictive
        common_non_headers = ['TASK', 'TODO', 'NOTE', 'IMPORTANT', 'WARNING', 'ERROR']
        if not any(word in text for word in common_non_headers) and len(text.split()) <= 6:
            return ("allcaps", text, m)
    
    return (None, None, None)

def convert_to_proper_header(text, level, pattern_type):
    """Convert various header patterns to proper markdown headers."""
    header_prefix = '#' * level
    
    if pattern_type == "date":
        # Format dates nicely
        return f"{header_prefix} {text}"
    elif pattern_type == "colon":
        # Remove the trailing colon for cleaner headers
        clean_text = text.rstrip(':')
        return f"{header_prefix} {clean_text}"
    elif pattern_type == "numbered":
        # Keep the number as part of the header
        return f"{header_prefix} {text}"
    else:
        # For bold, allcaps, and other patterns
        return f"{header_prefix} {text}"
    """Convert various header patterns to proper markdown headers."""
    header_prefix = '#' * level
    
    if pattern_type == "date":
        # Format dates nicely
        return f"{header_prefix} {text}"
    elif pattern_type == "colon":
        # Remove the trailing colon for cleaner headers
        clean_text = text.rstrip(':')
        return f"{header_prefix} {clean_text}"
    elif pattern_type == "numbered":
        # Keep the number as part of the header
        return f"{header_prefix} {text}"
    else:
        # For bold, allcaps, and other patterns
        return f"{header_prefix} {text}"

def process_markdown(md_text: str, rel_path: str, file_stem: str):
    lines = md_text.splitlines()
    out = []
    breadcrumb = []
    doc_title = file_stem  # fallback; will be replaced if H1 found

    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check all header patterns
        pattern_type, heading_text, match = check_header_patterns(line)
        
        if pattern_type:
            # Determine the appropriate level based on pattern type
            if pattern_type == "markdown":
                level = len(match.group(1))
            elif pattern_type == "bold":
                level = determine_bold_header_level(breadcrumb, lines, i)
            else:
                level = determine_header_level_by_context(breadcrumb, pattern_type, heading_text)

            # Maintain breadcrumb
            if level == 1:
                doc_title = heading_text or doc_title
                breadcrumb = [heading_text or doc_title]
            else:
                # ensure length equals current level
                while len(breadcrumb) >= level:
                    breadcrumb.pop()
                breadcrumb.append(heading_text)

            # Convert to proper markdown header (except for already proper markdown headers)
            if pattern_type == "markdown":
                proper_header = line  # Keep original markdown headers as-is
            else:
                proper_header = convert_to_proper_header(heading_text, level, pattern_type)
            
            out.append(proper_header)

            # Avoid double-injecting if a header block already exists
            # by peeking ahead at next non-empty line
            j = i + 1
            next_nonempty = ""
            while j < len(lines) and not next_nonempty:
                if lines[j].strip():
                    next_nonempty = lines[j].strip()
                j += 1
            already_injected = next_nonempty.startswith("[DocTitle:")

            if not already_injected:
                aliases = guess_aliases_from_heading(heading_text)
                out.append(build_header_block(doc_title, rel_path, breadcrumb, aliases))
            i += 1
            continue

        out.append(line)
        i += 1

    return "\n".join(out) + ("\n" if not out or out[-1] != "" else "")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Input folder with .md files")
    ap.add_argument("--out", dest="outp", required=True, help="Output folder to write augmented .md files")
    args = ap.parse_args()

    in_dir = Path(args.inp)
    out_dir = Path(args.outp)
    out_dir.mkdir(parents=True, exist_ok=True)

    for src in in_dir.rglob("*.md"):
        rel_path = str(src.relative_to(in_dir)).replace("\\", "/")
        text = src.read_text(encoding="utf-8", errors="ignore")
        augmented = process_markdown(text, rel_path, src.stem)

        dst = out_dir / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(augmented, encoding="utf-8")
        print(f"Augmented: {rel_path}")

if __name__ == "__main__":
    main()

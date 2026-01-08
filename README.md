# Markdown Augmentation Tool

This tool automatically injects header blocks into markdown files to enhance them for vector embedding and RAG (Retrieval-Augmented Generation) systems.

## What it does

The script processes all markdown files in a directory and:

1. **Converts various pseudo-header formats to proper markdown headers**:
   - `**text**` bold headers → `# text`
   - `Text:` colon headers → `# Text`
   - `2025 07 15` date headers → `# 2025 07 15`
   - `1. Section Name` numbered headers → `## 1. Section Name`
   - `ALL CAPS TEXT` (selective) → `# All Caps Text`
   
2. **Injects structured metadata blocks** after each header containing:
   - **DocTitle**: The document title (from H1 or filename)
   - **Path**: Relative path to the file
   - **Section**: Breadcrumb navigation (H1 > H2 > H3)
   - **Aliases**: Keywords extracted from the heading text

## Example Output

**Before (with various pseudo-header styles):**
```markdown
**Installation Guide**

This is the installation guide content...

Prerequisites:

You need the following...

2025 07 15

Today's meeting notes...

1. Jeremy Myers

Working on holotable issues...
```

**After (standardized with proper headers and metadata blocks):**
```markdown
# Installation Guide

[DocTitle: Installation Guide]
[Path: guides/installation.md]
[Section: Installation Guide]
[Aliases: Installation, Guide]

This is the installation guide content...

## Prerequisites

[DocTitle: Installation Guide]
[Path: guides/installation.md]
[Section: Installation Guide > Prerequisites]
[Aliases: Prerequisites]

You need the following...

# 2025 07 15

[DocTitle: Installation Guide]
[Path: guides/installation.md]
[Section: Installation Guide > 2025 07 15]
[Aliases: 2025]

Today's meeting notes...

## 1. Jeremy Myers

[DocTitle: Installation Guide]
[Path: guides/installation.md]
[Section: Installation Guide > 2025 07 15 > 1. Jeremy Myers]
[Aliases: Jeremy, Myers]

Working on holotable issues...
```

## Usage

### Option 1: PowerShell (Recommended for Windows)
```powershell
# Use default paths (input: I:\_RAG, output: I:\_RAG_augmented)
.\augment_markdown.ps1

# Use custom paths
.\augment_markdown.ps1 -InputPath "C:\MyDocs" -OutputPath "C:\MyDocs_Augmented"
```

### Option 2: Batch File
```cmd
# Use default paths
augment_markdown.bat

# Use custom paths
augment_markdown.bat "C:\MyDocs" "C:\MyDocs_Augmented"
```

### Option 3: Direct Python
```cmd
python augment_markdown.py --in "I:\_RAG" --out "I:\_RAG_augmented"
```

## Files Created

- `augment_markdown.py` - Main Python script
- `augment_markdown.bat` - Windows batch file wrapper
- `augment_markdown.ps1` - PowerShell script wrapper
- `README.md` - This documentation

## Features

- **Comprehensive header standardization**: Converts multiple pseudo-header formats to proper markdown:
  - Bold headers (`**text**`) 
  - Colon headers (`Text:`)
  - Date headers (`2025 07 15`)
  - Numbered section headers (`1. Section Name`)
  - Selective ALL CAPS headers
- **Intelligent hierarchy detection**: Determines appropriate header levels based on context and document structure
- **Recursive processing**: Processes all `.md` files in subdirectories
- **Breadcrumb tracking**: Maintains proper heading hierarchy across all header types
- **Duplicate prevention**: Won't inject blocks if they already exist
- **Path preservation**: Maintains original directory structure in output
- **Encoding safe**: Handles UTF-8 encoding properly
- **Error handling**: Continues processing even if individual files fail

## Customization

You can modify the `guess_aliases_from_heading()` function in `augment_markdown.py` to customize how aliases are generated from heading text.

## Requirements

- Python 3.6 or higher
- No additional Python packages required (uses only standard library)

## Notes

- The original files are preserved; processed files are written to the output directory
- **Multiple pseudo-header formats are automatically converted to proper markdown headers:**
  - `**text**` → `# text`
  - `Text:` → `# Text` 
  - `2025 07 15` → `# 2025 07 15`
  - `1. Section` → `## 1. Section`
  - Selective ALL CAPS → proper headers
- Header levels are intelligently determined based on context and document structure
- If a header block already exists (detected by `[DocTitle:` at the start), it won't be duplicated
- Aliases are automatically limited to 5 keywords and 120 characters to keep blocks concise
- Empty headings are handled gracefully using the filename as fallback

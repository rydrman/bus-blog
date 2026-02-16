#!/usr/bin/env bash
#
# Migrate WordPress blog to Hugo using wp2hugo
# 
# Prerequisites:
# 1. Export your WordPress site: WordPress Admin → Tools → Export → All content
# 2. Save the XML file as wordpress-export.xml in this directory
# 3. Download wp2hugo from https://github.com/ashishb/wp2hugo/releases
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
EXPORT_FILE="${1:-$PROJECT_ROOT/wordpress-export.xml}"
WP2HUGO_BIN="${WP2HUGO:-wp2hugo}"
OUTPUT_DIR="$PROJECT_ROOT/hugo-export"

cd "$PROJECT_ROOT"

if [[ ! -f "$EXPORT_FILE" ]]; then
    echo "Error: WordPress export file not found: $EXPORT_FILE"
    echo ""
    echo "To export your WordPress content:"
    echo "  1. Log into bus.thebottriells.com/wp-admin"
    echo "  2. Go to Tools → Export"
    echo "  3. Select 'All content' and download"
    echo "  4. Save the file as wordpress-export.xml in $PROJECT_ROOT"
    echo ""
    echo "Usage: $0 [path-to-export.xml]"
    exit 1
fi

if ! command -v "$WP2HUGO_BIN" &>/dev/null; then
    echo "Error: wp2hugo not found. Install it first:"
    echo ""
    echo "  # Download from https://github.com/ashishb/wp2hugo/releases"
    echo "  # Or with Go: go install github.com/ashishb/wp2hugo/src/wp2hugo@latest"
    echo ""
    echo "  # Or set WP2HUGO to path of binary:"
    echo "  export WP2HUGO=/path/to/wp2hugo"
    exit 1
fi

echo "Converting WordPress export to Hugo..."
echo "  Source: $EXPORT_FILE"
echo "  Output: $OUTPUT_DIR"
echo ""

"$WP2HUGO_BIN" \
    --source "$EXPORT_FILE" \
    --download-media \
    --output "$OUTPUT_DIR" \
    --continue-on-media-download-error

echo ""
echo "Migration complete! Output is in $OUTPUT_DIR"
echo ""
echo "Next steps:"
echo "  1. Copy content: cp -r $OUTPUT_DIR/content/* $PROJECT_ROOT/content/"
echo "  2. Copy static assets: cp -r $OUTPUT_DIR/static/* $PROJECT_ROOT/static/ 2>/dev/null || true"
echo "  3. Review hugo.toml - merge any settings from $OUTPUT_DIR/hugo.toml if needed"
echo "  4. Delete placeholder: rm $PROJECT_ROOT/content/posts/placeholder.md"
echo "  5. Test locally: hugo server"
echo "  6. Build: hugo"
echo ""

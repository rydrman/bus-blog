#!/usr/bin/env python3
"""
Download images from WordPress URLs in Hugo content and update markdown to use local paths.

Use this script if you used the WordPress-to-Hugo-Exporter plugin instead of wp2hugo,
and your content still has image URLs pointing to bus.thebottriells.com.

Usage:
  python scripts/download-wp-images.py [content_dir]

Scans all .md files for image URLs, downloads them to static/images/, and updates the content.
"""

import re
import sys
import os
import urllib.request
import urllib.parse
from pathlib import Path
from urllib.error import URLError, HTTPError

# Default WordPress domain to look for
WP_DOMAIN = "bus.thebottriells.com"

# Image URL pattern - matches markdown images and HTML img tags
IMG_PATTERNS = [
    # Markdown: ![alt](url)
    (r'!\[([^\]]*)\]\(([^)]+)\)', 2),
    # HTML: <img src="url" ...>
    (r'<img[^>]+src=["\']([^"\']+)["\']', 1),
    # Hugo shortcode: {{< figure src="url" ...>}}
    (r'src=["\']([^"\']+)["\']', 1),
]


def extract_image_urls(text: str) -> list[str]:
    """Extract all image URLs from content that point to WordPress."""
    urls = set()
    for pattern, group in IMG_PATTERNS:
        for match in re.finditer(pattern, text):
            url = match.group(group)
            if WP_DOMAIN in url or url.startswith("/wp-content/"):
                # Normalize URL
                if url.startswith("//"):
                    url = "https:" + url
                elif url.startswith("/"):
                    url = f"https://{WP_DOMAIN}" + url
                elif not url.startswith("http"):
                    url = f"https://{WP_DOMAIN}/" + url
                urls.add(url)
    return list(urls)


def download_image(url: str, dest_dir: Path) -> Path | None:
    """Download image and return local path relative to static/."""
    try:
        parsed = urllib.parse.urlparse(url)
        # Extract path like /wp-content/uploads/2024/01/image.jpg
        path = parsed.path
        if "/wp-content/uploads/" in path:
            rel_path = path.split("/wp-content/uploads/", 1)[1]
        else:
            # Use URL path as filename
            rel_path = path.strip("/").replace("/", "_")
        
        dest = dest_dir / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        if dest.exists():
            return Path("images") / rel_path
        
        req = urllib.request.Request(url, headers={"User-Agent": "Hugo-Migration/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            dest.write_bytes(resp.read())
        
        return Path("images") / rel_path
    except (URLError, HTTPError, OSError) as e:
        print(f"  Warning: Failed to download {url}: {e}", file=sys.stderr)
        return None


def update_content(text: str, url_map: dict[str, str]) -> str:
    """Replace WordPress image URLs with local paths in content."""
    result = text
    for old_url, new_path in sorted(url_map.items(), key=lambda x: -len(x[0])):
        # Use Hugo's path format
        new_ref = f"/{new_path}"
        result = result.replace(old_url, new_ref)
        # Also replace without protocol for relative-ish URLs
        result = result.replace(old_url.replace("https://", "//"), new_ref)
    return result


def main():
    content_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "content"
    static_dir = Path(__file__).parent.parent / "static"
    images_dir = static_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    if not content_dir.exists():
        print(f"Error: Content directory not found: {content_dir}")
        sys.exit(1)
    
    all_urls = set()
    file_urls = {}  # file -> list of urls
    
    for md_file in content_dir.rglob("*.md"):
        text = md_file.read_text(encoding="utf-8", errors="replace")
        urls = extract_image_urls(text)
        if urls:
            all_urls.update(urls)
            file_urls[md_file] = urls
    
    if not all_urls:
        print("No WordPress image URLs found in content.")
        return
    
    print(f"Found {len(all_urls)} unique image URLs in {len(file_urls)} files")
    
    url_map = {}
    for url in all_urls:
        local = download_image(url, images_dir)
        if local:
            url_map[url] = str(local)
            print(f"  Downloaded: {url.split('/')[-1]}")
    
    for md_file, urls in file_urls.items():
        text = md_file.read_text(encoding="utf-8", errors="replace")
        new_text = update_content(text, url_map)
        if new_text != text:
            md_file.write_text(new_text, encoding="utf-8")
            print(f"  Updated: {md_file}")
    
    print(f"\nDone. Downloaded {len(url_map)} images to static/images/")


if __name__ == "__main__":
    main()

# Migrating bus.thebottriells.com to Hugo + GitHub Pages

This guide walks you through archiving your WordPress blog as a static Hugo site and publishing it on GitHub Pages.

## Overview

1. **Export** content from WordPress (you do this while logged into the admin)
2. **Convert** to Hugo format using wp2hugo (handles posts, pages, images, galleries)
3. **Merge** into this Hugo site
4. **Deploy** to GitHub Pages

---

## Step 1: Export from WordPress

1. Log into your WordPress admin: **https://bus.thebottriells.com/wp-admin**
2. Go to **Tools → Export**
3. Select **"All content"**
4. Click **"Download Export File"**
5. Save the XML file as `wordpress-export.xml` in this project directory (`/home/rbottriell/work/bus-blog/`)

> **Note:** I cannot log into websites or use credentials directly. You'll need to perform this export yourself while logged in. The export includes all posts, pages, comments, and metadata—but not the actual image files (wp2hugo will download those in the next step).

---

## Step 2: Install wp2hugo

wp2hugo is a Go-based tool that converts WordPress XML exports to Hugo format and can download all your images.

**Option A: Download pre-built binary**

1. Go to https://github.com/ashishb/wp2hugo/releases
2. Download the latest `wp2hugo_*_linux_amd64.tar.gz` (or appropriate for your OS)
3. Extract and add to your PATH, or place in this project directory

**Option B: Install via Go**

```bash
go install github.com/ashishb/wp2hugo/src/wp2hugo@latest
```

**Verify installation:**

```bash
wp2hugo --help
```

---

## Step 3: Run the migration

```bash
cd /home/rbottriell/work/bus-blog
chmod +x scripts/migrate-from-wordpress.sh
./scripts/migrate-from-wordpress.sh
```

Or manually:

```bash
wp2hugo --source wordpress-export.xml --download-media --output ./hugo-export --continue-on-media-download-error
```

This creates an `hugo-export/` directory with your converted content.

---

## Step 4: Merge into the Hugo site

```bash
# Copy posts and pages
cp -r hugo-export/content/* content/

# Copy static assets (images, etc.)
cp -r hugo-export/static/* static/ 2>/dev/null || mkdir -p static

# Remove the placeholder post
rm -f content/posts/placeholder.md

# If wp2hugo generated a different config, you may want to merge settings
# diff hugo.toml hugo-export/hugo.toml
```

---

## Step 5: Configure for GitHub Pages

Edit `hugo.toml` and set `baseURL` to match your GitHub Pages URL:

- **Project page** (e.g. repo `bus-blog` under user `thebottriells`):
  ```
  baseURL = 'https://thebottriells.github.io/bus-blog/'
  ```

- **Custom domain** (if you'll use bus.thebottriells.com):
  ```
  baseURL = 'https://bus.thebottriells.com/'
  ```
  You'll also add a `CNAME` file in `static/` with `bus.thebottriells.com` and configure DNS.

---

## Step 6: Test locally

```bash
hugo server
```

Visit http://localhost:1313 and verify posts, images, and navigation look correct.

---

## Step 7: Push to GitHub and enable Pages

1. Create a new repository on GitHub (e.g. `bus-blog`)

2. Push this project:

   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/bus-blog.git
   git branch -M main
   git add .
   git commit -m "Migrate bus blog to Hugo"
   git push -u origin main
   ```

3. Enable GitHub Pages:
   - Go to **Settings → Pages**
   - Under "Build and deployment", set **Source** to **GitHub Actions**
   - The workflow in `.github/workflows/hugo.yml` will build and deploy automatically

4. After the first push, your site will be live at:
   `https://YOUR_USERNAME.github.io/bus-blog/`

---

## Alternative: WordPress plugin export

If you have plugin access and prefer not to use wp2hugo:

1. Install the [WordPress to Hugo Exporter](https://github.com/SchumacherFM/wordpress-to-hugo-exporter) plugin
2. In WordPress: **Tools → Export to Hugo**
3. Download the ZIP and extract into this project
4. Run the image download script (plugin may not bundle images):

   ```bash
   python scripts/download-wp-images.py
   ```

---

## Troubleshooting

**Images not loading:** Ensure wp2hugo ran with `--download-media`. If you used the plugin, run `download-wp-images.py`.

**Broken links:** WordPress permalinks may differ from Hugo's. Check `hugo-export/` for redirect config; wp2hugo can generate Nginx redirect rules.

**Large export timeout:** Use the CLI export or wp2hugo's `--continue-on-media-download-error` to skip failed image downloads.

**Theme issues:** This site uses the PaperMod theme. See [PaperMod docs](https://github.com/adityatelange/hugo-PaperMod/wiki) for customization.

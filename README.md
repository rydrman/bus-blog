# The Bus Blog

An archived collection of our bus adventures and travels.

**Live site:** [bus.thebottriells.com](https://bus.thebottriells.com/)

## Tech Stack

- **Static site generator:** [Hugo](https://gohugo.io/)
- **Theme:** [PaperMod](https://github.com/adityatelange/hugo-PaperMod)
- **Hosting:** GitHub Pages

## Local Development

1. Install [Hugo](https://gohugo.io/installation/) (extended version recommended)
2. Clone the repository and run the dev server:

```bash
git clone <repo-url>
cd bus-blog
hugo server -D
```

3. Open http://localhost:1313 in your browser.

## Building

```bash
hugo --minify
```

Output is written to the `public/` directory.

## Deployment

The site deploys automatically to GitHub Pages when changes are pushed to the `main` or `master` branch. The workflow is defined in `.github/workflows/hugo.yml`.

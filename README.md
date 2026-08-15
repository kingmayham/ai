# BetterSite

A dependency-free static landing page that can be published for free.

## Get a free website URL

The easiest free domain-style URL for this project is GitHub Pages. It gives you a free address like:

```text
https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/
```

### Publish with GitHub Pages

1. Push this repository to GitHub.
2. Open the repository on GitHub.
3. Go to **Settings → Pages**.
4. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
5. Select the current branch and the `/ (root)` folder.
6. Click **Save**.
7. Wait for GitHub to show your live `github.io` URL.

## Optional custom free subdomain providers

If you do not want to use the default GitHub Pages URL, you can also publish the same `index.html` on static hosts that provide free subdomains, such as:

- Netlify: `YOUR-SITE.netlify.app`
- Vercel: `YOUR-SITE.vercel.app`
- Cloudflare Pages: `YOUR-SITE.pages.dev`

You do not need to change the HTML for any of these hosts. Upload or connect the repository and set the project root as the publish directory.

## Files

- `index.html` — the complete website.
- `.nojekyll` — tells GitHub Pages to serve the static files directly.

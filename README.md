# millenniumchambers.in

Source for the Millennium Chambers website, served free by GitHub Pages from the `docs/` folder.

## Updating the site

1. Edit or add a page in `content/<url-slug>.md` (first line `# Page title`).
2. Add or update its entry in `pages.json` (SEO title, meta description, page type, optional image).
3. Run `python3 build.py` (needs `pip install markdown`). This regenerates `docs/`, including `sitemap.xml` and `llms.txt`.
4. Commit and push to `main`. GitHub Pages publishes in about a minute.

`docs/assets/` holds the stylesheet, favicon and images. Photos are from Unsplash, free under the Unsplash License.

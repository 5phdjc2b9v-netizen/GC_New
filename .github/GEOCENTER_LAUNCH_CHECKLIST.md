# GeoCenter Cloudflare Launch Checklist (2026-11-15)

## Verified technical state
- GitHub: `5phdjc2b9v-netizen/GC_New`, production branch `relaunch-v1`.
- Cloudflare Pages project: `geocenter-site`, URL: https://geocenter-site.pages.dev .
- GitHub-to-Cloudflare auto-deploy enabled and verified.
- Cloudflare account currently contains no DNS zones; the `gc-new` Worker is separate and has no verified public hostname. Do not delete it without a separate decision.
- **Do not change** `geocenter.de` DNS, nameservers, MX, mail settings, or the public site before a planned migration.

## Seobility
- Site Audit project ID: `1038109` (Cloudflare preview domain).
- Crawl #2: 82/100 (technical & meta 79, structure 90, content 76).
- Crawl #3 after URL clean-up, metadata, and introductory text changes: 91/100 (technical & meta 89, structure 100, content 83).
- New crawls should follow every meaningful deployment, with the latest completed crawl as the benchmark.

## Launch blockers and decisions
1. **Legal pages:** Current preview footer is missing working local Impressum/Datenschutz/AGB pages. Live legacy pages exist at https://www.geocenter.de/impressum-agb and https://www.geocenter.de/datenschutz. They must be migrated and reviewed, because the current Datenschutzerklaerung mentions Wix-era services (e.g. contact form/other tools) and may not describe the new Cloudflare infrastructure. Also review current managing directors in the legal notice.
2. **Catalogue files:** `programm.html` links to several https://www.geocenter.de/_files/ugd/... PDFs hosted by the legacy Wix website; these paths must remain reachable or be migrated before DNS cutover. Several buttons also link to legacy `www.geocenter.de/programm`, which would become circular after cutover.
3. **Image weight:** Seobility reports 6 oversized assets: `assets/images/trade/boutique-coffee-table.jpg`, `assets/images/about/frankfurt-book-fair-exterior.jpg`, and four catalogue PNGs (naturzeit, gestalten, biber-butzemann, kleine-gestalten). Compress/re-encode with visual QA before replacing files.
4. **SEO domain switch:** After the final hostname is in Cloudflare, decide primary domain (usually `www.geocenter.de`), add canonical URLs and a production sitemap, and maintain redirects from the legacy URL inventory. Do not use a staging-domain sitemap as the permanent public sitemap.
5. **Content tradeoffs:** Seobility flags a few concise B2B pages as having relatively little text and flags a decorative image with empty alt. Avoid stuffing text or compromising accessibility just to raise a numerical audit score.
6. Verify full mobile/desktop visuals and representative links manually before launch.

## Working principle
Improve SEO without sacrificing the intentionally concise, premium B2B design or inventing sales commitments. Keep all changes reversible in Git history.


## Tally forms (15.11.2026)
- Published: general inquiries https://tally.so/r/RWME19 (embedded in `kontakt.html`).
- Published: structured publisher qualification https://tally.so/r/0VBNzy (embedded in `potentialanalyse.html`).
- Forms load through `assets/js/tally-embed.js` and support a no-JS fallback to public Tally links.
- Potential form: 3 steps (program/publisher, channels/data/needs, contact), approximate title count and annual turnover range with opt-out, CAPTCHA, thank-you page.
- **Before public launch:** adapt and legally review privacy policy for Tally as external form processor, any cookies/third-party resources, data processing agreement and data retention. Consider whether consent management is necessary.
- **Routing blocker:** Tally plan does not permit custom owner notification recipients; requested delivery to `vertrieb@geocenter.de` was NOT applied. Default Tally owner notifications remain, and submissions are stored in the connected Tally account. Configure workflow/routing or upgrade plan before relying on reception by GeoCenter team.
- Advanced form dimensions/borders need Tally Pro to appear in published forms. Primary GeoCenter red, typography and basic theme were configured on both.
- Confirm actual iframe rendering on desktop and mobile and perform a test submission without confidential real data before production domain cutover.

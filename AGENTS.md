# Instructions for the next AI maintainer

This is an independently edited student life/study journal, not an official school website. Links to school resources are permitted. Preserve student editorial attribution and existing source/photo credits.

## Scope and source of truth

- Read `README.md`, `docs/MAINTAINING.md`, and the target Markdown source before editing. The Chinese maintenance guide remains available as a reference.
- Edit articles in `content/<lang>/<kind>/<slug>.md`. Never hand-edit generated `dist/`.
- Do not rerun `tools/import_existing.py`: the one-time snapshot extraction predates current edits.
- Use standard-library Python 3.9+. Do not add dependency services, online AI APIs, databases, reader logins, tracking or paid tooling for routine updates.
- The user has approved preparing a club-owned GitHub organization, source repository and publishing setup using their existing login. Do not change the existing Netlify site. Routine future article edits start with a local preview; preserve the current `PUBLISH_SITE` state and publish only when the maintainer requests publication. Read `docs/GitHub发布与恢复.md` before changing release settings.
- No personal emails, personal account identifiers, passwords, tokens or recovery codes in source/output. External source authors' required photo attribution must remain.

## Editorial rules

- English is the default public language: the site root, navigation, generic error page, repository welcome page and main handover instructions should be English. Preserve explicit Chinese and other language routes and the language switcher. New notes should include English; do not change the default based on the maintainer's chat language.
- Natural, concrete language: a clear question, short introduction, one useful takeaway, readable sections, sources. Never manufacture first-person experience or endorse a rental/business as vetted.
- `edited` records writing changes. `checked` records actual source review. Never update `checked` solely because the template or layout changed.
- Verify changeable facts at primary sources when adding/updating them. Preserve uncertainty and eligibility/cost distinctions. Do not call a service free if only a trial or some features are free.
- Existing imported facts have their original 2026-10-08/17/18 check dates. They were not all reverified during the redesign.
- Maintain Chinese and English where available. If adding only one language, the catalog automatically marks fallback languages. Do not claim all eleven languages are fully translated.
- Keep published `kind` and `slug` stable. If changing a route, add the old-to-new key in `theme/aliases.json` and verify it.
- Homepage curated starting/seasonal notes live in `theme/editorial.json`. New/updated notes automatically appear by `edited` date; do not hardcode article bodies in the builder.
- Markdown supports paragraphs, `##`–`####` headings, flat ordered/unordered lists, bold, inline code, links, blockquotes, tables, standalone images. No raw HTML, scripts, nested lists or complex YAML. Metadata is one scalar per line; commas separate `tags` and `related`.
- Use `/assets/...` for local images and HTTPS for external resource links; preserve credits and alt text. Avoid adding the same screenshot as both a cover and body image.

## Verify before handoff

1. Run `python3 tools/build.py` and `python3 tools/check.py` (offline checks, no upload).
2. Start `python3 tools/preview.py --no-browser`; inspect with the available browser tool. Check desktop and narrow/mobile layout, changed article, navigation/search/language fallback and relevant old links. Reset temporary viewport after testing.
3. Do not “test” by submitting bookings, applications, messages or payment forms.
4. Report what changed, which sources were checked, which checks passed and any remaining limits. Keep the preview local unless publication is explicitly authorized.

GitHub workflow files live in `.github/workflows/`. Every push/PR is checked; the Pages workflow only runs on `main` when repository variable `PUBLISH_SITE` equals `true`. Build/check failure blocks deployment. Use the configured Pages base URL and upload only `dist`. Default local build is noindex; `--public-url` enables canonical/sitemap for a known HTTPS site root. No account credentials belong in this repository. Creating files locally does not mean GitHub settings or publication have been completed.

# ISAB Everyday Journal

Useful websites and practical notes for student life in Iowa City, independently edited by students. **English is the default language.** Readers can choose Chinese and the other available languages from the language menu.

- **Read the journal:** [isabwebsite.github.io](https://isabwebsite.github.io/)
- **Latest project files:** [club repository](https://github.com/isabwebsite/isabwebsite.github.io)
- **Check an update:** [automatic checks and publishing](https://github.com/isabwebsite/isabwebsite.github.io/actions)

## Start here — no coding needed

Open the latest project in an AI tool that can edit files. Read [Keep the journal going](docs/MAINTAINING.md), which includes a prompt you can copy into your AI tool, publishing instructions and the annual handover steps.

**Describe the change → review the local preview → approve publication.** You choose what is useful and verify the facts; the AI helps with the files and checks. You do not need the previous maintainer's AI account.

## Preview a change

On a Mac, double-click `预览.command` in this folder. Keep the preview window running while you browse. If it will not open, ask your AI tool to start the preview using this README.

The project needs Python 3.9 or newer and no extra Python packages. On Windows or Linux, ask the AI to run `python tools/preview.py` or `python3 tools/preview.py`. It will print a local address. Opening `dist/index.html` directly does not load the site's routes correctly.

Saving an article rebuilds the local preview; refresh the browser to see the change.

## Find the right file

| What you want to change | Where it lives |
| --- | --- |
| An English article | `content/en/`, one text file per article |
| A Chinese article | `content/zh/` |
| A new article | Start with [the English template](docs/ARTICLE_TEMPLATE.md) |
| Homepage recommendations | `theme/editorial.json` |
| Website design | `theme/styles.css`, `theme/site.js`, `tools/build.py` |
| AI editing and handover instructions | [docs/MAINTAINING.md](docs/MAINTAINING.md) and `AGENTS.md` |

Each article is a plain-text Markdown file: a short information section at the top, followed by the article itself. Write in natural English, show useful sources and preserve image credits. School resource links are allowed; the journal must not claim to be an official school website.

English and Chinese versions are maintained where available. Existing seasonal and weekend articles also include nine other languages. Missing translations are clearly identified; not every article has eleven translations.

`dist/` contains generated webpages. Update the articles and rebuild instead of editing those pages. Do not rerun `tools/import_existing.py`, which records the original one-time import.

## Publish an approved update

1. Get the latest project files and make changes on a working branch.
2. Ask the AI to generate the site, run `python3 tools/check.py` and open a local preview.
3. Review the writing, sources, links, language switching and mobile layout.
4. Save the proposed update as a pull request. Wait for **Check website** to pass.
5. Once approved, merge into `main`. **A push or merge to `main` automatically updates the public website.** Wait for **Publish website** to succeed, then check the live page.

Other branches run checks without publishing. The repository's `PUBLISH_SITE` variable is currently `true`. Read [the maintenance guide](docs/MAINTAINING.md) before changing publication settings or undoing an update.

The local preview is excluded from search indexing. The publishing workflow uses the actual GitHub Pages address to generate public links and a sitemap. This project currently expects a website root such as `https://isabwebsite.github.io/`, not a repository subpath.

## Pass it to the next committee

The website belongs to the [isabwebsite organization](https://github.com/isabwebsite). Keep the organization and repository; update administrators and the club contact email each year. Incoming maintainers use their own GitHub accounts. A complete project backup is useful, but does not grant account access.

At least two trusted current committee members should be organization Owners. Only the founding administrator is currently in place; the second owner and the incoming committee's independent publishing exercise still need to be arranged. After a successful handover, departing administrators can leave.

The site uses GitHub Pages under the club's Free organization plan. No personal publishing credentials, reader logins or AI API keys belong in this project. AI tools may have their own pricing. Keep recovery information outside the public repository. The old Netlify project was permanently deleted on November 6, 2026, after its published files were backed up. Its old address is retired; use the GitHub Pages address above.

Chinese reference instructions remain available in [AI维护说明](docs/AI维护说明.md), [换届交接](docs/换届交接.md) and [GitHub发布与恢复](docs/GitHub发布与恢复.md).

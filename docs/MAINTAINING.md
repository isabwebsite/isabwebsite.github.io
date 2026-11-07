# Keep the journal going

You do not need to write code. Your role is to choose useful material, check the facts and review the preview. An AI tool that can edit project files can handle the website changes.

The website opens in **English**. Keep new notes and the main maintenance instructions in English, with other language versions where available. The journal is independently edited by students. Links to school resources are welcome; do not present the journal as an official school website.

## Copy this into your AI tool

> Please read README.md, AGENTS.md and docs/MAINTAINING.md first. Help me update the ISAB Everyday Journal. English is the default language. Edit the article source files in content, keep existing article addresses and preserve image credits. Check new facts against the original sources; distinguish the writing date from the date the sources were actually checked. Build the website, run its checks and open a local preview. Explain what changed in plain English and tell me about anything you could not verify. Keep this update on a working branch until I approve publication. Do not ask me to paste passwords, access tokens or recovery codes.
>
> What I want to change: …
>
> Sources or notes I can provide: …

## Update an article

1. Open the latest version of the [club repository](https://github.com/isabwebsite/isabwebsite.github.io) in your AI tool. A tool that can only read a link may not be able to save changes.
2. Describe the change and provide useful source links. English articles live in `content/en/`; Chinese articles live in `content/zh/`.
3. Ask the AI to run `python3 tools/build.py`, then `python3 tools/check.py`, and start `python3 tools/preview.py --no-browser`. It should give you the local preview address. Some computers use `python` instead of `python3`.
4. Read the changed page. Check its title, sources, dates, costs and links. Try the language menu and a narrow window. Automated checks do not verify every claim or external website.
5. Ask the AI to save the change on a working branch and open a pull request. This is a proposed update you can review before it becomes public.
6. When you approve it and **Check website** has passed, merge into `main`. **This automatically publishes the update.** Wait for **Publish website** to succeed, then open the real website and check the result.

Use [the English article template](ARTICLE_TEMPLATE.md) for a new note. Ask the AI to replace every placeholder, including the dates and links. Keep `kind` and `slug` stable after publication so shared links continue to work.

## What the files mean

| Location | Purpose |
| --- | --- |
| `content/en/` | Editable English articles: one text file per article |
| `content/zh/` | Chinese versions |
| `assets/` | Images and their source credits |
| `theme/editorial.json` | Curated homepage recommendations |
| `theme/`, `tools/` | Website appearance and generation tools |
| `.github/workflows/` | Automatic checking and publishing |
| `dist/` | Generated webpages; rebuilt when you preview |

Edit the articles, then regenerate the website. Do not edit `dist` directly or rerun `tools/import_existing.py`, which is only a record of the original import.

The article's `edited` date records a writing change. Its `checked` date records when someone actually reviewed the sources. A language or layout change does not refresh the facts. Describe a free tier, trial or paid option accurately, and do not invent first-person experience.

## If something goes wrong

If a check fails, ask the AI to read the failed step and fix it. The publishing workflow stops when generation or checks fail, leaving the previously published site in place.

To undo an update, ask the AI to revert that particular change, preview the result and submit it as another update. Preserve other people's later work. Once approved and merged into `main`, the corrected version is published normally.

The `PUBLISH_SITE` repository variable is currently `true`. Setting it to `false` pauses future automatic publishing; it does not remove the live website or stop a run already in progress. Changing it back to `true` does not itself publish: run **Publish website** or merge an approved update.

## Hand over to the next committee

Keep the same club organization, repository and website address. Each maintainer uses their own GitHub login and AI tool. Give article editors repository **Write** access; appoint at least two trusted current committee members as organization **Owners** so they can manage the next handover.

Before the old committee leaves, have the next maintainer independently make a small change, preview it, publish an approved update and restore the original wording. Update the club contact email before the old address stops working. A contact email does not automatically give its owner GitHub access.

Give the next committee the website link, repository link and a complete project backup. Keep account recovery information separately, outside the public repository and AI chats. Remove departing administrators after the handover works.

The site uses GitHub Pages under the club's Free organization plan. No personal publishing token or AI subscription is built into the website. AI services may have their own fees. The old Netlify project was permanently deleted on November 6, 2026, after a backup of its published files. Its old address no longer serves the journal; use the GitHub Pages address.

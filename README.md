# yashtekavade.dev

A hand-rolled static site generator, modeled on [earendil-works/website](https://github.com/earendil-works/website): Markdown + YAML frontmatter → Jinja templates → plain HTML, with auto-generated social-share images and an RSS/Atom feed for posts. No React, no framework lock-in — just files.

Design concept: every project and post is framed like a pipeline "run" — a status dot, a set of tags, a timestamp — echoing the Airflow/Databricks job monitors you use daily.

## Quick start

```bash
pip install -r requirements-dev.txt
python3 build.py serve
```

Open http://localhost:8000 — the page live-reloads whenever you edit a `.md` file, template, or the CSS.

For a one-shot production build (what Vercel runs):

```bash
pip install -r requirements.txt
python3 build.py build
```

Output goes to `_build/`.

## Adding a project

Create `projects/your-slug.md`:

```markdown
---
template: project
title: Project Name
description: One-line description, used in previews and OG images.
date: 2026-01-15
status: active        # active | wip | archived
tags: [docker, aws, web]
github: https://github.com/you/repo
live: https://your-demo.com
---

Full write-up in Markdown goes here.
```

It'll automatically show up on `/projects/`, become filterable by every tag you give it, get its own OG share image, and (if recent) surface on the homepage.

## Adding a post

Same idea, under `posts/your-slug.md`, with `template: post`:

```markdown
---
template: post
title: Post Title
date: 2026-01-15
subject: One-line subject/excerpt line.
---

Post body in Markdown.
```

Posts are auto-included in `/posts/feed.rss` and `/posts/feed.atom` (most recent 15).

## Linking out to external posts (e.g. Substack)

Add a `link:` field to a post's frontmatter and it becomes an external entry: it still shows up in `/posts/`, the homepage, and the RSS/Atom feeds, but the title links straight to the external URL (opens in a new tab, with a small "↗ substack" badge) instead of generating a page on this site. No `content` body is needed — the `subject` field is used as the listing excerpt and feed description.

```markdown
---
template: post
title: Post Title
date: 2026-01-15
subject: One-line subject/excerpt line — shown in listings and the RSS feed.
link: https://yourname.substack.com/p/the-actual-post
source: substack
---
```

All 14 of your existing Substack posts are already added this way under `posts/`.

## About page

Edit `about.md` at the repo root — it's the only file you should need to touch. Frontmatter fields: `photo` (path under `/static/`, falls back to initials if missing or broken), `education`, `tech`, `experience` (each a list — see the file for the shape). Drop your actual photo at `_static/img/profile.jpg` (create the folder) to replace the initials placeholder.

## Adding new content without re-reading this whole README

`_content-templates/` has fill-in-the-blank versions of a project, a native post, and an external (Substack-style) post, plus its own instructions. The workflow: copy one, paste it into a Claude chat with details about the new thing, save the filled-in result into `projects/` or `posts/`. That folder is never built (it starts with `_`), so it's safe to leave there permanently.

## Structure

```
build.py              — the whole build system (templating, OG images, feeds, dev server)
_templates/            — Jinja (minijinja) templates
_static/                — CSS, JS, fonts — copied as-is to /static/
_index.md              — homepage content
projects/_index.md     — projects landing page content
projects/*.md          — individual projects
posts/_index.md        — blog landing page content
posts/*.md             — individual posts
```

Any other `.md` file you drop outside `_`-prefixed folders becomes a page automatically too (e.g. an `about.md` at the root → `/about/`), using the `page.html` template unless you set `template:` in its frontmatter.

## Deploying on Vercel

This repo includes a `vercel.json` that tells Vercel to run `pip3 install -r requirements.txt && python3 build.py build` and serve the `_build/` folder as static output. Steps:

1. Push this repo to GitHub.
2. In Vercel: **Add New → Project**, import the repo.
3. Framework preset: **Other**. Vercel will read `vercel.json` for the build/output settings — no changes needed.
4. Deploy.

Once you attach a custom domain (or note your final `*.vercel.app` URL), update `SITE_URL` at the top of `build.py` — it's only used for absolute URLs in OG tags and the RSS/Atom feeds, so it's safe to leave as the placeholder until then.

## Before publishing project write-ups from client/employer work

A couple of the sample project entries (Monte Carlo toolkit) are based on work done under a client engagement. Before publishing anything derived from paid/contract work, check what your employer or client actually allows you to share publicly — brand names, company names, and specific figures are often the parts that shouldn't go public even when the general technique is fine to describe. The placeholder entries flag this inline; replace them with your own vetted write-up.

## What's a placeholder right now

- All `github:`/`live:` links in `projects/*.md` are guesses at your repo naming — fix them to the real URLs.
- The LinkedIn link in the footer (`_templates/base.html`) is a placeholder — replace `REPLACE-WITH-YOUR-LINKEDIN` with your actual profile slug.
- `SITE_URL` in `build.py` is a placeholder until you have a final domain.
- The default `from:` email address on posts (`hello@yashtekavade.dev`, set in `build.py`) is a placeholder — either set a real one per-post in frontmatter or change the default.
- The bio copy on the homepage and the sample post are starting drafts — rewrite in your own voice.

## Design notes

- **Live background** — `_static/js/background.js` draws a quiet animated node-graph on a fixed canvas behind everything: nodes drift slowly, occasional pulses travel between them, echoing data moving through a pipeline. It's an original animation (not a copy of anything), respects `prefers-reduced-motion`, and pauses when the tab isn't visible.
- **Dark/light theme** — toggle button top-right, persisted in `localStorage`, defaults to system preference on first visit. All colors are CSS custom properties in `_static/css/style.css`, overridden under `:root[data-theme="dark"]`.
- **Posts use an email-style header** — Date/From/To/Subject, matching a memo/RFC format. Frontmatter fields: `date`, `from` (optional, defaults to your name + placeholder email), `to` (optional, defaults to "You").

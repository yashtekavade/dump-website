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
- `SITE_URL` in `build.py` is a placeholder until you have a final domain.
- The bio copy on the homepage and the sample post are starting drafts — rewrite in your own voice.

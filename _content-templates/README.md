# Content templates

These are reusable "fill-in-the-blank" files for adding new projects and posts without
having to remember the exact format each time.

## The workflow

1. Copy the relevant template below.
2. Paste it into a Claude chat, along with whatever you have about the new thing —
   a GitHub README, a Substack link, a rough description, whatever. Ask Claude to fill
   in the fields.
3. Save the result as a new file:
   - New project → `projects/your-project-slug.md`
   - New native post (written on this site) → `posts/your-post-slug.md`
   - New Substack post (just linking out) → `posts/your-post-slug.md`
4. Rebuild (`python3 build.py build`) or just push — it picks up automatically.

That's it. No other file needs to change — the build script reads whatever `tags`,
`status`, `github`, `live`, or `link` fields you give it.

## Files in this folder

- `project-template.md` — a project card + detail page
- `post-template-native.md` — a post written directly on this site (gets the Date/From/To/Subject email-style header)
- `post-template-external.md` — a post that just links out to something you wrote elsewhere (e.g. Substack)

This folder starts with `_`, so the build script always ignores it — safe to leave these
here permanently as reference copies.

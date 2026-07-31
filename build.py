#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["minijinja", "pyyaml", "markdown", "watchdog", "pillow"]
# ///
"""
Static site builder for yashtekavade.dev

Content model:
  - Any *.md file in the repo (outside of "_"-prefixed / "."-prefixed dirs)
    becomes a page. `_index.md` in a folder represents that folder's index.
  - Frontmatter `template:` picks which _templates/<name>.html to render with.
  - projects/*.md (except _index.md) are collected as "projects" and exposed
    to templates as a list, sorted by date desc, with tag metadata for the
    client-side filter UI.
  - posts/*.md (except _index.md) are collected as "posts" the same way, and
    also emitted as an RSS + Atom feed at /posts/feed.rss and /posts/feed.atom.

Usage:
  ./build.py          # one-shot build into _build/
  ./build.py serve    # dev server with live reload on http://localhost:8000
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import threading
import time
import traceback
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urljoin
from xml.etree import ElementTree

import yaml
import markdown as md_lib
from minijinja import Environment, safe
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
TEMPLATES_DIR = ROOT / "_templates"
STATIC_DIR = ROOT / "_static"
BUILD_DIR = ROOT / "_build"

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)

SITE_NAME = "Yashvardhan Tekavade"
# Update this once a custom domain is attached in Vercel; used for OG/RSS
# absolute URLs only, and safe to leave as a placeholder until then.
SITE_URL = os.environ.get("SITE_URL", "https://yashtekavade.vercel.app/")

FEED_LIMIT = 15
IGNORED_INDEX_FILES = {"_index.md"}
# Repo housekeeping files that happen to be .md but aren't site content
ALWAYS_IGNORED_FILENAMES = {"README.md"}

OG_IMAGE_SIZE = (1200, 630)
OG_BG = (245, 246, 244)
OG_DOT = (196, 202, 196)
OG_INK = (20, 32, 28)
OG_ACCENT = (36, 86, 219)
OG_TITLE_MAX_WIDTH = 980
OG_TITLE_MAX_LINES = 3
FONTS_DIR = STATIC_DIR / "fonts"
OG_DISPLAY_FONT = FONTS_DIR / "SpaceGrotesk.ttf"
OG_MONO_FONT = FONTS_DIR / "IBMPlexMono-Medium.ttf"


def load_template_utf8(name: str) -> str:
    """Load templates using UTF-8 regardless of the platform default encoding."""
    candidate = (TEMPLATES_DIR / name).resolve()
    candidate.relative_to(TEMPLATES_DIR.resolve())
    return candidate.read_text(encoding="utf-8")


# ---------------------------------------------------------------- content --

def parse_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    match = FRONTMATTER_RE.match(raw)
    if not match:
        return {}, raw
    data = yaml.safe_load(match.group(1)) or {}
    body = raw[match.end():]
    return data, body


def render_markdown(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    return md_lib.markdown(text, extensions=["extra", "sane_lists"])


EMAIL_ANGLE_RE = re.compile(r"<([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})>")


def linkify_email_header(value: str) -> str:
    """Turn `Name <email@domain>` into a mailto-linked version for the
    email-style post header (Date/From/To/Subject)."""
    if not value:
        return ""
    return EMAIL_ANGLE_RE.sub(
        lambda m: f'&lt;<a href="mailto:{m.group(1)}">{m.group(1)}</a>&gt;',
        value,
    )


def parse_entry_date(date_str: str) -> datetime | None:
    if not date_str:
        return None
    try:
        parsed = parsedate_to_datetime(str(date_str))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except (TypeError, ValueError):
        try:
            parsed = datetime.strptime(str(date_str), "%Y-%m-%d")
            return parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            return None


def slug_for_path(path: Path) -> str:
    rel = path.relative_to(ROOT)
    if rel.name == "_index.md":
        parent_parts = rel.parent.parts
        return "/" if not parent_parts else "/" + "/".join(parent_parts) + "/"
    without_ext = rel.with_suffix("")
    return "/" + "/".join(without_ext.parts) + "/"


def output_path_for(path: Path, build_dir: Path, frontmatter: dict[str, Any]) -> Path:
    if "output" in frontmatter:
        return build_dir / frontmatter["output"]
    rel = path.relative_to(ROOT)
    if rel.name == "_index.md":
        parent_parts = rel.parent.parts
        return build_dir / "index.html" if not parent_parts else build_dir / Path(*parent_parts) / "index.html"
    return build_dir / rel.with_suffix("") / "index.html"


def iter_markdown_files() -> list[Path]:
    files: list[Path] = []
    for root, dirs, filenames in os.walk(ROOT):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if not d.startswith(("_", "."))]
        for filename in filenames:
            if filename.endswith(".md") and filename not in ALWAYS_IGNORED_FILENAMES:
                files.append(root_path / filename)
    return files


def collect_entries(folder: str, tag_field: bool = False, date_format: str = "%b %Y") -> list[dict[str, Any]]:
    """Collect dated markdown entries from a folder (projects/ or posts/)."""
    entries_dir = ROOT / folder
    if not entries_dir.exists():
        return []

    entries = []
    for md_path in sorted(entries_dir.glob("*.md")):
        if md_path.name in IGNORED_INDEX_FILES:
            continue
        raw = md_path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(raw)
        parsed_date = parse_entry_date(frontmatter.get("date", ""))

        entry = {
            "slug": slug_for_path(md_path),
            "title": frontmatter.get("title", md_path.stem),
            "description": frontmatter.get("description", ""),
            "date": frontmatter.get("date", ""),
            "date_day": parsed_date.strftime(date_format) if parsed_date else "",
            "date_iso": parsed_date.date().isoformat() if parsed_date else "",
            "parsed_date": parsed_date,
            "subject": frontmatter.get("subject", ""),
            "status": frontmatter.get("status", "active"),
            "github": frontmatter.get("github", ""),
            "live": frontmatter.get("live", ""),
            "content": render_markdown(body),
        }
        if tag_field:
            tags = frontmatter.get("tags", []) or []
            entry["tags"] = [str(t) for t in tags]
        entries.append(entry)

    entries.sort(key=lambda e: e["parsed_date"] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return entries


# ---------------------------------------------------------- feeds (posts) --

def _format_rss_date(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")


def _absolutize_urls(content: str, base_url: str) -> str:
    url_attr_re = re.compile(r"(?P<prefix>\b(?:href|src)\s*=\s*)(?P<q>['\"])(?P<url>[^'\"]+)(?P=q)", re.IGNORECASE)
    return url_attr_re.sub(
        lambda m: f"{m.group('prefix')}{m.group('q')}{urljoin(base_url, m.group('url'))}{m.group('q')}",
        content,
    )


def _serialize_xml(root: ElementTree.Element) -> str:
    ElementTree.indent(root, space="  ")
    return ElementTree.tostring(root, encoding="unicode", xml_declaration=True)


def build_atom_feed(posts: list[dict[str, Any]]) -> str:
    ns = "http://www.w3.org/2005/Atom"
    ElementTree.register_namespace("", ns)
    feed_url = SITE_URL.rstrip("/") + "/posts/feed.atom"

    def el(name: str) -> str:
        return f"{{{ns}}}{name}"

    feed = ElementTree.Element(el("feed"))
    ElementTree.SubElement(feed, el("id")).text = feed_url
    ElementTree.SubElement(feed, el("title")).text = f"{SITE_NAME} — Posts"
    ElementTree.SubElement(feed, el("link"), {"href": SITE_URL})
    ElementTree.SubElement(feed, el("link"), {"href": feed_url, "rel": "self"})
    ElementTree.SubElement(feed, el("updated")).text = datetime.now(timezone.utc).isoformat()
    author = ElementTree.SubElement(feed, el("author"))
    ElementTree.SubElement(author, el("name")).text = SITE_NAME

    for post in posts[:FEED_LIMIT]:
        if not post["parsed_date"]:
            continue
        entry_date = post["parsed_date"].astimezone(timezone.utc).isoformat()
        post_url = SITE_URL.rstrip("/") + post["slug"]
        entry = ElementTree.SubElement(feed, el("entry"))
        ElementTree.SubElement(entry, el("id")).text = post_url
        ElementTree.SubElement(entry, el("title")).text = post["title"]
        ElementTree.SubElement(entry, el("link"), {"href": post_url})
        ElementTree.SubElement(entry, el("published")).text = entry_date
        ElementTree.SubElement(entry, el("updated")).text = entry_date
        content = ElementTree.SubElement(entry, el("content"), {"type": "html"})
        content.text = _absolutize_urls(post["content"], post_url)

    return _serialize_xml(feed)


def build_rss_feed(posts: list[dict[str, Any]]) -> str:
    atom_ns = "http://www.w3.org/2005/Atom"
    ElementTree.register_namespace("atom", atom_ns)
    rss = ElementTree.Element("rss", {"version": "2.0"})
    channel = ElementTree.SubElement(rss, "channel")
    ElementTree.SubElement(channel, "title").text = f"{SITE_NAME} — Posts"
    ElementTree.SubElement(channel, "link").text = SITE_URL
    feed_url = SITE_URL.rstrip("/") + "/posts/feed.rss"
    ElementTree.SubElement(channel, f"{{{atom_ns}}}link", {"href": feed_url, "rel": "self", "type": "application/rss+xml"})
    ElementTree.SubElement(channel, "lastBuildDate").text = _format_rss_date(datetime.now(timezone.utc))

    for post in posts[:FEED_LIMIT]:
        if not post["parsed_date"]:
            continue
        post_url = SITE_URL.rstrip("/") + post["slug"]
        item = ElementTree.SubElement(channel, "item")
        ElementTree.SubElement(item, "title").text = post["title"]
        ElementTree.SubElement(item, "link").text = post_url
        ElementTree.SubElement(item, "guid", {"isPermaLink": "true"}).text = post_url
        ElementTree.SubElement(item, "pubDate").text = _format_rss_date(post["parsed_date"])
        description = ElementTree.SubElement(item, "description")
        description.text = _absolutize_urls(post["content"], post_url)

    return _serialize_xml(rss)


def write_feeds(posts: list[dict[str, Any]], build_dir: Path) -> None:
    if not posts:
        return
    posts_dir = build_dir / "posts"
    posts_dir.mkdir(parents=True, exist_ok=True)
    (posts_dir / "feed.atom").write_text(build_atom_feed(posts), encoding="utf-8")
    (posts_dir / "feed.rss").write_text(build_rss_feed(posts), encoding="utf-8")


# --------------------------------------------------------------- OG image --

def _text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def _wrap_title(draw: ImageDraw.ImageDraw, title: str, font: ImageFont.FreeTypeFont) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in title.split():
        candidate = f"{current} {word}".strip()
        if _text_width(draw, candidate, font) <= OG_TITLE_MAX_WIDTH:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:OG_TITLE_MAX_LINES]


def generate_og_image(title: str, kicker: str, output_path: Path) -> None:
    """Generate a social-share card: dot-grid background, accent bar, kicker + title."""
    width, height = OG_IMAGE_SIZE
    image = Image.new("RGB", OG_IMAGE_SIZE, OG_BG)
    draw = ImageDraw.Draw(image)

    # dot grid, echoes the site's own background texture
    step = 26
    for y in range(0, height, step):
        for x in range(0, width, step):
            draw.ellipse((x, y, x + 2, y + 2), fill=OG_DOT)

    # left accent bar
    draw.rectangle((0, 0, 10, height), fill=OG_ACCENT)

    mono_font = ImageFont.truetype(str(OG_MONO_FONT), 26)
    draw.text((64, 56), kicker.upper(), font=mono_font, fill=OG_ACCENT)

    # fit display title
    title_font = ImageFont.truetype(str(OG_DISPLAY_FONT), 84)
    lines = _wrap_title(draw, title, title_font)
    for size in range(84, 39, -4):
        title_font = ImageFont.truetype(str(OG_DISPLAY_FONT), size)
        lines = _wrap_title(draw, title, title_font)
        line_h = draw.textbbox((0, 0), "Ag", font=title_font)[3] + 14
        if len(lines) * line_h <= 380:
            break

    line_h = draw.textbbox((0, 0), "Ag", font=title_font)[3] + 14
    y = 130
    for line in lines:
        draw.text((64, y), line, font=title_font, fill=OG_INK)
        y += line_h

    draw.text((64, height - 70), "yashtekavade.dev", font=mono_font, fill=(75, 86, 79))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, "PNG", optimize=True)


# ------------------------------------------------------------------ build --

def build_to(build_dir: Path) -> None:
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)

    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, build_dir / "static")
        print(f"  copied static assets", flush=True)

    env = Environment(loader=load_template_utf8)

    projects = collect_entries("projects", tag_field=True, date_format="%b %Y")
    posts = collect_entries("posts", tag_field=False, date_format="%d %b %Y")
    all_tags = sorted({t for p in projects for t in p.get("tags", [])})

    md_files = iter_markdown_files()
    current_year = datetime.now().year

    for md_path in md_files:
        raw = md_path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(raw)
        template_name = frontmatter.get("template", "page") + ".html"
        html_body = render_markdown(body)
        output_path = output_path_for(md_path, build_dir, frontmatter)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        slug = slug_for_path(md_path)

        is_home = slug == "/"
        is_project_detail = str(md_path.parent.name) == "projects" and md_path.name not in IGNORED_INDEX_FILES
        is_post_detail = str(md_path.parent.name) == "posts" and md_path.name not in IGNORED_INDEX_FILES

        page = dict(frontmatter)
        if "date" in page:
            parsed = parse_entry_date(page.get("date", ""))
            if parsed:
                page["date_day"] = parsed.strftime("%a, %d %b %Y") if is_post_detail else parsed.strftime("%b %Y")

        if is_post_detail:
            default_from = f"{SITE_NAME} <hello@yashtekavade.dev>"
            page["from_html"] = safe(linkify_email_header(str(page.get("from", default_from))))
            page["to"] = page.get("to", "You")

        og_image_rel = f"static/og{slug.rstrip('/')}.png" if slug != "/" else "static/og/home.png"
        kicker = "project" if is_project_detail else "post" if is_post_detail else "portfolio"
        generate_og_image(frontmatter.get("title", SITE_NAME), kicker, build_dir / og_image_rel)
        og_image_url = SITE_URL.rstrip("/") + "/" + og_image_rel
        canonical_url = SITE_URL.rstrip("/") + slug

        rendered = env.render_template(
            template_name,
            site_name=SITE_NAME,
            site_url=SITE_URL,
            title=frontmatter.get("title", SITE_NAME),
            description=frontmatter.get("description", "Yashvardhan Tekavade — data & AI engineer."),
            page=page,
            content=safe(html_body),
            slug=slug,
            projects=projects if (is_home or is_project_detail or template_name == "projects-index.html") else None,
            all_tags=all_tags if template_name == "projects-index.html" else None,
            posts=posts if (is_home or template_name == "posts-index.html") else None,
            is_projects_section=slug.startswith("/projects/"),
            is_posts_section=slug.startswith("/posts/"),
            og_image=og_image_url,
            canonical_url=canonical_url,
            page_classes="",
            current_year=current_year,
        )
        output_path.write_text(rendered, encoding="utf-8")
        print(f"  {md_path.relative_to(ROOT)} -> {output_path.relative_to(build_dir)}", flush=True)

    write_feeds(posts, build_dir)
    print(f"  wrote RSS/Atom feeds for {len(posts)} post(s)", flush=True)


def build() -> None:
    temp_dir = BUILD_DIR.with_name(f"{BUILD_DIR.name}_tmp")
    build_to(temp_dir)
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    temp_dir.replace(BUILD_DIR)


# ------------------------------------------------------------- dev server --

HOST = "0.0.0.0"
PORT = 8000
DEBOUNCE_DELAY = 0.3
IGNORE_DIRS = {"_build", "_build_tmp", ".git"}
RELOAD_EVENTS: dict[int, threading.Event] = {}
RELOAD_EVENTS_LOCK = threading.Lock()
RELOAD_SCRIPT = """
<script>
(function() {
  const es = new EventSource('/sse');
  es.onmessage = (e) => { if (e.data === 'reload') location.reload(); };
  es.onerror = () => setTimeout(() => location.reload(), 1000);
})();
</script>
"""


class LiveReloadHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == "/sse":
                self.handle_sse()
            else:
                self.handle_file_with_reload()
        except (ConnectionResetError, BrokenPipeError):
            pass

    def handle_sse(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        connection_id = id(self)
        try:
            self.wfile.write(b"data: connected\n\n")
            reload_event = threading.Event()
            with RELOAD_EVENTS_LOCK:
                RELOAD_EVENTS[connection_id] = reload_event
            while True:
                if reload_event.wait(timeout=0.1):
                    self.wfile.write(b"data: reload\n\n")
                    self.wfile.flush()
                    break
                try:
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                    break
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
            pass
        finally:
            with RELOAD_EVENTS_LOCK:
                RELOAD_EVENTS.pop(connection_id, None)

    def handle_file_with_reload(self):
        path = self.path.split("?")[0]
        if not (path.endswith(".html") or path.endswith("/") or path == "/" or "." not in path.rsplit("/", 1)[-1]):
            return super().do_GET()
        fs_path = self.translate_path(self.path)
        if os.path.isdir(fs_path):
            fs_path = os.path.join(fs_path, "index.html")
        if not os.path.isfile(fs_path) or not fs_path.endswith(".html"):
            return super().do_GET()
        with open(fs_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace("</body>", f"{RELOAD_SCRIPT}</body>") if "</body>" in content else content + RELOAD_SCRIPT
        encoded = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format, *args):
        pass


def notify_reload():
    with RELOAD_EVENTS_LOCK:
        for event in RELOAD_EVENTS.values():
            event.set()
        RELOAD_EVENTS.clear()


class BackgroundBuilder:
    def __init__(self, on_build_complete: Callable[[], None] | None = None):
        self.last_change_time = 0.0
        self.stop_event = threading.Event()
        self.build_lock = threading.Lock()
        self.is_building = False
        self.on_build_complete = on_build_complete

    def should_ignore(self, path: str) -> bool:
        try:
            parts = Path(path).relative_to(ROOT).parts
            return any(part in IGNORE_DIRS or part.startswith(("_", ".")) for part in parts)
        except ValueError:
            return True

    def _on_change(self, event):
        if event.is_directory:
            return
        paths = [event.src_path] + ([event.dest_path] if getattr(event, "dest_path", None) else [])
        if all(self.should_ignore(p) for p in paths if p):
            return
        self.last_change_time = time.time()

    def _build_loop(self):
        while not self.stop_event.is_set():
            should_build = False
            with self.build_lock:
                if self.last_change_time > 0 and time.time() - self.last_change_time > DEBOUNCE_DELAY and not self.is_building:
                    should_build = True
                    self.is_building = True
                    trigger_time = self.last_change_time
            if should_build:
                try:
                    print("Rebuilding...", flush=True)
                    build()
                    print("Done.", flush=True)
                    if self.on_build_complete:
                        self.on_build_complete()
                except Exception:
                    traceback.print_exc()
                finally:
                    with self.build_lock:
                        self.is_building = False
                        if self.last_change_time == trigger_time:
                            self.last_change_time = 0
            time.sleep(0.1)

    def start(self):
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        print("Building...", flush=True)
        build()
        print("Done.", flush=True)

        handler = FileSystemEventHandler()
        handler.on_created = handler.on_modified = handler.on_deleted = handler.on_moved = self._on_change
        self.observer = Observer()
        self.observer.schedule(handler, str(ROOT), recursive=True)
        self.observer.start()
        self.build_thread = threading.Thread(target=self._build_loop, daemon=True)
        self.build_thread.start()

    def stop(self):
        self.stop_event.set()
        self.observer.stop()
        self.observer.join()


def serve() -> None:
    builder = BackgroundBuilder(on_build_complete=notify_reload)
    builder.start()
    try:
        print(f"Serving on http://localhost:{PORT}/ with live reload")
        server = ThreadingHTTPServer((HOST, PORT), lambda *a: LiveReloadHandler(*a, directory=str(BUILD_DIR)))
        server.allow_reuse_address = True
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping...")
        builder.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the site.")
    parser.add_argument("command", nargs="?", default="build", choices=["build", "serve"])
    args = parser.parse_args()
    if args.command == "serve":
        serve()
    else:
        print("Building...", flush=True)
        build()
        print("Done.", flush=True)


if __name__ == "__main__":
    main()

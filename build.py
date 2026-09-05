"""Stitches partials/nav.html and partials/footer.html into each page in
pages/*.html, writing the finished static HTML to the repo root (what
GitHub Pages actually serves).

Edit nav/footer: change partials/nav.html or partials/footer.html.
Edit page content: change the matching file in pages/.
Then run: python build.py

Never hand-edit the generated .html files in the repo root directly --
they get overwritten the next time this runs.
"""

import re
import pathlib

ROOT = pathlib.Path(__file__).parent
PARTIALS = ROOT / "partials"
PAGES = ROOT / "pages"

NAV_KEYS = ["home", "about", "projects", "resume"]

FOOTER_EXTRA = (
    "\n      The diagrams throughout are my own — designed and built in code, not reproductions of shipped UI."
    "\n      Where a screen depicts a real shipped experience, it&rsquo;s either a redacted recreation (noted in its"
    "\n      caption) or a Microsoft-published, public screenshot (attributed) — never confidential or unreleased"
    "\n      company materials."
)

INCLUDE_RE = re.compile(r'<!--@include:(\w+)((?:\s+\w+="[^"]*")*)\s*-->')
ATTR_RE = re.compile(r'(\w+)="([^"]*)"')


def render_nav(active):
    tpl = (PARTIALS / "nav.html").read_text(encoding="utf-8")
    for key in NAV_KEYS:
        token = "{{cls_%s}}" % key
        tpl = tpl.replace(token, ' class="active"' if key == active else "")
    return tpl.rstrip("\n")


def render_footer(extra):
    tpl = (PARTIALS / "footer.html").read_text(encoding="utf-8")
    return tpl.replace("{{footer_extra}}", FOOTER_EXTRA if extra else "").rstrip("\n")


COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def strip_comments(text):
    """Drop all HTML comments from built output (source-file headers, TODOs,
    dev notes) so they aren't served publicly. Must run after include
    substitution, since @include markers are themselves HTML comments."""
    return COMMENT_RE.sub("", text)


def build_page(src_path):
    text = src_path.read_text(encoding="utf-8")

    def repl(match):
        name = match.group(1)
        attrs = dict(ATTR_RE.findall(match.group(2)))
        if name == "nav":
            return render_nav(attrs.get("active", "home"))
        if name == "footer":
            return render_footer(attrs.get("extra", "false") == "true")
        raise ValueError(f"Unknown include type: {name!r} in {src_path.name}")

    built = INCLUDE_RE.sub(repl, text)
    return strip_comments(built)


def main():
    sources = sorted(PAGES.glob("*.html"))
    if not sources:
        print("No pages found in pages/. Nothing to build.")
        return
    for src in sources:
        out = build_page(src)
        dest = ROOT / src.name
        dest.write_text(out, encoding="utf-8", newline="\n")
        print(f"built {dest.name}")
    print(f"done — {len(sources)} page(s)")


if __name__ == "__main__":
    main()

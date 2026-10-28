"""Build Neilyodog Blog as dependency-light static HTML for GitHub Pages."""

from __future__ import annotations

import html
import json
import re
import shutil
from collections import OrderedDict
from pathlib import Path
from urllib.parse import quote

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
BASE_URL = "https://neilyodoge.github.io"
SITE_TITLE = "Neilyodog Blog"
SITE_DESC = "喜欢而已"
AVATAR = "/media/collection-icon-ab376694-2204-40a0-9a1e-86920643bc4d.jpg"
HERO = "/media/site-hero.webp"
GITHUB = "https://github.com/Neilyodoge"


def read_post(path: Path, markdown: MarkdownIt) -> dict:
    source = path.read_text(encoding="utf-8")
    if not source.startswith("---\n"):
        raise ValueError(f"No frontmatter: {path}")
    _, raw_meta, body = source.split("---\n", 2)
    meta = yaml.safe_load(raw_meta)
    article_html = markdown.render(body)
    stripped = html.unescape(re.sub(r"<[^>]+>", " ", article_html))
    stripped = re.sub(r"\s+", " ", stripped).strip()
    slug = meta["source_id"]
    thumb_path = ROOT / "public" / "thumbs" / (Path(meta.get("cover") or "").stem + ".webp")
    thumbnail = f"/thumbs/{thumb_path.name}" if meta.get("cover") and thumb_path.is_file() else meta.get("cover", "")
    return {
        **meta,
        "slug": slug,
        "url": f"/article/{slug}/",
        "category_url": f"/category/{quote(meta['category'])}/",
        "tag_links": [{"name": tag, "url": f"/tag/{quote(tag)}/"} for tag in meta.get("tags", [])],
        "html": article_html,
        "plain": stripped,
        "thumbnail": thumbnail,
        "summary": meta.get("summary") or stripped[:120],
    }


def write_page(relative: str, template: str, context: dict, env: Environment) -> None:
    destination = DIST / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(env.get_template(template).render(**context), encoding="utf-8")


def main() -> None:
    markdown = MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")
    posts = [read_post(path, markdown) for path in (ROOT / "content" / "posts").glob("*.md")]
    posts.sort(key=lambda post: (post["date"], post["title"]), reverse=True)
    if DIST.is_symlink() or DIST.resolve().parent != ROOT.resolve():
        raise RuntimeError(f"Unsafe build output path: {DIST}")
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / "public", DIST)
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    categories: dict[str, list[dict]] = {}
    tags: dict[str, list[dict]] = {}
    archive: OrderedDict[str, list[dict]] = OrderedDict()
    for post in posts:
        categories.setdefault(post["category"], []).append(post)
        for tag in post.get("tags", []):
            tags.setdefault(tag, []).append(post)
        archive.setdefault(post["date"][:7], []).append(post)
    common = {
        "site_title": SITE_TITLE,
        "site_desc": SITE_DESC,
        "base_url": BASE_URL,
        "avatar": AVATAR,
        "hero": HERO,
        "github": GITHUB,
        "posts": posts,
        "recent": posts[:5],
        "post_count": len(posts),
        "category_count": len(categories),
        "tag_count": len(tags),
        "categories": categories,
        "tags": tags,
    }
    write_page("index.html", "home.html", {**common, "page_title": SITE_TITLE, "canonical": BASE_URL + "/"}, env)
    write_page("archive/index.html", "archive.html", {**common, "page_title": "归档", "canonical": BASE_URL + "/archive/", "archive": archive}, env)
    write_page("search/index.html", "search.html", {**common, "page_title": "搜索", "canonical": BASE_URL + "/search/"}, env)
    write_page("category/index.html", "taxonomy_index.html", {**common, "page_title": "分类", "canonical": BASE_URL + "/category/", "items": categories, "kind": "category"}, env)
    write_page("tag/index.html", "taxonomy_index.html", {**common, "page_title": "标签", "canonical": BASE_URL + "/tag/", "items": tags, "kind": "tag"}, env)
    write_page("about/index.html", "about.html", {**common, "page_title": "关于", "canonical": BASE_URL + "/about/"}, env)
    for category, subset in categories.items():
        route = f"/category/{quote(category)}/"
        write_page(f"category/{category}/index.html", "listing.html", {**common, "page_title": category, "canonical": BASE_URL + route, "listing_title": category, "listing_kind": "分类", "listing_posts": subset}, env)
    for tag, subset in tags.items():
        route = f"/tag/{quote(tag)}/"
        write_page(f"tag/{tag}/index.html", "listing.html", {**common, "page_title": tag, "canonical": BASE_URL + route, "listing_title": tag, "listing_kind": "标签", "listing_posts": subset}, env)
    for index, post in enumerate(posts):
        older = posts[index + 1] if index + 1 < len(posts) else None
        newer = posts[index - 1] if index else None
        write_page(
            f"article/{post['slug']}/index.html", "article.html",
            {**common, "page_title": post["title"], "description": post["summary"], "canonical": BASE_URL + post["url"], "post": post, "older": older, "newer": newer},
            env,
        )
    legacy_routes = {
        "2020/11/27/guang-xue-miao-ju": "9e4ab212-315e-4773-b6fc-f7a7558ff2de",
        "2020/11/27/tong-guo-di-san-tao-uv-ti-gao-mo-xing-jing-du": "3e196a75-9d46-4d4d-9357-22664be5b111",
        "2021/02/15/qiang-jie-xiao-guo-ti-sheng": "bdbee6c8-f0f0-4c80-8b18-6dfbf7d571f2",
        "2021/04/20/dither": "5d737f3f-fe0d-4a6b-8422-08393a49cf86",
        "2021/06/02/render-pipeline-zheng-li": "d47a3e64-61f7-4ca0-abc3-78657e4fb79b",
        "2021/10/24/shadergui": "e395c14d-ec97-402b-89c8-d7bd84d22e53",
        "2022/07/11/urp-zi-dai-hou-chu-li-gao-si-jing-shen-de-artifact": "urp-depth-of-field-artifact",
        "2022/07/11/xiao-ng-de-urp-hou-chu-li-wen-dang": "627404f1-9b81-4f89-9a60-38ad32b45e04",
        "2022/10/11/chuan-di-han-shu": "b28f4082-ee85-46b4-a3c4-5c0dcec6b64a",
        "2023/01/04/bian-su-shan-shuo-xiao-guo": "d1a23618-6182-4906-8895-982df57c1ef5",
        "2023/01/06/vfx-tou-ming-miao-bian": "bb6393c7-cb5a-4d9a-80ba-9d26d641a246",
    }
    for old_path, slug in legacy_routes.items():
        write_page(old_path + "/index.html", "redirect.html", {"target": f"/article/{slug}/"}, env)
    for old_path, target in {
        "archives": "/archive/",
        "categories": "/category/",
        "tags": "/tag/",
        "contact": "/about/",
        "message": "/about/",
        "links": "/about/",
        "page/2": "/archive/",
        "archives/page/2": "/archive/",
    }.items():
        write_page(old_path + "/index.html", "redirect.html", {"target": target}, env)
    for month in archive:
        year, number = month.split("-")
        write_page(f"archives/{year}/index.html", "redirect.html", {"target": "/archive/"}, env)
        write_page(f"archives/{year}/{number}/index.html", "redirect.html", {"target": f"/archive/#{month}"}, env)
    search = [{"title": p["title"], "date": p["date"], "category": p["category"], "tags": p["tags"], "summary": p["summary"], "plain": p["plain"], "url": p["url"], "cover": p["cover"]} for p in posts]
    (DIST / "search-index.json").write_text(json.dumps(search, ensure_ascii=False), encoding="utf-8")
    urls = ["/", "/archive/", "/search/", "/category/", "/tag/", "/about/"] + [p["url"] for p in posts]
    (DIST / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{BASE_URL}{path}</loc></url>" for path in urls) + "</urlset>", encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")
    print(f"Built {len(posts)} posts, {len(categories)} categories, {len(tags)} tags into {DIST}")


if __name__ == "__main__":
    main()

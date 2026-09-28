"""Validate content.json and generate the portfolio's browser files."""

import argparse
from datetime import date
from html import escape
import json
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent
PAGES = [
    ("home", "index.html", "Home", "Saitomu: CTF player, binary exploitation enthusiast, and low-level security learner."),
    ("about", "about.html", "About", "About Saitomu, a binary exploitation and low-level security learner based in Vietnam."),
    ("writeups", "writeups.html", "Notes & Learning", "CTF write-ups, low-level security research, and practical notes by Saitomu."),
    ("resources", "resources.html", "Resources", "Practice platforms, study notes, and documentation for exploring low-level systems."),
    ("contact", "contact.html", "Contact", "Find Saitomu on GitHub, pwnable.tw, and HackMD."),
]
EXTRA_PAGES = [
    ("writeup", "writeup.html", "Write-up", "Read a CTF write-up or research note by Saitomu."),
    ("home", "portfolio.html", "Home", PAGES[0][3]),
    ("resources", "skills.html", "Resources", PAGES[3][3]),
]


def require_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field}: expected non-empty text")
    return value


def require_list(value: object, field: str) -> list:
    if not isinstance(value, list):
        raise ValueError(f"{field}: expected a list")
    return value


def text_list(value: object, field: str) -> list:
    items = require_list(value, field)
    for index, item in enumerate(items):
        require_text(item, f"{field}[{index}]")
    return items


def canonical_url(value: object) -> str:
    url = require_text(value, "URL")
    parsed = urlsplit(url)
    if (parsed.scheme not in ("http", "https") or not parsed.hostname
            or parsed.username is not None or parsed.password is not None
            or any(char.isspace() for char in url)):
        raise ValueError("URL: use an http:// or https:// address without spaces or credentials")
    # Validate ports as well as the hostname; preserve meaningful queries and fragments.
    parsed.port
    return urlunsplit((parsed.scheme, parsed.netloc.lower(), parsed.path.rstrip("/"), parsed.query, parsed.fragment))


def validate_content(data: object, root: Path = ROOT) -> None:
    if not isinstance(data, dict):
        raise ValueError("content.json: expected an object")
    categories = text_list(data.get("categories"), "categories")
    if not categories or len(categories) != len(set(categories)):
        raise ValueError("categories: provide at least one unique category")
    if any(not re.fullmatch(r"[A-Z][A-Z0-9_-]*", item) or item == "ALL" for item in categories):
        raise ValueError("categories: use uppercase names; ALL is generated automatically")

    profile = data.get("profile")
    if not isinstance(profile, dict):
        raise ValueError("profile: expected an object")
    for field in ("handle", "headline", "intro"):
        require_text(profile.get(field), f"profile.{field}")
    text_list(profile.get("about", []), "profile.about")
    for field in ("role", "eyebrow", "aboutLead", "contactLead", "motto", "aboutQuote", "resourcesQuote"):
        if field in profile and not isinstance(profile[field], str):
            raise ValueError(f"profile.{field}: expected text")

    for collection, fields in (("links", ("label", "value")), ("repositories", ("name", "summary"))):
        for index, item in enumerate(require_list(data.get(collection), collection)):
            context = f"{collection}[{index}]"
            if not isinstance(item, dict):
                raise ValueError(f"{context}: expected an object")
            for field in fields:
                require_text(item.get(field), f"{context}.{field}")
            canonical_url(item.get("url"))
            if collection == "repositories":
                text_list(item.get("tags", []), f"{context}.tags")

    ids, destinations = set(), set()
    for collection in ("writeups", "notes"):
        for index, item in enumerate(require_list(data.get(collection), collection)):
            context = f"{collection}[{index}]"
            if not isinstance(item, dict):
                raise ValueError(f"{context}: expected an object")
            entry_id = require_text(item.get("id"), f"{context}.id")
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", entry_id):
                raise ValueError(f"{context}.id: use a lowercase slug such as my-new-note")
            if entry_id in ids:
                raise ValueError(f"Duplicate write-up ID: {entry_id}")
            ids.add(entry_id)
            for field in ("title", "summary", "category"):
                require_text(item.get(field), f"{context}.{field}")
            if item["category"] not in categories:
                raise ValueError(f"{context}.category: choose from {', '.join(categories)}")
            text_list(item.get("tags", []), f"{context}.tags")
            if "source" in item:
                require_text(item["source"], f"{context}.source")
            if "date" in item:
                value = require_text(item["date"], f"{context}.date")
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                    raise ValueError(f"{context}.date: use YYYY-MM-DD")
                try:
                    date.fromisoformat(value)
                except ValueError as error:
                    raise ValueError(f"{context}.date: invalid calendar date") from error
            if ("url" in item) == ("file" in item):
                raise ValueError(f"{context}: provide exactly one of url or file")
            if "url" in item:
                destination = canonical_url(item["url"])
            else:
                filename = require_text(item["file"], f"{context}.file")
                path = Path(filename)
                resolved = (root / path).resolve()
                if path.is_absolute() or ".." in path.parts or not resolved.is_relative_to((root / "content").resolve()):
                    raise ValueError(f"{context}.file: use a relative path inside content/")
                if path.suffix.lower() != ".md" or not resolved.is_file():
                    raise ValueError(f"{context}.file: Markdown file does not exist: {filename}")
                destination = str(resolved)
            if destination in destinations:
                raise ValueError(f"Duplicate write-up destination: {item.get('url', item.get('file'))}")
            destinations.add(destination)

    groups, resources = set(), set()
    for index, group in enumerate(require_list(data.get("resourceGroups"), "resourceGroups")):
        context = f"resourceGroups[{index}]"
        if not isinstance(group, dict):
            raise ValueError(f"{context}: expected an object")
        title = require_text(group.get("title"), f"{context}.title")
        if title.strip().casefold() in groups:
            raise ValueError(f"Duplicate resource group: {title}")
        groups.add(title.strip().casefold())
        for item in require_list(group.get("items"), f"{context}.items"):
            if not isinstance(item, dict):
                raise ValueError(f"{context}.items: expected resource objects")
            require_text(item.get("label"), f"{context}.label")
            require_text(item.get("summary"), f"{context}.summary")
            url = canonical_url(item.get("url"))
            if url in resources:
                raise ValueError(f"Duplicate resource URL: {item['url']}")
            resources.add(url)

    text_list(data.get("currentFocus", []), "currentFocus")
    for step in require_list(data.get("workflow", []), "workflow"):
        if not isinstance(step, dict):
            raise ValueError("workflow: expected step objects")
        require_text(step.get("title"), "workflow.title")
        require_text(step.get("summary"), "workflow.summary")


def load_content(root: Path = ROOT) -> dict:
    data = json.loads((root / "content.json").read_text(encoding="utf-8"))
    validate_content(data, root)
    return data


def content_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2) + "\n"


def inline_script(source: str) -> str:
    # A literal closing tag inside JS data must not end the surrounding script.
    return re.sub(r"</script", lambda match: "<\\/" + match[0][2:], source, flags=re.IGNORECASE)


def navigation(page: str) -> str:
    active_page = "writeups" if page == "writeup" else page
    links = []
    for route, filename, title, _ in PAGES:
        current = ' class="active" aria-current="page"' if route == active_page else ""
        links.append(f'      <a href="{filename}" data-route="{route}"{current}>{title}</a>')
    return "\n".join(links)


def render_outputs(data: dict, root: Path = ROOT) -> dict[Path, str]:
    validate_content(data, root)
    template = (root / "page-template.html").read_text(encoding="utf-8")
    serialized = content_json(data).rstrip()
    outputs = {
        root / "data.js": "// Generated from content.json by sync_data.py. Do not edit.\n"
        + f"window.PORTFOLIO_DATA = {serialized};\n"
    }
    shared = {
        "styles": (root / "styles.css").read_text(encoding="utf-8").strip(),
        "app": inline_script((root / "app.js").read_text(encoding="utf-8").strip()),
        "fallback": inline_script(f"window.PORTFOLIO_DATA_FALLBACK = {serialized};"),
    }
    for page, filename, title, description in PAGES + EXTRA_PAGES:
        values = {
            **shared,
            "page": page,
            "title": escape(title),
            "description": escape(description),
            "navigation": navigation(page),
        }
        try:
            outputs[root / filename] = re.sub(r"\{\{(\w+)\}\}", lambda match: values[match[1]], template)
        except KeyError as error:
            raise ValueError(f"Unknown page-template.html placeholder: {error.args[0]}") from error
    return outputs


def write_outputs(outputs: dict[Path, str]) -> list[Path]:
    changed = []
    for path, text in outputs.items():
        if path.exists() and path.read_text(encoding="utf-8") == text:
            continue
        # Replace complete files so an active preview never reads a half-written script.
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            try:
                handle.write(text)
                handle.close()
                temporary.chmod(path.stat().st_mode & 0o777 if path.exists() else 0o644)
                temporary.replace(path)
            finally:
                temporary.unlink(missing_ok=True)
        changed.append(path)
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate content and check generated files without writing.")
    args = parser.parse_args()
    try:
        outputs = render_outputs(load_content())
        if args.check:
            outdated = [path.name for path, text in outputs.items()
                        if not path.exists() or path.read_text(encoding="utf-8") != text]
            if outdated:
                raise ValueError("Run python3 sync_data.py to update: " + ", ".join(outdated))
            print("Content is valid. All generated files are up to date.")
        else:
            changed = write_outputs(outputs)
            print(f"Content is valid. Updated {len(changed)} generated files.")
    except (ValueError, OSError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()

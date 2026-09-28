"""Add or update portfolio write-ups and resources, then rebuild the site."""

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlsplit

from sync_data import ROOT, canonical_url, content_json, load_content, render_outputs, write_outputs


def slugify(title: str) -> str:
    text = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if not slug:
        raise ValueError("Provide --id with a lowercase slug for this title")
    return slug


def source_label(url: str | None) -> str:
    if not url:
        return "Portfolio"
    host = urlsplit(url).hostname.lower()
    return {"github.com": "GitHub", "hackmd.io": "HackMD"}.get(host, "External")


def add_writeup(data: dict, args: argparse.Namespace) -> tuple[str, dict]:
    url = canonical_url(args.url) if args.url else None
    filename = Path(args.file).as_posix() if args.file else None
    requested_collection = getattr(args, "collection", None)
    matches = []
    for collection in ("writeups", "notes"):
        for index, item in enumerate(data[collection]):
            same_id = args.id is not None and item["id"] == args.id
            same_url = url is not None and "url" in item and canonical_url(item["url"]) == url
            same_file = filename is not None and "file" in item and Path(item["file"]).as_posix() == filename
            if same_id or same_url or same_file:
                matches.append((collection, index, item))
    if len(matches) > 1:
        raise ValueError("The ID and destination identify different write-ups; choose one existing entry")
    if matches and not args.update:
        raise ValueError(f"Write-up already exists as {matches[0][2]['id']}; use --update to edit it")
    if args.update and not matches:
        raise ValueError("No matching write-up to update; supply its --id or existing destination")
    if matches and args.id is not None and args.id != matches[0][2]["id"]:
        raise ValueError(f"That destination belongs to {matches[0][2]['id']}; existing IDs stay unchanged")

    entry = deepcopy(matches[0][2]) if matches else {"id": args.id or slugify(args.title)}
    same_destination = ((url is not None and "url" in entry and canonical_url(entry["url"]) == url)
                        or (filename is not None and "file" in entry and Path(entry["file"]).as_posix() == filename))
    previous_source = entry.get("source") if same_destination else None
    entry.update(title=args.title.strip(), summary=args.summary.strip(), category=args.category)
    entry["tags"] = args.tags if args.tags is not None else entry.get("tags", [])
    entry["source"] = args.source or previous_source or source_label(args.url)
    if args.date is not None:
        entry["date"] = args.date
    if args.url:
        entry.pop("file", None)
        entry["url"] = args.url
    else:
        entry.pop("url", None)
        entry["file"] = filename
    if matches:
        previous_collection, index, _ = matches[0]
        collection = requested_collection or previous_collection
        if collection == previous_collection:
            data[collection][index] = entry
        else:
            data[previous_collection].pop(index)
            data[collection].append(entry)
        label = "note" if collection == "notes" else "write-up"
        return f"Updated {label}", entry
    collection = requested_collection or "writeups"
    data[collection].append(entry)
    label = "note" if collection == "notes" else "write-up"
    return f"Added {label}", entry


def add_resource(data: dict, args: argparse.Namespace) -> tuple[str, dict]:
    url = canonical_url(args.url)
    existing = next(((group, index, item)
                     for group in data["resourceGroups"]
                     for index, item in enumerate(group["items"])
                     if canonical_url(item["url"]) == url), None)
    if existing and not args.update:
        raise ValueError(f"Resource already exists in {existing[0]['title']}; use --update to edit or move it")
    if args.update and not existing:
        raise ValueError("No resource matches that URL; omit --update to add it")

    title = args.group.strip()
    group = next((group for group in data["resourceGroups"] if group["title"].strip().casefold() == title.casefold()), None)
    if group is None:
        group = {"title": title, "items": []}
        data["resourceGroups"].append(group)
    entry = deepcopy(existing[2]) if existing else {}
    entry.update(label=args.title.strip(), summary=args.summary.strip(), url=args.url)
    if existing and existing[0] is group:
        group["items"][existing[1]] = entry
    else:
        if existing:
            previous, index, _ = existing
            previous["items"].pop(index)
            if not previous["items"]:
                data["resourceGroups"].remove(previous)
        group["items"].append(entry)
    return ("Updated resource" if existing else "Added resource"), entry


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    writeup = commands.add_parser("add-writeup", help="Add an external link or an existing local Markdown file.")
    resource = commands.add_parser("add-resource", help="Add a resource link to an existing or new group.")
    for command in (writeup, resource):
        command.add_argument("--title", required=True, help="Visible card or link title.")
        command.add_argument("--summary", required=True, help="A short, accurate description.")
        command.add_argument("--update", action="store_true", help="Update a matching entry instead of adding a duplicate.")
        command.add_argument("--dry-run", action="store_true", help="Validate and show the entry without changing files.")
    destination = writeup.add_mutually_exclusive_group(required=True)
    destination.add_argument("--url", help="External write-up URL.")
    destination.add_argument("--file", help="Existing Markdown path relative to the site, such as content/my-note.md.")
    writeup.add_argument("--category", type=str.upper, required=True, help="One of the categories in content.json.")
    writeup.add_argument("--collection", choices=("writeups", "notes"),
                         help="Store the entry in the write-ups or notes collection (defaults to write-ups for new entries).")
    writeup.add_argument("--id", help="Stable lowercase slug; defaults to a slug generated from the title.")
    writeup.add_argument("--tags", nargs="*", help="Optional tags; existing tags are retained on update when omitted.")
    writeup.add_argument("--source", help="Optional source label; inferred for GitHub, HackMD, and local notes.")
    writeup.add_argument("--date", help="Optional known publication date in YYYY-MM-DD format.")
    resource.add_argument("--url", required=True, help="External resource URL.")
    resource.add_argument("--group", required=True, help="Resource group title; created if it does not exist.")
    return parser


def main(argv: list[str] | None = None, root: Path = ROOT) -> None:
    parser = make_parser()
    args = parser.parse_args(argv)
    try:
        data = load_content(root)
        action, entry = (add_writeup if args.command == "add-writeup" else add_resource)(data, args)
        # Prepare and validate every output before changing either content or generated files.
        outputs = {root / "content.json": content_json(data), **render_outputs(data, root)}
        if args.dry_run:
            print(f"Dry run: {action.lower()}. No files changed.")
            print(json.dumps(entry, ensure_ascii=False, indent=2))
        else:
            changed = write_outputs(outputs)
            print(f"{action}: {entry.get('title', entry.get('label'))}")
            print(f"Validated content and updated {len(changed)} files.")
    except (ValueError, OSError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()

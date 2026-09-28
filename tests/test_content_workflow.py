from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import manage_content
import sync_data


class ContentWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for filename in ("content.json", "page-template.html", "app.js", "styles.css"):
            shutil.copy2(sync_data.ROOT / filename, self.root / filename)
        shutil.copytree(sync_data.ROOT / "content", self.root / "content")
        sync_data.write_outputs(sync_data.render_outputs(sync_data.load_content(self.root), self.root))

    def run_command(self, args):
        output = StringIO()
        with redirect_stdout(output):
            manage_content.main(args, root=self.root)
        return output.getvalue()

    def snapshot(self):
        return {path.relative_to(self.root).as_posix(): path.read_bytes()
                for path in self.root.rglob("*") if path.is_file()}

    def writeup_args(self, **overrides):
        options = {
            "url": "https://example.com/new-note", "title": "A new note",
            "summary": "Notes from a local experiment.", "category": "PWN",
        }
        options.update(overrides)
        return ["add-writeup"] + [argument for key, value in options.items() if value is not None
                                  for argument in ("--" + key, value)]

    def resource_args(self, **overrides):
        options = {
            "url": "https://example.com/reference", "title": "New reference",
            "summary": "Documentation for a study topic.", "group": "New references",
        }
        options.update(overrides)
        return ["add-resource"] + [argument for key, value in options.items()
                                   for argument in ("--" + key, value)]

    def assert_rejected_without_writes(self, args, message):
        before = self.snapshot()
        errors = StringIO()
        with redirect_stderr(errors), self.assertRaises(SystemExit) as raised:
            self.run_command(args)
        self.assertEqual(raised.exception.code, 1)
        self.assertIn(message, errors.getvalue())
        self.assertEqual(self.snapshot(), before)

    def test_add_writeup_rebuilds_browser_data_and_embedded_copies(self):
        previous = sync_data.load_content(self.root)
        self.run_command(self.writeup_args(date="2026-09-07") + ["--tags", "heap", "memory layout"])
        data = sync_data.load_content(self.root)
        self.assertEqual(len(data["writeups"]), len(previous["writeups"]) + 1)
        entry = data["writeups"][-1]
        self.assertEqual(entry["id"], "a-new-note")
        self.assertEqual(entry["category"], "PWN")
        self.assertEqual(entry["tags"], ["heap", "memory layout"])
        browser_json = (self.root / "data.js").read_text().partition("window.PORTFOLIO_DATA = ")[2].strip().removesuffix(";")
        self.assertEqual(json.loads(browser_json), data)
        for _, filename, _, _ in sync_data.PAGES + sync_data.EXTRA_PAGES:
            self.assertIn(entry["url"], (self.root / filename).read_text())

    def test_add_note_uses_separate_collection_and_renders_both_grids(self):
        self.run_command(self.writeup_args(collection="notes", id="local-learning"))
        data = sync_data.load_content(self.root)
        self.assertEqual(data["notes"][-1]["id"], "local-learning")
        self.assertNotIn(data["notes"][-1], data["writeups"])
        html = (self.root / "writeups.html").read_text()
        self.assertIn('data-entry-collection="writeups"', html)
        self.assertIn('data-entry-collection="notes"', html)
        self.assertIn("local-learning", html)

    def test_update_can_move_entry_between_collections_without_changing_id(self):
        self.run_command(self.writeup_args(collection="notes", id="movable-note"))
        self.run_command(self.writeup_args(collection="writeups", id="movable-note") + ["--update"])
        data = sync_data.load_content(self.root)
        self.assertEqual(data["writeups"][-1]["id"], "movable-note")
        self.assertNotIn("movable-note", {item["id"] for item in data["notes"]})

    def test_add_local_markdown_and_infer_portfolio_source(self):
        (self.root / "content" / "new-note.md").write_text("# A local note\n\nA short observation.\n")
        self.run_command(self.writeup_args(url=None, file="content/new-note.md", category="skills"))
        entry = sync_data.load_content(self.root)["writeups"][-1]
        self.assertEqual(entry["file"], "content/new-note.md")
        self.assertEqual(entry["source"], "Portfolio")
        self.assertEqual(entry["category"], "SKILLS")
        self.assertNotIn("url", entry)

    def test_duplicate_urls_are_rejected_before_writing(self):
        self.run_command(self.writeup_args())
        self.assert_rejected_without_writes(
            self.writeup_args(url="https://EXAMPLE.com/new-note/", title="Another title"), "already exists")
        self.run_command(self.resource_args())
        self.assert_rejected_without_writes(
            self.resource_args(url="https://EXAMPLE.com/reference/", group="Another group"), "already exists")

    def test_update_preserves_ids_tags_and_dates(self):
        self.run_command(self.writeup_args(date="2026-09-07") + ["--tags", "heap"])
        count = len(sync_data.load_content(self.root)["writeups"])
        self.run_command(self.writeup_args(title="A better title", category="KERNEL") + ["--update"])
        entries = sync_data.load_content(self.root)["writeups"]
        self.assertEqual(len(entries), count)
        self.assertEqual(entries[-1]["id"], "a-new-note")
        self.assertEqual(entries[-1]["category"], "KERNEL")
        self.assertEqual(entries[-1]["tags"], ["heap"])
        self.assertEqual(entries[-1]["date"], "2026-09-07")

    def test_change_destination_by_id_updates_source_and_keeps_id(self):
        self.run_command(self.writeup_args(url="https://github.com/example/new-note"))
        self.assertEqual(sync_data.load_content(self.root)["writeups"][-1]["source"], "GitHub")
        (self.root / "content" / "new-note.md").write_text("# A local note\n")
        self.run_command(self.writeup_args(url=None, file="content/new-note.md", id="a-new-note") + ["--update"])
        entry = sync_data.load_content(self.root)["writeups"][-1]
        self.assertEqual(entry["id"], "a-new-note")
        self.assertEqual(entry["source"], "Portfolio")
        self.assertNotIn("url", entry)

    def test_new_groups_case_insensitive_matching_and_resource_moves(self):
        before = len(sync_data.load_content(self.root)["resourceGroups"])
        self.run_command(self.resource_args())
        self.run_command(self.resource_args(url="https://example.com/second", group="new REFERENCES"))
        data = sync_data.load_content(self.root)
        self.assertEqual(len(data["resourceGroups"]), before + 1)
        self.assertEqual(len(data["resourceGroups"][-1]["items"]), 2)
        self.run_command(self.resource_args(group="Moved references", title="Updated reference") + ["--update"])
        data = sync_data.load_content(self.root)
        self.assertEqual(len(data["resourceGroups"][-2]["items"]), 1)
        self.assertEqual(data["resourceGroups"][-1]["title"], "Moved references")
        self.assertEqual(data["resourceGroups"][-1]["items"][0]["label"], "Updated reference")

    def test_invalid_entries_leave_every_file_unchanged(self):
        cases = [
            (self.writeup_args(category="RESOURCES"), "choose from"),
            (self.writeup_args(date="2026-02-30"), "invalid calendar date"),
            (self.writeup_args(url=None, file="content/missing.md"), "does not exist"),
            (self.writeup_args(url="not-a-url"), "URL:"),
            (self.resource_args(title=" "), "non-empty text"),
        ]
        for args, message in cases:
            with self.subTest(args=args):
                self.assert_rejected_without_writes(args, message)

    def test_colliding_ids_and_conflicting_update_identifiers_are_rejected(self):
        self.run_command(self.writeup_args())
        self.assert_rejected_without_writes(self.writeup_args(url="https://example.com/other"), "Duplicate write-up ID")
        self.assert_rejected_without_writes(self.writeup_args(id="different-id") + ["--update"], "IDs stay unchanged")

    def test_dry_run_does_not_modify_content_or_generated_files(self):
        before = self.snapshot()
        output = self.run_command(self.resource_args() + ["--dry-run"])
        self.assertIn("Dry run", output)
        self.assertIn("New reference", output)
        self.assertEqual(self.snapshot(), before)

    def test_template_failure_does_not_commit_new_content(self):
        template = self.root / "page-template.html"
        template.write_text(template.read_text() + "\n{{unknown_placeholder}}\n")
        self.assert_rejected_without_writes(self.writeup_args(), "Unknown page-template.html placeholder")

    def test_embedded_content_cannot_end_its_script_tag(self):
        self.run_command(self.writeup_args(title="A literal </script> in a title", id="literal-title"))
        html = (self.root / "writeups.html").read_text()
        self.assertNotIn("A literal </script> in a title", html)
        self.assertIn("A literal <\\/script> in a title", html)
        self.assertEqual(sync_data.load_content(self.root)["writeups"][-1]["title"], "A literal </script> in a title")


if __name__ == "__main__":
    unittest.main()

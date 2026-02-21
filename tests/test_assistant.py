from pathlib import Path
import tempfile
import unittest

from coding_assistant import SmartCodingAssistant


class SmartCodingAssistantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assistant = SmartCodingAssistant()

    def test_intent_detection_feature(self):
        intent = self.assistant.analyze_task("implement OAuth login for web app")
        self.assertEqual(intent, "feature")

    def test_pick_relevant_files_by_task_tokens(self):
        files = [
            "src/auth/login.py",
            "src/auth/oauth.py",
            "README.md",
            "tests/test_auth.py",
        ]
        relevant = self.assistant.pick_relevant_files(
            "add oauth login tests", files, limit=3
        )
        self.assertIn("src/auth/oauth.py", relevant)
        self.assertIn("src/auth/login.py", relevant)

    def test_repo_file_discovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.py").write_text("print('hi')\n", encoding="utf-8")
            (root / "notes.txt").write_text("x\n", encoding="utf-8")
            files = self.assistant.gather_repo_files(root)
            self.assertEqual(files, ["main.py"])

    def test_generate_and_apply_function_stub(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "app.py"
            source.write_text("def existing():\n    return 1\n", encoding="utf-8")

            result = self.assistant.run(
                task="add function parse_config to app",
                repo_path=root,
                files=["app.py"],
                apply=True,
            )

            self.assertEqual(result.intent, "feature")
            updated = source.read_text(encoding="utf-8")
            self.assertIn("def parse_config(", updated)
            self.assertIn("NotImplementedError", updated)
            self.assertIn("Applied edits", "\n".join(result.commands))

    def test_patch_preview_in_response(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "module.py"
            source.write_text("", encoding="utf-8")
            result = self.assistant.run(
                task="add function build_index",
                repo_path=root,
                files=["module.py"],
                apply=False,
            )
            self.assertIn("Patch preview:", result.response)
            self.assertIn("def build_index(", result.response)


if __name__ == "__main__":
    unittest.main()

import unittest

from coding_assistant import AssistantResult
from gui_server import _result_to_dict


class GuiServerTests(unittest.TestCase):
    def test_result_to_dict_shape(self):
        result = AssistantResult(
            task="add function x",
            intent="feature",
            relevant_files=["app.py"],
            plan=["step1"],
            commands=["cmd"],
            response="ok",
        )
        payload = _result_to_dict(result)
        self.assertEqual(payload["task"], "add function x")
        self.assertEqual(payload["intent"], "feature")
        self.assertIn("relevant_files", payload)
        self.assertIn("plan", payload)
        self.assertIn("commands", payload)
        self.assertIn("response", payload)


if __name__ == "__main__":
    unittest.main()

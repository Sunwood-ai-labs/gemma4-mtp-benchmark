from __future__ import annotations

import io
import json
import unittest

from gemma4_mtp_benchmark import cli


class ChatCliTests(unittest.TestCase):
    def test_parser_accepts_chat_mode(self) -> None:
        parser = cli.build_parser()

        args = parser.parse_args(
            ["chat", "--model", "e4b", "--backend", "gpu", "--mode", "compare", "--dry-run"]
        )

        self.assertEqual(args.command, "chat")
        self.assertEqual(args.model, "e4b")
        self.assertEqual(args.backend, "gpu")
        self.assertEqual(args.mode, "compare")
        self.assertTrue(args.dry_run)

    def test_chat_dry_run_prints_configuration(self) -> None:
        parser = cli.build_parser()
        args = parser.parse_args(["chat", "--model", "e2b", "--mode", "mtp", "--dry-run"])
        out = io.StringIO()

        result = cli.run_chat(args, out=out)

        self.assertEqual(result, 0)
        payload = json.loads(out.getvalue())
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["chat_mode"], "mtp")
        self.assertEqual(payload["model"]["key"], "e2b")

    def test_format_chat_stats_includes_ratio_for_compare(self) -> None:
        text = cli.format_chat_stats(
            {
                False: cli.ChatTurnStats(seconds=20.0, output_chars=800, estimated_tokens=200.0),
                True: cli.ChatTurnStats(seconds=10.0, output_chars=800, estimated_tokens=200.0),
            }
        )

        self.assertIn("baseline: 20.00s", text)
        self.assertIn("mtp: 10.00s", text)
        self.assertIn("estimated speed ratio: 2.00x", text)


if __name__ == "__main__":
    unittest.main()

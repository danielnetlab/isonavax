"""Exercise help through the public command-line entry point."""

import subprocess
import sys
import unittest


class HelpTests(unittest.TestCase):
    def test_get_files_help_describes_listing(self):
        result = subprocess.run(
            [sys.executable, "-m", "isonavax.main", "--help"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("list files inside the ISO", result.stdout)
        self.assertNotIn("extrat", result.stdout)
        self.assertIn("--get-files", result.stdout)

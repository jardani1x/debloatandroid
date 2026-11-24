import unittest
from unittest.mock import patch, MagicMock
import os
import json
import sys

# Add scripts directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
import debloat

class TestDebloatScript(unittest.TestCase):
    def setUp(self):
        self.mock_device = "mock-device-1234"
        self.mock_user = "0"
        self.sample_packages = [
            "com.hxywizard",
            "com.android.egg",
            "com.android.systemui"  # Protected package!
        ]

    @patch("debloat.run_adb")
    def test_protection_check(self, mock_run_adb):
        """Verify protected system components cannot be disabled."""
        protected_pkg = "com.android.systemui"
        self.assertIn(protected_pkg, debloat.PROTECTED_SYSTEM_PACKAGES)

    @patch("debloat.get_connected_device")
    @patch("debloat.run_adb")
    def test_stability_check_healthy(self, mock_run_adb, mock_get_dev):
        """Verify stability check passes when SystemUI is alive."""
        mock_run_adb.side_effect = [
            ("1234", "", 0),  # pidof com.android.systemui
            ("package:/system/framework/framework-res.apk", "", 0)  # pm path android
        ]
        stable, reason = debloat.check_system_stability(self.mock_device)
        self.assertTrue(stable)
        self.assertEqual(reason, "Stable")

    @patch("debloat.get_connected_device")
    @patch("debloat.run_adb")
    def test_stability_check_failure(self, mock_run_adb, mock_get_dev):
        """Verify stability check flags failed SystemUI."""
        mock_run_adb.side_effect = [
            ("", "No such process", 1),  # pidof com.android.systemui fails
        ]
        stable, reason = debloat.check_system_stability(self.mock_device)
        self.assertFalse(stable)

    def test_transaction_logging(self):
        """Verify transaction log writes formatted jsonl."""
        log_file = "logs/test_transactions.jsonl"
        with patch("debloat.TX_LOG_PATH", log_file):
            debloat.log_transaction("test_action", "com.example.test", "enabled", "disabled", "SUCCESS", "mock test")
            self.assertTrue(os.path.exists(log_file))
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                self.assertGreater(len(lines), 0)
                entry = json.loads(lines[-1])
                self.assertEqual(entry["package"], "com.example.test")
                self.assertEqual(entry["status"], "SUCCESS")
            os.remove(log_file)

if __name__ == "__main__":
    unittest.main()

"""Offline unit tests for validation and the three-step flow."""

import unittest
from unittest.mock import patch

import connect_android as app


class AddressTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(
            app.parse_address("192.168.1.42:037123"),
            "192.168.1.42:37123",
        )

    def test_invalid(self):
        for address in (
            "192.168.1.300:1234",
            "192.168.1.42:0",
            "192.168.1.42:65536",
            "example.com:5555",
            "192.168.1.42:abc",
        ):
            with self.subTest(address=address):
                with self.assertRaises(ValueError):
                    app.parse_address(address)

    @patch("builtins.input", side_effect=["123", "123456"])
    def test_pairing_code_validation(self, _):
        self.assertEqual(app.read_pairing_code(), "123456")

    @patch.object(app, "find_adb", return_value="adb")
    @patch.object(app, "run_adb")
    @patch(
        "builtins.input",
        side_effect=[
            "192.168.1.42:37123",
            "123456",
            "192.168.1.42:41587",
        ],
    )
    def test_three_step_order(self, _input, run, _find):
        run.side_effect = [
            "Successfully paired to 192.168.1.42:37123",
            "connected to 192.168.1.42:41587",
            "device",
            "List of devices attached",
        ]
        self.assertEqual(app.main(), 0)
        self.assertEqual(
            run.call_args_list[0].args,
            ("adb", "pair", "192.168.1.42:37123", "123456"),
        )
        self.assertEqual(
            run.call_args_list[1].args,
            ("adb", "connect", "192.168.1.42:41587"),
        )
        self.assertEqual(
            run.call_args_list[2].args,
            ("adb", "-s", "192.168.1.42:41587", "get-state"),
        )


if __name__ == "__main__":
    unittest.main()

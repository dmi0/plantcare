from unittest import TestCase, mock

import config
import plantsensor


class Test(TestCase):
    def setUp(self):
        config._config["_loaded"] = False

    def test__update_empty(self):
        a = {"a": 1, "b": {"c": 2}}
        config._update(a, {})
        self.assertEqual(a, {"a": 1, "b": {"c": 2}})

    def test__update_not_applicable(self):
        a = {"a": 1, "b": {"c": 2}}
        config._update(a, {"aa": 11, "b": {"cc": 22}})
        self.assertEqual(a, {"a": 1, "b": {"c": 2}})

    def test__update_replace(self):
        a = {"a": 1, "b": {"c": 2}}
        config._update(a, {"a": 2})
        self.assertEqual(a, {"a": 2, "b": {"c": 2}})

    def test__update_none(self):
        a = {"a": 1, "b": {"c": 2, "z": None}}
        config._update(a, {"b": {"z": 123}})
        self.assertEqual(a, {"a": 1, "b": {"c": 2, "z": 123}})

    def test__update_type_mismatch(self):
        a = {"a": 1, "b": {"c": 2}}
        with self.assertRaises(ValueError):
            config._update(a, {"b": {"c": "123"}})

    def test__update_empty_dict(self):
        a = {"a": 1, "b": {}}
        config._update(a, {"b": {"z": 123}})
        self.assertEqual(a, {"a": 1, "b": {"z": 123}})

    @mock.patch("config._get_cfg")
    def test_get_all(self, mock_get_cfg):
        mock_get_cfg.return_value = {"test": {"a": 123}, "_loaded": True}
        self.assertEqual(config.get_all(), {"test": {"a": 123}})

    @mock.patch("config._load_custom")
    def test_get_max_attempts_default(self, mock_load_custom):
        mock_load_custom.return_value = {}
        self.assertGreater(config.get_max_attempts(), 0)

    @mock.patch("config._get_cfg")
    def test_get_max_attempts(self, mock_get_cfg):
        mock_get_cfg.return_value = {"max_attempts": "123"}
        self.assertEqual(config.get_max_attempts(), 123)

    @mock.patch("config._get_cfg")
    def test_get_max_attempts_not_numeric(self, mock_get_cfg):
        mock_get_cfg.return_value = {"max_attempts": "123abc"}
        with self.assertRaises(ValueError):
            config.get_max_attempts()

    @mock.patch("config._load_custom")
    def test_get_loglevel_default(self, mock_load_custom):
        mock_load_custom.return_value = {}
        self.assertIn(config.get_loglevel(), ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"])

    @mock.patch("config._get_cfg")
    def test_get_loglevel(self, mock_get_cfg):
        mock_get_cfg.return_value = {"loglevel": "NOTSET"}
        self.assertEqual(config.get_loglevel(), "NOTSET")

    @mock.patch("config._get_cfg")
    def test_get_loglevel_wrong(self, mock_get_cfg):
        mock_get_cfg.return_value = {"loglevel": "ABC"}
        with self.assertRaises(ValueError):
            config.get_loglevel()

    @mock.patch("config._get_cfg")
    def test__get_non_empty_one(self, mock_get_cfg):
        mock_get_cfg.return_value = {"key": "ABC"}
        self.assertEqual(config._get_non_empty("key"), "ABC")

    @mock.patch("config._get_cfg")
    def test__get_non_empty_three(self, mock_get_cfg):
        mock_get_cfg.return_value = {"key1": {"key2": {"key3": "ABC"}}}
        self.assertEqual(config._get_non_empty("key1", "key2", "key3"), "ABC")

    @mock.patch("config._get_cfg")
    def test__get_non_empty_empty(self, mock_get_cfg):
        mock_get_cfg.return_value = {"key": ""}
        with self.assertRaises(ValueError):
            config._get_non_empty("key")

    @mock.patch("config._get_cfg")
    def test__get_non_empty_none(self, mock_get_cfg):
        mock_get_cfg.return_value = {"key": None}
        with self.assertRaises(ValueError):
            config._get_non_empty("key")

    @mock.patch("config._load_custom")
    def test_get_adapter_default(self, mock_load_custom):
        mock_load_custom.return_value = {}
        config.get_adapter()

    @mock.patch("config._get_cfg")
    def test_get_adapter(self, mock_get_cfg):
        mock_get_cfg.return_value = {"adapter": "h123"}
        self.assertEqual(config.get_adapter(), "h123")

    @mock.patch("config._load_custom")
    def test_get_telegram_token_default(self, mock_load_custom):
        mock_load_custom.return_value = {}
        with self.assertRaises(ValueError):
            config.get_telegram_token()

    @mock.patch("config._get_cfg")
    def test_get_telegram_token(self, mock_get_cfg):
        mock_get_cfg.return_value = {"telegram": {"token": "t"}}
        self.assertEqual(config.get_telegram_token(), "t")

    @mock.patch("config._load_custom")
    def test_get_telegram_channel_default(self, mock_load_custom):
        mock_load_custom.return_value = {}
        with self.assertRaises(ValueError):
            config.get_telegram_channel()

    @mock.patch("config._get_cfg")
    def test_get_telegram_channel(self, mock_get_cfg):
        mock_get_cfg.return_value = {"telegram": {"channel": "ch"}}
        self.assertEqual(config.get_telegram_channel(), "ch")

    @mock.patch("config._load_custom")
    def test_get_message_parse_mode_default(self, mock_load_custom):
        mock_load_custom.return_value = {}
        config.get_message_parse_mode()

    @mock.patch("config._get_cfg")
    def test_get_message_parse_mode(self, mock_get_cfg):
        mock_get_cfg.return_value = {"telegram": {"message": {"parse_mode": "p"}}}
        self.assertEqual(config.get_message_parse_mode(), "p")

    @mock.patch("config._load_custom")
    def test_get_message_templates(self, mock_load_custom):
        mock_load_custom.return_value = {
            "telegram": {"message": {"parse_mode": "p", "conductivity": "c", "battery": ""}}
        }
        message_templates = config.get_message_templates()
        self.assertNotIn("parse_mode", message_templates)
        self.assertEqual(message_templates["conductivity"], "c")
        self.assertEqual(message_templates["battery"], "")
        self.assertGreater(len(message_templates), 2)

    @mock.patch("config._load_custom")
    def test_get_sensors_default(self, mock_load_custom):
        mock_load_custom.return_value = {}
        with self.assertRaises(ValueError):
            config.get_sensors()

    @mock.patch("config._get_cfg")
    def test_get_sensors_wrong_range(self, mock_get_cfg):
        mock_get_cfg.return_value = {
            "sensors": {
                "s1": {
                    "mac": "123",
                    "wellbeing_range": {"moisture": {"min": "2", "max": "1"}}
                }
            }
        }
        with self.assertRaises(ValueError):
            config.get_sensors()

    @mock.patch("config._get_cfg")
    def test_get_sensors_wrong_param(self, mock_get_cfg):
        mock_get_cfg.return_value = {
            "sensors": {
                "s1": {
                    "mac": "123",
                    "wellbeing_range": {"xyz": {"min": "1", "max": "2"}}
                }
            }
        }
        with self.assertRaises(ValueError):
            config.get_sensors()

    @mock.patch("config._get_cfg")
    def test_get_sensors(self, mock_get_cfg):
        mock_get_cfg.return_value = {
            "sensors": {
                "s1": {
                    "mac": "123",
                    "wellbeing_range": {"temperature": {"min": "1", "max": "2"}}
                }
            }
        }
        self.assertEqual(
            config.get_sensors(),
            {
                "s1": {
                    "mac": "123",
                    "wellbeing_range": {"temperature": {"min": 1, "max": 2}}
                }
            }
        )

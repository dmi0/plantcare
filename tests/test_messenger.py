from unittest import TestCase, mock

from messenger import RangeCheckerEvaluator, AlertMessageRender


class TestRangeCheckerEvaluator(TestCase):
    def test_need_to_notify_not_defined(self):
        e = RangeCheckerEvaluator({"wellbeing_range": {"moisture": {"min": 0, "max": 10}}})
        self.assertTrue(not e.need_to_notify("light", 5))

    def test_need_to_notify_in_range(self):
        e = RangeCheckerEvaluator({"wellbeing_range": {"moisture": {"min": 0, "max": 10}}})
        self.assertTrue(not e.need_to_notify("moisture", 5))

    def test_need_to_notify_not_in_range(self):
        e = RangeCheckerEvaluator({"wellbeing_range": {"moisture": {"min": 0, "max": 10}}})
        self.assertTrue(e.need_to_notify("moisture", 11))

    def test_need_to_notify_in_open_range_left(self):
        e = RangeCheckerEvaluator({"wellbeing_range": {"moisture": {"min": 3, "max": None}}})
        self.assertTrue(not e.need_to_notify("moisture", 5))

    def test_need_to_notify_not_in_open_range_left(self):
        e = RangeCheckerEvaluator({"wellbeing_range": {"moisture": {"min": 3, "max": None}}})
        self.assertTrue(e.need_to_notify("moisture", 2))

    def test_need_to_notify_in_open_range_right(self):
        e = RangeCheckerEvaluator({"wellbeing_range": {"moisture": {"min": None, "max": 10}}})
        self.assertTrue(not e.need_to_notify("moisture", 5))

    def test_need_to_notify_not_in_open_range_right(self):
        e = RangeCheckerEvaluator({"wellbeing_range": {"moisture": {"min": None, "max": 10}}})
        self.assertTrue(e.need_to_notify("moisture", 20))


class TestAlertMessageRender(TestCase):
    @mock.patch("messenger._render_boundaries")
    def test_prepare(self, br):
        br.return_value = "boundaries"
        r = AlertMessageRender(
            {"zzz": {"wellbeing_range": {"moisture": {"min": 0, "max": 10}}}},
            {"moisture": "{plant}:{boundaries}:{value}"}
        )
        self.assertEqual(r.prepare("zzz", "moisture", 5), "zzz:boundaries:5")

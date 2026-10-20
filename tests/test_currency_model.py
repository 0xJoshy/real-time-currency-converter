import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from models.currency import (  
    ConversionRequest,
    ValidationError,
    validate_amount,
    validate_currency_code,
)

SUPPORTED = ["USD", "PHP", "EUR", "JPY"]


class ValidateAmountTests(unittest.TestCase):
    def test_accepts_valid_numbers(self):
        self.assertEqual(validate_amount("100"), 100.0)
        self.assertEqual(validate_amount(" 12.50 "), 12.5)
        self.assertEqual(validate_amount("1,234.56"), 1234.56)
        self.assertEqual(validate_amount(5), 5.0)
        self.assertEqual(validate_amount("0"), 0.0)

    def test_rejects_non_numeric(self):
        for bad in ["abc", "12abc", "", "   ", None, True, [], "1.2.3"]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValidationError):
                    validate_amount(bad)

    def test_rejects_negative(self):
        with self.assertRaisesRegex(ValidationError, "negative"):
            validate_amount("-1")
        with self.assertRaises(ValidationError):
            validate_amount(-0.01)

    def test_rejects_nan_and_infinity(self):
        for bad in ["nan", "inf", "-inf", float("nan"), float("inf")]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValidationError):
                    validate_amount(bad)
                    

class ValidateCurrencyCodeTests(unittest.TestCase):
    def test_normalizes_case_and_whitespace(self):
        self.assertEqual(validate_currency_code(" usd ", SUPPORTED), "USD")

    def test_rejects_unsupported_code(self):
        with self.assertRaisesRegex(ValidationError, "XYZ"):
            validate_currency_code("xyz", SUPPORTED)

    def test_rejects_empty_or_non_string(self):
        for bad in ["", "  ", None, 123]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValidationError):
                    validate_currency_code(bad, SUPPORTED)


class ConversionRequestTests(unittest.TestCase):
    def test_creates_valid_request(self):
        req = ConversionRequest.create("100", "usd", "php", SUPPORTED)
        self.assertEqual(req, ConversionRequest(100.0, "USD", "PHP"))

    def test_is_immutable(self):
        req = ConversionRequest.create("1", "USD", "PHP", SUPPORTED)
        with self.assertRaises(Exception):
            req.amount = 2  # type: ignore[misc]

    def test_invalid_fields_raise(self):
        with self.assertRaises(ValidationError):
            ConversionRequest.create("-5", "USD", "PHP", SUPPORTED)
        with self.assertRaises(ValidationError):
            ConversionRequest.create("5", "USD", "ZZZ", SUPPORTED)
        with self.assertRaises(ValidationError):
            ConversionRequest.create("5", "ZZZ", "PHP", SUPPORTED)

    def test_accepts_generator_of_codes(self):
        req = ConversionRequest.create("1", "USD", "PHP", (c for c in SUPPORTED))
        self.assertEqual(req.target, "PHP")


if __name__ == "__main__":
    unittest.main()
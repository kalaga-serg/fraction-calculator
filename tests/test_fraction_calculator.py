import unittest

from fraction_calculator import calculate_expression, format_decimal, tokenize


class FractionCalculatorTests(unittest.TestCase):
    def assert_calculation(self, expr: str, fraction: str, decimal: str):
        result = calculate_expression(expr)
        self.assertEqual(str(result), fraction)
        self.assertEqual(format_decimal(result), decimal)

    def test_tokenize_division_after_parenthesis(self):
        self.assertEqual(
            tokenize("(1/3 + 0.25) / 2".replace(",", ".")),
            ["(", "1/3", "+", "0.25", ")", "/", "2"],
        )

    def test_negative_numbers_and_unary_minus(self):
        self.assert_calculation("-1+2", "1", "1")
        self.assert_calculation("1*-2", "-2", "-2")
        self.assert_calculation("(-1/2)+1", "1/2", "0.5")
        self.assert_calculation("-(1/2 + 3)", "-7/2", "-3.5")
        self.assert_calculation("2/-(1/3)", "-6", "-6")

    def test_decimal_input_and_comma_normalization(self):
        self.assert_calculation("2.5 * 4 + 0.1", "101/10", "10.1")
        self.assert_calculation("2,5 * 4 + 0,1", "101/10", "10.1")
        self.assert_calculation(".25 + .5", "3/4", "0.75")
        self.assert_calculation("2.", "2", "2")

    def test_format_decimal_without_padding(self):
        self.assert_calculation("1/8", "1/8", "0.125")
        self.assert_calculation("1/40", "1/40", "0.025")
        self.assert_calculation("1/3", "1/3", "0.333333333333333")


if __name__ == "__main__":
    unittest.main()

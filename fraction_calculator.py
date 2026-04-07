from fractions import Fraction


def parse_number(token: str) -> Fraction:
    if "." in token:
        negative = token.startswith("-")
        positive = token.startswith("+")
        normalized = token[1:] if negative or positive else token
        parts = normalized.split(".")
        if len(parts) != 2:
            raise ValueError(f"Некорректное число: {token}")
        integer_part = parts[0] or "0"
        fractional_part = parts[1] or ""
        if not integer_part.isdigit() or not fractional_part.isdigit() and fractional_part != "":
            raise ValueError(f"Некорректное число: {token}")
        denominator = 10 ** len(fractional_part)
        numerator = int(integer_part) * denominator + int(fractional_part or "0")
        return Fraction(-numerator if negative else numerator, denominator or 1)
    if "/" in token:
        numerator, denominator = token.split("/", 1)
        return Fraction(int(numerator), int(denominator))
    return Fraction(int(token), 1)


def is_unary_context(tokens) -> bool:
    prev = tokens[-1] if tokens else None
    return prev in {None, "+", "-", "*", "/", "(", "u-", "u+"}


def is_number_token(token: str) -> bool:
    if not token:
        return False
    if token[0] in "+-":
        token = token[1:]
    if not token:
        return False
    if "." in token:
        parts = token.split(".")
        return (
            len(parts) == 2
            and (parts[0].isdigit() or parts[0] == "")
            and (parts[1].isdigit() or parts[1] == "")
            and parts != ["", ""]
        )
    if "/" in token:
        parts = token.split("/")
        return len(parts) == 2 and all(part.isdigit() for part in parts)
    return token.isdigit()


def tokenize(expr: str):
    tokens = []
    number = ""
    compact = expr.replace(" ", "")
    for index, ch in enumerate(compact):
        if ch.isdigit():
            number += ch
        elif ch == ".":
            if "." in number or "/" in number:
                raise ValueError("Некорректное число")
            number += ch
        elif ch == "/":
            next_char = compact[index + 1] if index + 1 < len(compact) else ""
            can_extend_fraction = (
                bool(number)
                and number[-1].isdigit()
                and "/" not in number
                and "." not in number
                and next_char.isdigit()
            )
            if can_extend_fraction:
                number += ch
            else:
                if number:
                    tokens.append(number)
                    number = ""
                tokens.append(ch)
        elif ch in "+-":
            next_char = compact[index + 1] if index + 1 < len(compact) else ""
            if not number and is_unary_context(tokens):
                if next_char.isdigit() or next_char == ".":
                    number = ch
                else:
                    tokens.append("u-" if ch == "-" else "u+")
            else:
                if number:
                    tokens.append(number)
                    number = ""
                tokens.append(ch)
        elif ch in "*()":
            if number:
                tokens.append(number)
                number = ""
            tokens.append(ch)
        else:
            raise ValueError(f"Недопустимый символ: {ch}")
    if number:
        tokens.append(number)
    return tokens


def to_rpn(tokens):
    precedence = {"+": 1, "-": 1, "*": 2, "/": 2, "u-": 3, "u+": 3}
    right_associative = {"u-", "u+"}
    output = []
    ops = []
    for token in tokens:
        if is_number_token(token):
            output.append(token)
        elif token in precedence:
            while (
                ops
                and ops[-1] in precedence
                and (
                    precedence[ops[-1]] > precedence[token]
                    or (
                        precedence[ops[-1]] == precedence[token]
                        and token not in right_associative
                    )
                )
            ):
                output.append(ops.pop())
            ops.append(token)
        elif token == "(":
            ops.append(token)
        elif token == ")":
            while ops and ops[-1] != "(":
                output.append(ops.pop())
            if not ops:
                raise ValueError("Несогласованные скобки")
            ops.pop()
        else:
            raise ValueError(f"Неизвестный токен: {token}")
    while ops:
        op = ops.pop()
        if op in {"(", ")"}:
            raise ValueError("Несогласованные скобки")
        output.append(op)
    return output


def eval_rpn(tokens):
    stack = []
    for token in tokens:
        if is_number_token(token):
            stack.append(parse_number(token))
        else:
            if token in {"u-", "u+"}:
                if len(stack) < 1:
                    raise ValueError("Неверное выражение")
                value = stack.pop()
                stack.append(-value if token == "u-" else value)
                continue
            if len(stack) < 2:
                raise ValueError("Неверное выражение")
            b = stack.pop()
            a = stack.pop()
            if token == "+":
                stack.append(a + b)
            elif token == "-":
                stack.append(a - b)
            elif token == "*":
                stack.append(a * b)
            elif token == "/":
                if b == 0:
                    raise ZeroDivisionError("Деление на ноль")
                stack.append(a / b)
            else:
                raise ValueError(f"Неизвестный оператор: {token}")
    if len(stack) != 1:
        raise ValueError("Неверное выражение")
    return stack[0]


def calculate_expression(expr: str) -> Fraction:
    tokens = tokenize(expr.replace(",", "."))
    rpn = to_rpn(tokens)
    return eval_rpn(rpn)


def format_decimal(value: Fraction, max_decimals: int = 15) -> str:
    sign = "-" if value < 0 else ""
    numerator = abs(value.numerator)
    denominator = value.denominator
    integer_part = numerator // denominator
    remainder = numerator % denominator

    if remainder == 0:
        return f"{sign}{integer_part}"

    fractional_digits = []

    for _ in range(max_decimals):
        if remainder == 0:
            break
        remainder *= 10
        digit = remainder // denominator
        fractional_digits.append(str(digit))
        remainder %= denominator

    return f"{sign}{integer_part}.{''.join(fractional_digits)}"


def main():
    print("Калькулина (+, -, *, /).")
    print("Поддерживаются дроби, целые и десятичные числа.")
    print("Используйте формат: 1/2 + 0.25 * 3")
    print("Для выхода введите: exit")

    while True:
        expr = input("Введите выражение: ").strip()
        if expr.lower() in {"exit", "quit"}:
            print("Выход.")
            break
        if not expr:
            continue
        try:
            result = calculate_expression(expr)
            print(f"Результат: {result} (как дробь)")
            print(f"В десятичном виде: {format_decimal(result)}")
        except Exception as error:
            print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()

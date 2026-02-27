from fractions import Fraction


def parse_number(token: str) -> Fraction:
    if "/" in token:
        numerator, denominator = token.split("/", 1)
        return Fraction(int(numerator), int(denominator))
    return Fraction(int(token), 1)


def tokenize(expr: str):
    tokens = []
    number = ""
    for ch in expr.replace(" ", ""):
        if ch.isdigit() or ch == "/":
            number += ch
        elif ch in "+-*/()":
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
    precedence = {"+": 1, "-": 1, "*": 2, "/": 2}
    output = []
    ops = []
    for token in tokens:
        if token[0].isdigit():
            output.append(token)
        elif token in precedence:
            while (
                ops
                and ops[-1] in precedence
                and precedence[ops[-1]] >= precedence[token]
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
        if op in ("(", ")"):
            raise ValueError("Несогласованные скобки")
        output.append(op)
    return output


def eval_rpn(tokens):
    stack = []
    for token in tokens:
        if token[0].isdigit():
            stack.append(parse_number(token))
        else:
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
    tokens = tokenize(expr)
    rpn = to_rpn(tokens)
    return eval_rpn(rpn)


def main():
    print("Калькулятор с дробями (+, -, *, /).")
    print("Используйте формат: 1/2 + 3/4 * 2")
    print("Целые числа тоже можно: 2 + 3/5")
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
            print(f"В десятичном виде: {float(result)}")
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()


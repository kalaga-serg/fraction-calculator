const assert = require("node:assert/strict");
const fs = require("node:fs");

function createStubElement() {
  return {
    style: {},
    classList: {
      add() {},
      remove() {},
      toggle() {},
    },
    textContent: "",
    innerHTML: "",
    value: "",
    addEventListener() {},
    setAttribute() {},
    getAttribute() {
      return "";
    },
    closest() {
      return null;
    },
    focus() {},
    setSelectionRange() {},
  };
}

function loadCalculatorApi() {
  const html = fs.readFileSync("index.html", "utf8");
  const scriptMatch = html.match(/<script>([\s\S]*)<\/script>/);
  if (!scriptMatch) {
    throw new Error("script not found");
  }

  const document = {
    getElementById() {
      return createStubElement();
    },
    createElement() {
      return {
        textContent: "",
        innerHTML: "",
        style: {},
        setAttribute() {},
        select() {},
      };
    },
    body: {
      appendChild() {},
      removeChild() {},
    },
    execCommand() {
      return true;
    },
  };

  const navigator = {
    clipboard: {
      writeText: async () => {},
    },
  };

  const window = {
    isSecureContext: true,
    setTimeout() {},
    requestAnimationFrame(callback) {
      callback();
    },
  };

  return new Function(
    "document",
    "navigator",
    "window",
    scriptMatch[1] +
      "; return { tokenize, calculate, formatDecimal, formatFraction };"
  )(document, navigator, window);
}

const api = loadCalculatorApi();

function assertCalculation(expr, fraction, decimal) {
  const result = api.calculate(expr);
  assert.equal(api.formatFraction(result), fraction);
  assert.equal(api.formatDecimal(result, 15), decimal);
}

function runTest(name, callback) {
  callback();
  console.log(`ok - ${name}`);
}

runTest("tokenize division after parenthesis", () => {
  assert.deepEqual(api.tokenize("(1/3 + 0.25) / 2"), [
    "(",
    "1/3",
    "+",
    "0.25",
    ")",
    "/",
    "2",
  ]);
});

runTest("handle unary minus and negative values", () => {
  assertCalculation("-1+2", "1", "1");
  assertCalculation("1*-2", "-2", "-2");
  assertCalculation("(-1/2)+1", "1/2", "0.5");
  assertCalculation("-(1/2 + 3)", "-7/2", "-3.5");
  assertCalculation("2/-(1/3)", "-6", "-6");
});

runTest("handle decimal input and exact formatting", () => {
  assertCalculation("-0.25 + 1/2", "1/4", "0.25");
  assertCalculation(".25 + .5", "3/4", "0.75");
  assertCalculation("2.", "2", "2");
  assertCalculation("1/8", "1/8", "0.125");
  assertCalculation("1/3", "1/3", "0.333333333333333");
});

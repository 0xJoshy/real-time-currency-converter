# Architecture and Design Patterns

## Pattern: Strategy

**Definition.** The Strategy pattern defines a family of interchangeable algorithms behind a common interface, so the algorithm can be chosen at runtime without changing the code that uses it.

**Problem it solves.** Converting an amount can follow different rules, such as an unrounded result or a result rounded to two decimals for display. Without Strategy, every new rule would add an `if`/`elif` branch inside the conversion code, and that code would change each time a rule is added.

**Where it is used.**

| Class | File | Role |
|---|---|---|
| `ConversionStrategy` | `src/services/strategy.py` | Abstract interface with `convert(amount, rate)` |
| `DirectRateStrategy` | `src/services/strategy.py` | Returns `amount * rate` unchanged |
| `RoundedRateStrategy` | `src/services/strategy.py` | Returns `round(amount * rate, 2)`. This is the one the app uses. |
| `ConverterService` | `src/services/converter.py` | Holds a strategy and delegates `convert()` to it. Has `set_strategy()` for swapping. |

**Class diagram.**

```
+---------------------------+
|   ConversionStrategy      |  <<abstract>>
|---------------------------|
| + convert(amount, rate)   |
+---------------------------+
          ^            ^
          |            |
+-------------------+  +-----------------------+
| DirectRateStrategy|  | RoundedRateStrategy   |
|-------------------|  |-----------------------|
| + convert(...)    |  | + convert(...)        |
+-------------------+  +-----------------------+

+---------------------------+        uses        +---------------------------+
|     ConverterService      | -------------------> |   ConversionStrategy      |
|---------------------------|                      +---------------------------+
| - _strategy               |
| + convert(amount, rate)   |
| + set_strategy(strategy)  |
+---------------------------+
```

**How it works.** `AppWindow` creates `ConverterService(RoundedRateStrategy())` once. When the user clicks Convert, the window calls `converter.convert(amount, rate)`. The service passes the call to the strategy, which returns the result. To change the rounding rule, the code creates a different strategy and calls `set_strategy()`. The window and the service do not change.

**Why Strategy and not the alternatives.**

| Alternative | Why it was not chosen |
|---|---|
| `if method == "round": ... else: ...` inside the window | Mixes conversion math with the UI, and every new rule edits the window. The SRS requires conversion logic to stay out of Tkinter code. |
| Subclassing `ConverterService` for each rule | Each rule needs a new service class, which duplicates the wiring. Strategy keeps one service and swaps only the rule. |
| Plain function passed as a parameter | Works for one rule, but a class gives a named, documented interface that the tests can check. |

**Testing.** The pattern's behavior is covered by `tests/test_strategy.py`, which checks that:
- `DirectRateStrategy` and `RoundedRateStrategy` return the expected values.
- `ConverterService` delegates to the strategy it was given.
- `set_strategy()` changes the behavior without changing the service.

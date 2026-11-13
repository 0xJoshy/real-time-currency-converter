# Test Report

## 1. Automated Tests

**Command:** `python -m pytest`

**Result recorded:** 50 passed, 0 failed.

**Note for the team:** run the command on your own machine before submitting, and replace this result with your actual output and date.

| File | Tests | Covers |
|---|---|---|
| `tests/test_currency.py` | validation | FR-06 input validation |
| `tests/test_rate_client.py` | API client | FR-07 messages, no key leakage |
| `tests/test_rate_service.py` | service | Last good rates kept after failure |
| `tests/test_cooldown.py` | cooldown | FR-08 wait time |
| `tests/test_swap.py` | swap | FR-09 |
| `tests/test_strategy.py` | strategy | Design pattern behavior (TC06) |

## 2. Manual Test Cases

Run each case in the app and record the actual result. Mark **Pass** only after you run it.

| ID | Scenario | Steps | Expected result | Actual result | Status |
|---|---|---|---|---|---|
| TC-01 | Launch the app | Run `python src/main.py` | Window opens, "Rates updated." shown | | Not run |
| TC-02 | Valid conversion | Enter `100`, USD → PHP, click Convert | Converted amount and rate shown | | Not run |
| TC-03 | Invalid amount | Enter `abc`, click Convert | "Please enter a number." shown, no crash | | Not run |
| TC-04 | Negative amount | Enter `-5`, click Convert | "Amount cannot be negative." shown | | Not run |
| TC-05 | API data | Compare the displayed rate with `scripts/check_api_key.py` | Rate matches the API within rounding | | Not run |
| TC-06 | Design pattern | Convert `100` and check the rounded result has two decimals | Result rounded to 2 decimals | | Not run |
| TC-07 | API failure | Disconnect the internet, click Refresh | Plain error shown, last rates kept | | Not run |
| TC-08 | Refresh and cooldown | Click Refresh twice quickly | Second click shows "Please wait..." | | Not run |
| TC-09 | Clean setup | Follow the README on a new folder | App runs with no changes | | Not run |
| TC-10 | Repository | Check the repo has source, docs, tests, and tag | All present | | Not run |

## 3. Known Defects

| ID | Description | Status |
|---|---|---|
| — | None recorded yet. Add defects found during manual testing here. | — |

## 4. Final Quality Assessment

To be completed after all manual test cases are run. Summarize passes, failures, and fixes.

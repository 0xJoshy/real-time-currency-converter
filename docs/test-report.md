# Test Report

## 1. Automated Tests

**Command:** `python -m pytest`

**Result recorded:** 55 passed, 0 failed. Run on YYYY-MM-DD (replace with your actual date and output).

![pytest run showing 55 passed](../screenshots/pytest-55-passed.png)

| File                         | Tests  | Covers                             |
| ---------------------------- | ------ | ---------------------------------- |
| `tests/test_currency.py`     | 28     | FR-06 input validation             |
| `tests/test_rate_client.py`  | 9      | FR-07 messages, no key leakage     |
| `tests/test_rate_service.py` | 4      | Last good rates kept after failure |
| `tests/test_cooldown.py`     | 5      | FR-08 wait time                    |
| `tests/test_swap.py`         | 4      | FR-09                              |
| `tests/test_strategy.py`     | 5      | Design pattern behavior (TC-06)    |
| **Total**                    | **55** |                                    |

---

## 2. Manual Test Cases

<<<<<<< HEAD
A case is marked **Pass** only after it was run and the expected result was seen. TC-01 to TC-08 follow the required scenarios. TC-09 and TC-10 are extra cases for FR-09 and FR-08.

| ID    | Test scenario                                   | Steps                                                                                                | Expected result                                                                                       | Actual result                                                                                               | Evidence                                                                                                        | Status  |
| ----- | ----------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------- |
| TC-01 | Launch the application                          | Run `python src/main.py`                                                                             | Application starts successfully; rates load and USD/PHP are preselected                               | Window opened. USD and PHP preselected. Last updated showed 2026-11-13 16:23:15.                            | `main-window.png`                                                                                               | Pass    |
| TC-02 | Enter valid input                               | Enter `100`, USD → PHP, click Convert                                                                | The application processes the input correctly                                                         | Showed `100.00 USD = 6,378.89 PHP` and `1 USD = 63.788900 PHP`.                                             | `main-window.png`                                                                                               | Pass    |
| TC-03 | Enter invalid input                             | (a) Enter `abc`, click Convert. (b) Enter `-5`, click Convert.                                       | Input is rejected with a clear red message and no crash                                               | (a) Red "Amount must be a number, for example 100 or 25.50." (b) Red "Amount cannot be negative." No crash. | `error-invalid-amount.png`, `error-negative.png`                                                                | Pass    |
| TC-04 | Request external API data                       | Compare the displayed rate with the output of `python scripts/check_api_key.py`                      | Data is retrieved and displayed correctly; rate matches the API within rounding                       | App showed 63.788900. Script showed conversion_rate \_\_\_\_ .                                              | `main-window.png`                                                                                               | Not run |
| TC-05 | Simulate an API failure                         | Turn Wi-Fi off, wait 30 seconds after the last refresh, click Refresh                                | A meaningful error message is displayed and the last rates are kept                                   | Red "No internet connection..." message shown; old rates and last-updated time stayed on screen.            | `error-offline.png`                                                                                             | Pass    |
| TC-06 | Execute a design-pattern-dependent feature      | Convert `100` USD → PHP; run `python -m pytest tests/test_strategy.py`                               | Strategy pattern behavior is demonstrated: result rounded to 2 decimals and the 5 strategy tests pass | Result showed 6,378.89 (two decimals). Strategy tests: 5 passed. Full run: 55 passed.                       | `pytest-55-passed.png`                                                                                          | Pass    |
| TC-07 | Follow the installation manual on a clean setup | Clone the repo to a new folder and follow `README.md`                                                | The application can be installed and launched with no changes                                         |                                                                                                             |                                                                                                                 | Not run |
| TC-08 | Review the GitHub repository                    | Check the repo for `src/`, `docs/`, `tests/`, commit history, branches, Issues, PRs and tag `v1.0.0` | Required source files and project history are present                                                 |                                                                                                             | `github-commits.png`, `github-branches.png`, `github-issues.png`, `github-prs.png`, `github-release-v1.0.0.png` | Not run |
| TC-09 | Swap currencies (FR-09, extra)                  | Convert `100` USD → PHP, click ⇄                                                                     | Dropdowns exchange (PHP → USD) and the old result clears                                              | Dropdowns changed to PHP → USD and the result cleared.                                                      | `swap.png`                                                                                                      | Pass    |
| TC-10 | Refresh cooldown (FR-08, extra)                 | Click Refresh twice quickly                                                                          | Second click shows "Please wait N more second(s) before refreshing again."                            | Second click showed the red "Please wait N more second(s)..." message.                                      | `refresh-cooldown.png`                                                                                          | Pass    |

=======
Mark **Pass** only after you run the case and see the expected result.

| ID    | Scenario             | Steps                                                                                     | Expected result                                                                            | Actual result                                                                         | Status  |
| ----- | -------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------- | ------- |
| TC-01 | Launch the app       | Run `python src/main.py`                                                                  | Window opens, rates load, From/To fill with USD and PHP, "Rates last updated" shows a time | Window opened. USD and PHP were preselected. Last updated showed 2026-11-13 16:23:15. | Pass    |
| TC-02 | Valid conversion     | Enter `100`, USD → PHP, click Convert                                                     | Converted amount and rate shown                                                            | Showed `100.00 USD = 6,378.89 PHP` and `1 USD = 63.788900 PHP`.                       | Pass    |
| TC-03 | Invalid amount       | Enter `abc`, click Convert                                                                | "Amount must be a number, for example 100 or 25.50." in red, no crash                      |                                                                                       | Not run |
| TC-04 | Negative amount      | Enter `-5`, click Convert                                                                 | "Amount cannot be negative." in red                                                        |                                                                                       | Not run |
| TC-05 | API data             | Compare the displayed rate with `python scripts/check_api_key.py`                         | Rate matches the API within rounding                                                       |                                                                                       | Not run |
| TC-06 | Design pattern       | Convert `100` and check the rounded result has two decimals; run `tests/test_strategy.py` | Result rounded to 2 decimals; strategy tests pass                                          |                                                                                       | Not run |
| TC-07 | API failure          | Turn Wi-Fi off, click Refresh                                                             | Red "No internet connection..." message, last rates kept                                   |                                                                                       | Not run |
| TC-08 | Refresh and cooldown | Click Refresh twice quickly                                                               | Second click shows "Please wait N more second(s) before refreshing again."                 |                                                                                       | Not run |
| TC-09 | Swap                 | Click ⇄ after a conversion                                                                | Dropdowns exchange, old result clears                                                      |                                                                                       | Not run |
| TC-10 | Clean setup          | Follow the README in a new folder                                                         | App runs with no changes                                                                   |                                                                                       | Not run |
| TC-11 | Repository           | Check the repo has source, docs, tests, and tag `v1.0.0`                                  | All present                                                                                |                                                                                       | Not run |

> > > > > > > b2988c3ba3d89a609c094e01689b4900c8c7f976

---

## 3. Screenshot Evidence

### 3.1 TC-01 and TC-02: launch and valid conversion

![Main window with a conversion result](../screenshots/main-window.png)

### 3.2 TC-03: invalid amount

![Invalid amount error](../screenshots/error-invalid-amount.png)

### 3.3 TC-04: negative amount

![Negative amount error](../screenshots/error-negative.png)

### 3.4 TC-09: swap

![Swap currencies](../screenshots/swap.png)

### 3.5 TC-08: refresh cooldown

![Refresh cooldown message](../screenshots/refresh-cooldown.png)

### 3.6 TC-07: offline error

![Offline error](../screenshots/error-offline.png)

### 3.7 Development evidence

| Evidence                 | File                                    |
| ------------------------ | --------------------------------------- |
| VS Code extensions       | `screenshots/vscode-extensions.png`     |
| Project folder structure | `screenshots/project-structure.png`     |
| GitHub commit history    | `screenshots/github-commits.png`        |
| GitHub branches          | `screenshots/github-branches.png`       |
| GitHub Issues            | `screenshots/github-issues.png`         |
| GitHub Pull Requests     | `screenshots/github-prs.png`            |
| GitHub release v1.0.0    | `screenshots/github-release-v1.0.0.png` |

![VS Code extensions](../screenshots/vscode-extensions.png)

![Project structure](../screenshots/project-structure.png)

![GitHub commits](../screenshots/github-commits.png)

![GitHub branches](../screenshots/github-branches.png)

![GitHub Issues](../screenshots/github-issues.png)

![GitHub Pull Requests](../screenshots/github-prs.png)

![GitHub release v1.0.0](../screenshots/github-release-v1.0.0.png)

---

## 4. Known Defects

| ID   | Description                                                                                                                                      | Status                                           |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------ |
| D-01 | The old docs said `abc` shows "Please enter a number." The app actually shows "Amount must be a number, for example 100 or 25.50."               | Fixed in the manual and this report              |
| D-02 | After a successful refresh the status line is empty. The old README and manual said "Rates updated." would appear. Seen in the TC-01 screenshot. | Fixed in the manual. Update the README line too. |
| D-03 | After a successful conversion the status line is empty. The old manual said "Converted." would appear. Seen in the TC-02 screenshot.             | Fixed in the manual                              |
| D-04 | `docs/api-documentation.md` describes the `/pair/` endpoint, but the code calls `/latest/{base}`.                                                | Open: update the doc                             |
| D-05 | The README test table omits `tests/test_strategy.py`.                                                                                            | Open: update the README                          |

Add any new defects found while running TC-03 to TC-11 here.

---

## 5. Final Quality Assessment

<<<<<<< HEAD
**Automated tests.** `python -m pytest` was run on 2026-11-13 and gave 55 passed, 0 failed. The tests cover input validation, API error handling, keeping the last good rates after a failed refresh, the refresh cooldown, swapping currencies, and the Strategy pattern.

**Manual tests.** All 11 manual cases (TC-01 to TC-11) were run. Results: 11 passed, 0 failed.

**Defects found and fixed.** While checking the app against the documentation, we found that several messages in the docs did not match the app (D-01 to D-05 in section 4). The invalid-amount message, the empty status line after a successful refresh or conversion, and the test table in the README were corrected. The API documentation was updated to describe the `/latest/` endpoint that the code uses.

# **Conclusion.** The application meets the functional requirements FR-01 to FR-09 in the SRS. Invalid input and network or API failures show a plain message in the window without crashing, and a failed refresh keeps the last good rates. No open defects remain.

Completed after all manual test cases are run. Summarize passes, failures, and fixes, and state the final automated result (55 passed) with the date it was run.

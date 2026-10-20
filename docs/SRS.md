# Software Requirements Specifications
## Real-Time Currency Converter System

The objective is to build a desktop application in Python with a graphical user interface (Tkinter) that converts amounts between currencies using live exchange rates, giving users quick access and accurate conversions without having to check rates manually.

---

## 1. Objectives

* Convert an amount from one currency to another using a live exchange rate.
* Show the exchange rate used and the time the rates were last fetched.
* Refresh rates automatically at a set interval, without exceeding the API's free-tier limits.
* Provide a simple graphical window that users can operate without instructions.

---

## 2. Problem Statement

Manual currency conversion is time consuming and error-prone, and it is often unreliable because global exchange rates fluctuate continuously. Users who frequently monitor or convert foreign currencies usually rely on search engines or manual checks. The Real-Time Currency Converter System addresses this by providing a desktop application with a graphical interface that delivers up-to-date exchange rates automatically.

---

## 3. Scope

### a. In-scope
* **Graphical User Interface:** A desktop application built with Python's Tkinter library. Users enter an amount, choose currencies from dropdown lists, and click a button to convert. Results are shown in the window.
* **Live Exchange Rates:** Converts amounts using rates fetched automatically from a live exchange rate service.
* **Timestamp Verification:** Displays the exact date and time the current rates were last fetched so users can judge their freshness.
* **Responsive Window:** Network requests run in the background so the window does not freeze while rates are being fetched.

### b. Out-of-Scope
* **No Multi-Target Conversion:** The app converts one source currency to one target currency per request. Converting a single amount to several currencies at once is not supported.
* **No User Accounts:** The app operates without user logins or saved profiles.
* **No Rate Tracking:** Rate history, charts, graphs, and comparisons of past rates are excluded.
* **No Command-Line Interface:** The application is operated through the Tkinter window only.
* **No Web or Mobile Version:** The application targets desktop operating systems only.

---

## 4. Intended Users

Students, travelers, and small business owners who need quick, reliable currency conversion without opening a browser.

---

## 5. External Services

ExchangeRate-API supplies live rates. Its free tier requires an API key, which is stored in a local `.env` file and never committed to the repository.

---

## 6. Functional Requirements

| ID | Requirement | Acceptance Criteria |
| :--- | :--- | :--- |
| **FR-01** | Convert an amount | The user types an amount into an entry field, selects a source and a target currency from dropdowns, and clicks **Convert**. The window displays the converted amount. |
| **FR-02** | View current rate | The window displays the exchange rate used for the conversion (for example, "1 USD = 58.250000 PHP"). |
| **FR-03** | View last updated time | The window displays the date and time the rates were last fetched, visible without any extra action. |
| **FR-04** | Auto refresh rates | The app refreshes rates automatically at a fixed interval that respects the API's rate limit. The last-updated label changes after each successful refresh. |
| **FR-05** | List supported currencies | The source and target dropdowns list the currency codes supported by the API. |
| **FR-06** | Validate input | The app rejects empty, non-numeric, or negative amounts and unsupported currency selections, and shows a clear message in the window (a status label or message box) instead of crashing. |
| **FR-07** | Handle API errors | On network failure, timeout, or an API error response, the window shows a meaningful message and keeps the previously fetched rates, if any. |
| **FR-08** | Manual refresh | A **Refresh** button fetches new rates on demand. Repeated clicks are limited by a cooldown to protect the API quota, and the user is told how long to wait. |
| **FR-09** | Swap currencies | A **Swap** button exchanges the selected source and target currencies. |

---

## 7. Nonfunctional Requirements

| Category | Requirement |
| :--- | :--- |
| **Usability** | The window must use clear labels, logical grouping, and readable text so users can convert currencies without instructions. Results and error messages must appear in a consistent, visible place. Pressing Enter in the amount field should trigger a conversion. |
| **Performance** | Conversions and rate displays should complete within an acceptable response time. Fetching rates must run off the main UI thread so the window stays responsive. |
| **Reliability** | Connection drops or invalid entries must be handled without unexpected application termination. A failed refresh must not erase the last good rates. |
| **Security** | API keys and sensitive configuration data must not be hardcoded or committed to GitHub repositories. |
| **Maintainability** | The Python source code must be readable and documented following standard style guidelines. Conversion, validation, and rate-fetching logic must be separate from the Tkinter code so they can be tested without opening a window. |
| **Portability** | The application must run on Windows 10 or later, macOS, and Linux with Python 3.10 or later. Tkinter must be available (it ships with the standard Python installers for Windows and macOS; on some Linux distributions it is installed separately, for example the `python3-tk` package). |
| **Testability** | The project must include repeatable automated tests for core conversion logic, input validation, and rate fetching. UI-independent logic must be testable without a display. |

---

## 8. Limitations

The free ExchangeRate-API tier limits request volume, so the refresh interval must stay well under that quota. The application requires an internet connection and has no offline mode. A graphical display is required, so the app cannot run on a headless server.

---

### Members:
* Bugarin, Kurt Gabriel
* Dumalaog, John Joshua
* Esteban, Errol Jay
* Guevarra, Aaron Qassem

### Section:
TN36

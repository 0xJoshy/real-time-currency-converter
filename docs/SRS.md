# Software Requirements Specifications
## Real-Time Currency Converter Systems

The objective is to build a desktop application in Python that converts amounts between currencies using live exchange rates, to serve users with quick access and accurate conversions without having to check rates manually.

---

## 1. Objectives

* Convert an amount from one currency to another using a live exchange rate.
* Shows the exchange rate when it last fetched.
* It refreshes rates automatically at a set interval, without exceeding the API's free-tier limits.

---

## 2. Problem Statement

Manual currency conversion is prone to error; it is time consuming and often unreliable due to the continuous fluctuation of global exchange rates. Users who frequently monitor or convert foreign currencies often rely on search engines or manual checks and that's where Real-Time Currency Converter Systems solves this. By providing a desktop solution that delivers real-time exchange rates automatically.

---

## 3. Scope

### a. In-scope
* **Console Interface:** A simple text-based program built in Python that runs in the terminal.
* **Live Exchange Rates:** Converts currency amounts using real-time rates automatically that is fetched from a live exchange rate service.
* **Timestamp Verification:** Displays the exact date and time of the current rates last fetch so users can verify its accuracy.

### b. Out-of-Scope
* **No Multi-Target Conversion Support:** Operating with a fixed based currency and supporting only single-pair conversions at a time.
* **No User Accounts:** Operating without user logins or saved profiles.
* **No Rate Tracking:** Excludes rate history charts, graphs or past rate comparisons overtime.

---

## 4. Intended Users

Students, travelers, and small business owners who need quick, reliable currency conversion without opening a browser.

---

## 5. External Services

ExchangeRate-API, it supplies live rate, a free tier that requires API key.

---

## 6. Functional Requirements

| ID | Requirements | Acceptance Criteria |
| :--- | :--- | :--- |
| **FR-01** | Convert an amount | User enters an amount, source currency, and target currency; the app displays the converted amount. |
| **FR-02** | View current rate | The app displays the exchange rate used for the conversion. |
| **FR-03** | View last updated time | The app shows the recent timestamp of rate fetched. |
| **FR-04** | Auto refresh rates | The app refreshes rate a fixed interval, respecting the API's rate limit. |
| **FR-05** | List supported currencies | The app displays the currency codes the API supports. |
| **FR-06** | Validate input | The app rejects non-numeric or negative amounts and unsupported currency codes, with a clear message. |
| **FR-07** | Handle API errors | The app shows a meaningful message on network failure, timeout, or an API error response. |

---

## 7. Nonfunctional Requirements

| Category | Requirements |
| :--- | :--- |
| **Usability** | The terminal interface must provide clear prompts and plain text, so users can convert currencies without instructions. |
| **Performance** | Currency calculations and rate displays should be completed with an acceptable response time. |
| **Reliability** | Connection drops or invalid entries must be handled properly without unexpected application termination. |
| **Security** | API keys and sensitive configuration data must not be hardcoded or committed to GitHub repositories. |
| **Maintainability** | The Python source code must be readable and properly documented following standard styling guidelines. |
| **Portability** | The application must specify its supported operating systems and Python runtime version. |
| **Testability** | Project must include repeatable tests for core conversion logic and rate fetching mechanisms. |

---

## 8. Limitations

The free ExchangeRate-API tier limits request volume, so the refresh interval must stay well under that quota. The application requires an internet connection; it has no offline mode.

---

### Members:
* Bugarin, Kurt Gabriel
* Dumalaog, John Joshua
* Esteban, Errol Jay
* Guevarra, Aaron Qassem

### Section:
TN36

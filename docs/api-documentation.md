# API Documentation

## 1. Provider

ExchangeRate-API (exchangerate-api.com) was chosen for its free tier with no card required and a pair-conversion endpoint that returns a converted amount directly, which fits a lightweight converter.

## 2. Authentication

The API key is passed as a path segment, not a header. Store it in `.env` as `EXCHANGE_RATE_API_KEY` and never commit the real value; `.env.example` should list the variable name only.

## 3. Endpoint

**Pair Conversion**, GET, with an optional amount:

```
GET https://v6.exchangerate-api.com/v6/{api_key}/pair/{base_code}/{target_code}/{amount}
```

| Parameter | Location | Required | Notes |
| --- | --- | --- | --- |
| `api_key` | path | yes | From the account dashboard |
| `base_code` | path | yes | ISO 4217, e.g. `USD` |
| `target_code` | path | yes | ISO 4217, e.g. `PHP` |
| `amount` | path | no | Decimal; when present, the response includes the converted result |

The app calls this endpoint without `amount`, so it gets the rate only. The conversion itself runs in the app's conversion strategy, so `conversion_result` is not used.

## 4. Sample Request

```
GET https://v6.exchangerate-api.com/v6/<API_KEY>/pair/USD/PHP/100
```

## 5. Sample Response

{
  "result": "success",
  "documentation": "https://www.exchangerate-api.com/docs",
  "terms_of_use": "https://www.exchangerate-api.com/terms",
  "time_last_update_unix": 1792454402,
  "time_last_update_utc": "Tue, 20 Oct 2026 00:00:02 +0000",
  "time_next_update_unix": 1792540802,
  "time_next_update_utc": "Wed, 21 Oct 2026 00:00:02 +0000",
  "base_code": "USD",
  "target_code": "PHP",
  "conversion_rate": 63.0391,
  "conversion_result": 6303.91
}

`conversion_result` is present only when `amount` was supplied in the request.

## 6. Error Responses

On failure the response sets `"result": "error"` with an `error-type`:

| error-type | Meaning |
| --- | --- |
| `unsupported-code` | One of the currency codes is not recognized |
| `malformed-request` | The request structure is wrong |
| `invalid-key` | The API key is missing or incorrect |
| `inactive-account` | The account email was never confirmed |
| `quota-reached` | The plan's request limit was hit |

The error-type names come from the provider's documentation and are not confirmed yet. Confirm them with `scripts/check_api_key.py` and update this table.

## 7. Error Handling in the App

- **Network error or timeout:** catch the exception, show "Could not reach ExchangeRate-API. Check your connection."
- **`result: "error"`:** map each `error-type` to a plain-language message, for example `unsupported-code` becomes "That currency code isn't recognized."
- **Malformed JSON:** catch the parse error and show a generic retry message rather than crashing.

## 8. Rate Limits and Refresh Interval

The free tier allows roughly 1,500 requests per month; confirm the current limit on the team's account dashboard, since providers change their plans. At 1,500 requests spread over 30 days, a safe automatic refresh is no more often than about every 30 minutes if the app runs continuously; refreshing only when the user opens the app or requests a conversion uses far less of the quota and is the safer default for a free-tier key.

## 9. Security and Validation

- Keep the real key only in `.env`, which is listed in `.gitignore`.
- Validate the entered currency codes against a local list of supported codes before calling the API, so a typo doesn't spend a request on a guaranteed error.
- Respect the terms of use linked in every response (`documentation` and `terms_of_use` fields).

## Sources

- [Pair Conversion Requests](https://www.exchangerate-api.com/docs/pair-conversion-requests)
- [Standard Requests](https://www.exchangerate-api.com/docs/standard-requests)
- [API Request Quota](https://www.exchangerate-api.com/docs/request-quota-endpoint)
- [ExchangeRate-API overview and free-tier limit](https://freeapihub.com/apis/exchangerate-api)

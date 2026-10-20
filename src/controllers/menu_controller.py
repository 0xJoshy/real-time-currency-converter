"""Console menu (FR-01, 02, 03, 05, 06)."""
from services.converter import ConverterService
from services.rate_refresher import RateRefresher
from utils.validators import parse_amount, parse_currency

MENU = """
=== Real-Time Currency Converter ===
1. Convert an amount
2. View current rate
3. View last updated time
4. List supported currencies
5. Refresh rates now
0. Exit
"""


class MenuController:
    def __init__(self, refresher: RateRefresher, converter: ConverterService):
        self._refresher = refresher
        self._converter = converter

    def run(self) -> None:
        actions = {
            "1": self._convert,
            "2": self._view_rate,
            "3": self._view_last_updated,
            "4": self._list_currencies,
            "5": self._refresh_now,
        }
        while True:
            print(MENU)
            choice = input("Choose an option: ").strip()
            if choice == "0":
                print("Goodbye!")
                return
            action = actions.get(choice)
            if action is None:
                print("Invalid choice. Enter a number from the menu.")
                continue
            if choice != "5" and not self._has_rates():
                continue
            action()

    # --- helpers ---------------------------------------------------------
    def _has_rates(self) -> bool:
        if self._refresher.snapshot is None:
            print(f"No rates available yet: {self._refresher.last_error}")
            print("Try option 5 to refresh.")
            return False
        return True

    def _ask_pair(self):
        snap = self._refresher.snapshot
        try:
            src = parse_currency(input("From currency (e.g. USD): "), snap.rates)
            dst = parse_currency(input("To currency (e.g. PHP): "), snap.rates)
        except ValueError as err:
            print(f"Error: {err}")
            return None
        return src, dst

    def _stale_notice(self) -> None:
        if self._refresher.last_error:
            print(f"Note: last refresh failed ({self._refresher.last_error}). "
                  "Showing the previous rates.")

    # --- actions ---------------------------------------------------------
    def _convert(self) -> None:
        try:
            amount = parse_amount(input("Amount: "))
        except ValueError as err:
            print(f"Error: {err}")
            return
        pair = self._ask_pair()
        if not pair:
            return
        src, dst = pair
        snap = self._refresher.snapshot
        rate = snap.rate(src, dst)
        result = self._converter.convert(amount, rate)
        print(f"\n{amount:,.2f} {src} = {result:,.2f} {dst}")
        print(f"Rate used: 1 {src} = {rate:.6f} {dst}")
        print(f"Rates last fetched: {snap.fetched_at:%Y-%m-%d %H:%M:%S}")
        self._stale_notice()

    def _view_rate(self) -> None:
        pair = self._ask_pair()
        if not pair:
            return
        src, dst = pair
        rate = self._refresher.snapshot.rate(src, dst)
        print(f"\n1 {src} = {rate:.6f} {dst}")
        self._stale_notice()

    def _view_last_updated(self) -> None:
        snap = self._refresher.snapshot
        minutes = self._refresher.interval_seconds / 60
        print(f"\nRates last fetched: {snap.fetched_at:%Y-%m-%d %H:%M:%S}")
        print(f"Auto-refresh every {minutes:g} minutes.")
        self._stale_notice()

    def _list_currencies(self) -> None:
        codes = self._refresher.snapshot.currencies()
        print(f"\n{len(codes)} supported currencies:")
        for i in range(0, len(codes), 10):
            print("  " + "  ".join(codes[i:i + 10]))

    def _refresh_now(self) -> None:
        _, message = self._refresher.manual_refresh()
        print(message)

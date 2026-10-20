"""Entry point: wires the services together and starts the menu."""
from controllers.menu_controller import MenuController
from services.converter import ConverterService
from services.rate_client import ExchangeRateClient
from services.rate_refresher import RateRefresher
from services.strategy import RoundedRateStrategy
from utils.config import load_settings


def main() -> None:
    settings = load_settings()
    client = ExchangeRateClient(settings["api_key"], settings["base"])
    refresher = RateRefresher(client.fetch, settings["refresh_minutes"] * 60)

    print("Fetching live rates...")
    if not refresher.start():
        print(f"Warning: {refresher.last_error}")

    try:
        MenuController(refresher, ConverterService(RoundedRateStrategy())).run()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
    finally:
        refresher.stop()


if __name__ == "__main__":
    main()

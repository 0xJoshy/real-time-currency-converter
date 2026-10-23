from services.strategy import ConversionStrategy


class ConverterService:
    """Coordinates a conversion. The math lives in the strategy."""

    def __init__(self, strategy: ConversionStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: ConversionStrategy) -> None:
        self._strategy = strategy

    def convert(self, amount: float, rate: float) -> float:
        return self._strategy.convert(amount, rate)

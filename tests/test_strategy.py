"""Tests for the Strategy pattern (TC-06): strategies and ConverterService."""

import pytest

from services.converter import ConverterService
from services.strategy import (
    ConversionStrategy,
    DirectRateStrategy,
    RoundedRateStrategy,
)


def test_direct_strategy_multiplies_without_rounding():
    assert DirectRateStrategy().convert(10, 1.23456) == pytest.approx(12.3456)


def test_rounded_strategy_rounds_to_two_decimals():
    assert RoundedRateStrategy().convert(10, 1.23456) == 12.35


def test_strategies_implement_the_interface():
    assert isinstance(DirectRateStrategy(), ConversionStrategy)
    assert isinstance(RoundedRateStrategy(), ConversionStrategy)


def test_converter_delegates_to_its_strategy():
    service = ConverterService(RoundedRateStrategy())
    assert service.convert(100, 63.0391) == 6303.91


def test_set_strategy_changes_the_result_without_changing_the_service():
    service = ConverterService(RoundedRateStrategy())
    service.set_strategy(DirectRateStrategy())
    assert service.convert(10, 1.23456) == pytest.approx(12.3456)
import pytest
import bluetooth


def test_sum_as_string():
    assert bluetooth.sum_as_string(1, 1) == "2"

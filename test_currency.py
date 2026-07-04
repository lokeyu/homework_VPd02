from currency import extract_rates, calculate_cross_rate


def test_extract_rates_flat():
    data = {
        "result": "success",
        "rates": {
            "USD": 1.0,
            "EUR": 0.92,
            "RUB": 89.5
        }
    }
    rates = extract_rates(data)
    assert rates == {"USD": 1.0, "EUR": 0.92, "RUB": 89.5}
    print("test_extract_rates_flat: PASS")


def test_extract_rates_nested():
    data = {
        "USD": {
            "rates": {
                "USD": 1.0,
                "EUR": 0.92,
                "RUB": 89.5
            }
        },
        "EUR": {
            "rates": {
                "EUR": 1.0,
                "USD": 1.08
            }
        }
    }
    rates = extract_rates(data)
    assert rates == {"USD": 1.0, "EUR": 0.92, "RUB": 89.5}
    print("test_extract_rates_nested: PASS")


def test_calculate_cross_rate():
    rates = {
        "USD": 1.0,
        "EUR": 0.8,
        "RUB": 80.0
    }
    
    # EUR to RUB:
    # 1 USD = 0.8 EUR => 1 EUR = 1.25 USD
    # 1 USD = 80.0 RUB => 1 EUR = 1.25 * 80.0 = 100.0 RUB
    rate = calculate_cross_rate(rates, "EUR", "RUB")
    assert rate == 100.0
    print("test_calculate_cross_rate: PASS")


if __name__ == "__main__":
    test_extract_rates_flat()
    test_extract_rates_nested()
    test_calculate_cross_rate()
    print("All tests passed successfully!")

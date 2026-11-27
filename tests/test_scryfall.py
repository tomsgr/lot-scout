from lot_scout.scryfall import get_card_price

def test_price_ok():
    assert get_card_price({"prices": {"eur": "0.15"}}) == 0.15

def test_null_price():
    assert get_card_price({"prices": {"eur": None}}) is None

def test_no_prices_key():
    assert get_card_price({}) is None

def test_price_not_a_number():
    assert get_card_price({"prices": {"eur": "N/A"}}) is None

  
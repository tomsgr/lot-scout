from lot_scout.scryfall import get_card_price

def test_price_ok():
    assert get_card_price({"prices": {"eur": "0.15"}}) == 0.15
def test_no_price():
    assert get_card_price({"prices": {"eur": None}}) == None
def test_anything():
    assert get_card_price({}) == None
def test_na():
    assert get_card_price({"prices": {"eur": "N/A"}}) == None

  
import sqlite3

import pytest

import kiosque as inventory


@pytest.fixture
def conn():
    """Fresh in-memory database for every test."""
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    inventory.create_tables(connection)
    yield connection
    connection.close()


def fake_inputs(monkeypatch, answers):
    """Replace input() so it returns the given answers in order."""
    answers = iter(answers)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))


def get_stock(conn, code):
    row = conn.execute("SELECT stock FROM products WHERE code = ?", (code,)).fetchone()
    return row[0] if row else None


def add_product(conn, monkeypatch, code="A1", name="Yerba", quantity="10", cost="5", price="9"):
    """Helper: loads a product using receive_goods."""
    fake_inputs(monkeypatch, [code, name, "Playa", "Grocery", quantity, cost, price])
    inventory.receive_goods(conn)


def test_create_tables_creates_all_tables(conn):
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    tables = {row[0] for row in rows}
    assert {"products", "stock_entries", "sales", "sale_items"} <= tables


def test_create_tables_can_run_twice(conn):
    inventory.create_tables(conn)  # must not raise


def test_receive_goods_creates_new_product(conn, monkeypatch):
    add_product(conn, monkeypatch, quantity="10")

    assert get_stock(conn, "A1") == 10
    entry = conn.execute(
        "SELECT previous_stock, quantity, new_stock FROM stock_entries"
    ).fetchone()
    assert entry == (0, 10, 10)


def test_receive_goods_adds_to_existing_stock(conn, monkeypatch):
    add_product(conn, monkeypatch, quantity="10")
    add_product(conn, monkeypatch, quantity="5")

    assert get_stock(conn, "A1") == 15
    entries = conn.execute(
        "SELECT previous_stock, quantity, new_stock FROM stock_entries ORDER BY id"
    ).fetchall()
    assert entries == [(0, 10, 10), (10, 5, 15)]


def test_receive_goods_rejects_non_numeric_quantity(conn, monkeypatch):
    add_product(conn, monkeypatch, quantity="abc")

    assert get_stock(conn, "A1") is None
    assert conn.execute("SELECT COUNT(*) FROM stock_entries").fetchone()[0] == 0


def test_receive_goods_rejects_zero_quantity(conn, monkeypatch):
    add_product(conn, monkeypatch, quantity="0")

    assert get_stock(conn, "A1") is None


def test_receive_goods_rejects_negative_price(conn, monkeypatch):
    add_product(conn, monkeypatch, price="-3")

    assert get_stock(conn, "A1") is None


def test_receive_goods_requires_code_and_name(conn, monkeypatch):
    add_product(conn, monkeypatch, code="", name="")

    assert conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0


def test_register_sale_reduces_stock_and_saves_sale(conn, monkeypatch):
    add_product(conn, monkeypatch, quantity="10", price="9")

    # code, quantity, finish, confirm
    fake_inputs(monkeypatch, ["A1", "4", "", "y"])
    inventory.register_sale(conn)

    assert get_stock(conn, "A1") == 6
    sale = conn.execute("SELECT total FROM sales").fetchone()
    assert sale[0] == pytest.approx(36.0)
    item = conn.execute(
        "SELECT code, quantity, unit_price, subtotal FROM sale_items"
    ).fetchone()
    assert item == ("A1", 4, 9.0, 36.0)


def test_register_sale_with_several_products(conn, monkeypatch):
    add_product(conn, monkeypatch, code="A1", name="Yerba", quantity="10", price="9")
    add_product(conn, monkeypatch, code="B2", name="Sugar", quantity="20", price="2")

    fake_inputs(monkeypatch, ["A1", "2", "B2", "5", "", "y"])
    inventory.register_sale(conn)

    assert get_stock(conn, "A1") == 8
    assert get_stock(conn, "B2") == 15
    assert conn.execute("SELECT total FROM sales").fetchone()[0] == pytest.approx(28.0)
    assert conn.execute("SELECT COUNT(*) FROM sale_items").fetchone()[0] == 2


def test_register_sale_rejects_quantity_above_stock(conn, monkeypatch):
    add_product(conn, monkeypatch, quantity="3")

    fake_inputs(monkeypatch, ["A1", "10", "", ""])
    inventory.register_sale(conn)

    assert get_stock(conn, "A1") == 3
    assert conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 0


def test_register_sale_counts_cart_when_checking_stock(conn, monkeypatch):
    add_product(conn, monkeypatch, quantity="5")

    # 3 + 3 is more than the 5 available, so the second line must be rejected
    fake_inputs(monkeypatch, ["A1", "3", "A1", "3", "", "y"])
    inventory.register_sale(conn)

    assert get_stock(conn, "A1") == 2


def test_register_sale_unknown_code_is_ignored(conn, monkeypatch):
    fake_inputs(monkeypatch, ["ZZ", ""])
    inventory.register_sale(conn)

    assert conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 0


def test_register_sale_cancelled_does_not_change_anything(conn, monkeypatch):
    add_product(conn, monkeypatch, quantity="10")

    fake_inputs(monkeypatch, ["A1", "4", "", "n"])
    inventory.register_sale(conn)

    assert get_stock(conn, "A1") == 10
    assert conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 0


# ---------- view_products ----------

def test_view_products_empty(conn, capsys):
    inventory.view_products(conn)

    assert "No products registered." in capsys.readouterr().out


def test_view_products_lists_products(conn, monkeypatch, capsys):
    add_product(conn, monkeypatch, name="Yerba", quantity="10")
    capsys.readouterr()  # clear output from receive_goods

    inventory.view_products(conn)

    output = capsys.readouterr().out
    assert "Yerba" in output
    assert "A1" in output

pytest.main(["-v", "--tb=line", "-rN", __file__])

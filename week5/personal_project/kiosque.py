import sqlite3

# Kiosque App
# Kiosque is the spanish name for a small store that sells snacks, drinks, and other small items. This is a simple inventory management system for a kiosque.
# I used most of my knowledge from the course creating functions and my SQL knowledge I acquired from watching a pildorasinformaticas youtube channel tutorial.

DB_NAME = "inventory.db"  # Change to ":memory:" to start from scratch on every run if you don't want the program to save the data in your computer!!! :)


def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            brand TEXT,
            category TEXT,
            stock INTEGER NOT NULL DEFAULT 0,
            cost REAL,
            price REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            brand TEXT,
            category TEXT,
            previous_stock INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            new_stock INTEGER NOT NULL,
            cost REAL,
            price REAL,
            FOREIGN KEY (code) REFERENCES products(code)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT DEFAULT CURRENT_TIMESTAMP,
            total REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales(id),
            FOREIGN KEY (code) REFERENCES products(code)
        )
    """)

    conn.commit()


def receive_goods(conn):
    cursor = conn.cursor()

    code = input("Product code: ").strip()
    name = input("Name: ").strip()
    brand = input("Brand: ").strip()
    category = input("Category: ").strip()

    if not code or not name:
        print("Code and name are required.")
        return

    try:
        quantity = int(input("Quantity received: "))
        cost = float(input("Cost: "))
        price = float(input("Price: "))
    except ValueError:
        print("Quantity, cost and price must be numbers.")
        return

    if quantity <= 0:
        print("Quantity must be greater than 0.")
        return
    if cost < 0 or price < 0:
        print("Cost and price cannot be negative.")
        return

    # Previous stock (0 if the product does not exist yet)
    cursor.execute("SELECT stock FROM products WHERE code = ?", (code,))
    row = cursor.fetchone()
    previous_stock = row[0] if row else 0
    new_stock = previous_stock + quantity

    # Product first (because of the foreign key)
    if row:
        cursor.execute(
            "UPDATE products SET name = ?, brand = ?, category = ?, "
            "stock = ?, cost = ?, price = ? WHERE code = ?",
            (name, brand, category, new_stock, cost, price, code),
        )
    else:
        cursor.execute(
            "INSERT INTO products (code, name, brand, category, stock, cost, price) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (code, name, brand, category, new_stock, cost, price),
        )

    # Then the stock entry record
    cursor.execute(
        "INSERT INTO stock_entries (code, name, brand, category, previous_stock, "
        "quantity, new_stock, cost, price) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (code, name, brand, category, previous_stock, quantity, new_stock, cost, price),
    )

    conn.commit()
    print(f"Stock entry saved. Stock of {name}: {previous_stock} -> {new_stock}")


def register_sale(conn):
    cursor = conn.cursor()
    cart = []  # list of (code, name, quantity, price, subtotal)

    while True:
        code = input("Product code (press Enter to finish): ").strip()
        if code == "":
            break

        cursor.execute(
            "SELECT name, stock, price FROM products WHERE code = ?", (code,)
        )
        row = cursor.fetchone()
        if row is None:
            print("That code does not exist.")
            continue

        name, stock, price = row
        price = price or 0

        # Stock already reserved in the cart for this code
        in_cart = sum(item[2] for item in cart if item[0] == code)
        available = stock - in_cart

        try:
            quantity = int(input(f"{name} (available: {available}) - Quantity: "))
        except ValueError:
            print("Quantity must be a whole number.")
            continue

        if quantity <= 0:
            print("Quantity must be greater than 0.")
            continue
        if quantity > available:
            print("Not enough stock.")
            continue

        subtotal = quantity * price
        cart.append((code, name, quantity, price, subtotal))
        print(f"Added: {quantity} x {name} = ${subtotal:.2f}")

    if not cart:
        print("Empty sale, nothing was recorded.")
        return

    total = sum(item[4] for item in cart)
    print(f"\nTOTAL: ${total:.2f}")
    if input("Confirm sale? (y/n): ").strip().lower() != "y":
        print("Sale cancelled.")
        return

    cursor.execute("INSERT INTO sales (total) VALUES (?)", (total,))
    sale_id = cursor.lastrowid

    for code, name, quantity, price, subtotal in cart:
        cursor.execute(
            "INSERT INTO sale_items (sale_id, code, name, quantity, "
            "unit_price, subtotal) VALUES (?, ?, ?, ?, ?, ?)",
            (sale_id, code, name, quantity, price, subtotal),
        )
        cursor.execute(
            "UPDATE products SET stock = stock - ? WHERE code = ?",
            (quantity, code),
        )

    conn.commit()
    print(f"Sale #{sale_id} recorded.")


def view_products(conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT code, name, brand, category, stock, cost, price "
        "FROM products ORDER BY name"
    )
    rows = cursor.fetchall()

    if not rows:
        print("No products registered.")
        return

    print(f"\n{'Code':<10}{'Name':<20}{'Brand':<15}{'Category':<15}{'Stock':>6}{'Cost':>10}{'Price':>10}")
    print("-" * 86)
    for code, name, brand, category, stock, cost, price in rows:
        print(f"{code:<10}{name:<20}{brand or '':<15}{category or '':<15}{stock:>6}{cost or 0:>10.2f}{price or 0:>10.2f}")


def main():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    create_tables(conn)

    while True:
        print("\n===== INVENTORY SYSTEM =====")
        print("1. View products")
        print("2. Receive goods")
        print("3. Sell")
        print("4. Exit")

        option = input("Choose an option: ").strip()

        if option == "1":
            view_products(conn)
        elif option == "2":
            receive_goods(conn)
        elif option == "3":
            register_sale(conn)
        elif option == "4":
            print("Goodbye.")
            break
        else:
            print("Invalid option.")

    conn.close()


if __name__ == "__main__":
    main()
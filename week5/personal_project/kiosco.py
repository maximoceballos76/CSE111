import sqlite3

DB_NAME = "inventario.db"  # Cambiá a ":memory:" si querés empezar de cero en cada ejecución


def crear_tablas(conn):
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articulos (
            codigo TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            marca TEXT,
            rubro TEXT,
            stock INTEGER NOT NULL DEFAULT 0,
            costo REAL,
            precio REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL,
            nombre TEXT NOT NULL,
            marca TEXT,
            rubro TEXT,
            stock_anterior INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            stock_actual INTEGER NOT NULL,
            costo REAL,
            precio REAL,
            FOREIGN KEY (codigo) REFERENCES articulos(codigo)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT DEFAULT CURRENT_TIMESTAMP,
            total REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            codigo TEXT NOT NULL,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas(id),
            FOREIGN KEY (codigo) REFERENCES articulos(codigo)
        )
    """)

    conn.commit()


def ingresar_mercaderia(conn):
    cursor = conn.cursor()

    codigo = input("Código del artículo: ").strip()
    nombre = input("Nombre: ").strip()
    marca = input("Marca: ").strip()
    rubro = input("Rubro: ").strip()

    if not codigo or not nombre:
        print("El código y el nombre son obligatorios.")
        return

    try:
        cantidad = int(input("Cantidad ingresada: "))
        costo = float(input("Costo: "))
        precio = float(input("Precio: "))
    except ValueError:
        print("Cantidad, costo y precio deben ser números.")
        return

    if cantidad <= 0:
        print("La cantidad debe ser mayor a 0.")
        return
    if costo < 0 or precio < 0:
        print("El costo y el precio no pueden ser negativos.")
        return

    # Stock anterior (0 si el artículo no existe)
    cursor.execute("SELECT stock FROM articulos WHERE codigo = ?", (codigo,))
    fila = cursor.fetchone()
    stock_anterior = fila[0] if fila else 0
    stock_actual = stock_anterior + cantidad

    # Primero el artículo (por la clave foránea)
    if fila:
        cursor.execute(
            "UPDATE articulos SET nombre = ?, marca = ?, rubro = ?, "
            "stock = ?, costo = ?, precio = ? WHERE codigo = ?",
            (nombre, marca, rubro, stock_actual, costo, precio, codigo),
        )
    else:
        cursor.execute(
            "INSERT INTO articulos (codigo, nombre, marca, rubro, stock, costo, precio) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (codigo, nombre, marca, rubro, stock_actual, costo, precio),
        )

    # Después el registro del ingreso
    cursor.execute(
        "INSERT INTO ingresos (codigo, nombre, marca, rubro, stock_anterior, "
        "cantidad, stock_actual, costo, precio) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (codigo, nombre, marca, rubro, stock_anterior, cantidad, stock_actual, costo, precio),
    )

    conn.commit()
    print(f"Ingreso registrado. Stock de {nombre}: {stock_anterior} -> {stock_actual}")


def registrar_venta(conn):
    cursor = conn.cursor()
    carrito = []  # lista de (codigo, nombre, cantidad, precio, subtotal)

    while True:
        codigo = input("Código del producto (Enter para terminar): ").strip()
        if codigo == "":
            break

        cursor.execute(
            "SELECT nombre, stock, precio FROM articulos WHERE codigo = ?", (codigo,)
        )
        fila = cursor.fetchone()
        if fila is None:
            print("Ese código no existe.")
            continue

        nombre, stock, precio = fila
        precio = precio or 0

        # Stock ya reservado en el carrito para este código
        en_carrito = sum(item[2] for item in carrito if item[0] == codigo)
        disponible = stock - en_carrito

        try:
            cantidad = int(input(f"{nombre} (disponible: {disponible}) - Cantidad: "))
        except ValueError:
            print("La cantidad debe ser un número entero.")
            continue

        if cantidad <= 0:
            print("La cantidad debe ser mayor a 0.")
            continue
        if cantidad > disponible:
            print("No hay stock suficiente.")
            continue

        subtotal = cantidad * precio
        carrito.append((codigo, nombre, cantidad, precio, subtotal))
        print(f"Agregado: {cantidad} x {nombre} = ${subtotal:.2f}")

    if not carrito:
        print("Venta vacía, no se registró nada.")
        return

    total = sum(item[4] for item in carrito)
    print(f"\nTOTAL: ${total:.2f}")
    if input("¿Confirmar venta? (s/n): ").strip().lower() != "s":
        print("Venta cancelada.")
        return

    cursor.execute("INSERT INTO ventas (total) VALUES (?)", (total,))
    venta_id = cursor.lastrowid

    for codigo, nombre, cantidad, precio, subtotal in carrito:
        cursor.execute(
            "INSERT INTO detalle_ventas (venta_id, codigo, nombre, cantidad, "
            "precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?, ?)",
            (venta_id, codigo, nombre, cantidad, precio, subtotal),
        )
        cursor.execute(
            "UPDATE articulos SET stock = stock - ? WHERE codigo = ?",
            (cantidad, codigo),
        )

    conn.commit()
    print(f"Venta #{venta_id} registrada.")


def ver_articulos(conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT codigo, nombre, marca, rubro, stock, costo, precio "
        "FROM articulos ORDER BY nombre"
    )
    filas = cursor.fetchall()

    if not filas:
        print("No hay artículos cargados.")
        return

    print(f"\n{'Código':<10}{'Nombre':<20}{'Marca':<15}{'Rubro':<15}{'Stock':>6}{'Costo':>10}{'Precio':>10}")
    print("-" * 86)
    for codigo, nombre, marca, rubro, stock, costo, precio in filas:
        print(f"{codigo:<10}{nombre:<20}{marca or '':<15}{rubro or '':<15}{stock:>6}{costo or 0:>10.2f}{precio or 0:>10.2f}")


def main():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    crear_tablas(conn)

    while True:
        print("\n===== SISTEMA DE INVENTARIO =====")
        print("1. Ver artículos")
        print("2. Ingresar mercadería")
        print("3. Vender")
        print("4. Salir")

        opcion = input("Elegí una opción: ").strip()

        if opcion == "1":
            ver_articulos(conn)
        elif opcion == "2":
            ingresar_mercaderia(conn)
        elif opcion == "3":
            registrar_venta(conn)
        elif opcion == "4":
            print("Hasta luego.")
            break
        else:
            print("Opción inválida.")

    conn.close()


if __name__ == "__main__":
    main()
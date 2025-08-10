import sqlite3

conn = sqlite3.connect('mydatabase.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        price REAL NOT NULL
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        product_id INTEGER,
        quantity INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
''')

customers_data = [
    ("Benny", "Ryan", "Benny_Ryan@gmail.com"),
    ("Bob", "Ross", "Bob_Ross@gmail.com"),
    ("Job", "Man", "Job_Man@gmail.com"),
]

product_data = [
    ('Lamp', 15.0),
    ('Mouse', 20.0),
    ('Pencil', 1.0),
    ('Eraser', 3.0),
    ('Desk', 150.0),
]

c.executemany("INSERT OR IGNORE INTO users (first_name, last_name, email) VALUES (?, ?, ?)", customers_data)
c.executemany("INSERT OR IGNORE INTO products (name, price) VALUES (?, ?)", product_data)

c.execute("INSERT OR IGNORE INTO orders (user_id, product_id, quantity) VALUES (?,?,?)", (1, 1, 1))
c.execute("INSERT OR IGNORE INTO orders (user_id, product_id, quantity) VALUES (?,?,?)", (2, 3, 5))
c.execute("INSERT OR IGNORE INTO orders (user_id, product_id, quantity) VALUES (?,?,?)", (3, 5, 1))

conn.commit()

print("--- ALL Users ---")
c.execute('SELECT * FROM users')
all_users = c.fetchall()
for user in all_users:
    print(user)

print("\n--- ALL Orders ---")
c.execute("SELECT orders.id, users.first_name, products.name, orders.quantity FROM orders JOIN users ON orders.user_id = users.id JOIN products ON orders.product_id = products.id")
all_orders = c.fetchall()
for order in all_orders:
    print(order)

conn.close()

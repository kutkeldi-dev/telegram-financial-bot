import sqlite3
import sys

# Устанавливаем encoding для stdout
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('./data/bot.db')
cursor = conn.cursor()

print("=== CHECKING EXPENSES WITH CATEGORIES ===")

# Проверяем последние расходы с категориями
cursor.execute('''
    SELECT e.id, e.amount, e.purpose, e.category_id, ec.name 
    FROM expenses e 
    LEFT JOIN expense_categories ec ON e.category_id = ec.id 
    ORDER BY e.id DESC LIMIT 5
''')

results = cursor.fetchall()
if results:
    print("Latest 5 expenses:")
    for row in results:
        print(f"ID: {row[0]}, Amount: {row[1]}, Category ID: {row[3]}, Category: {row[4]}")
else:
    print("No expenses found")

print("\n=== AVAILABLE CATEGORIES ===")
cursor.execute('SELECT id, name FROM expense_categories')
categories = cursor.fetchall()
for cat in categories:
    print(f"ID: {cat[0]}, Name: {cat[1]}")

conn.close()
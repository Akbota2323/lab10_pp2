import psycopg2
import csv

conn = psycopg2.connect(
    dbname="neondb",
    user="neondb_owner",
    password="npg_9gG3aHQSZfFA",
    host="ep-delicate-bread-a4vahd6w-pooler.us-east-1.aws.neon.tech",
    port="5432",
    sslmode="require"
)
cur = conn.cursor()

# 1. Создание таблицы
def create_table():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            phone VARCHAR(20)
        );
    """)
    conn.commit()

# 2. Добавление вручную
def add_entry():
    name = input("Введите имя: ")
    phone = input("Введите номер телефона: ")
    cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (name, phone))
    conn.commit()
    print(" Добавлено!")

# 3. Загрузка из CSV
def load_from_csv(filename='pp.csv'):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (row[0], row[1]))
    conn.commit()
    print(" Данные из CSV загружены!")

# 4. Обновление данных
def update_entry():
    name = input("Введите имя для обновления: ")
    new_phone = input("Новый номер: ")
    cur.execute("UPDATE phonebook SET phone = %s WHERE name = %s", (new_phone, name))
    conn.commit()
    print(" Обновлено!")

# 5. Поиск по фильтру
def search():
    keyword = input("Введите имя или номер для поиска: ")
    cur.execute("SELECT * FROM phonebook WHERE name ILIKE %s OR phone LIKE %s", (f'%{keyword}%', f'%{keyword}%'))
    results = cur.fetchall()
    for row in results:
        print(row)

# 6. Удаление
def delete_entry():
    keyword = input("Введите имя или номер для удаления: ")
    cur.execute("DELETE FROM phonebook WHERE name ILIKE %s OR phone LIKE %s", (f'%{keyword}%', f'%{keyword}%'))
    conn.commit()
    print("🗑 Удалено!")

# Меню
def main():
    create_table()
    while True:
        print("\n--- Телефонная книга ---")
        print("1. Добавить контакт вручную")
        print("2. Загрузить из CSV")
        print("3. Обновить номер")
        print("4. Поиск")
        print("5. Удалить")
        print("0. Выход")
        choice = input("Выберите действие: ")

        if choice == "1":
            add_entry()
        elif choice == "2":
            load_from_csv()
        elif choice == "3":
            update_entry()
        elif choice == "4":
            search()
        elif choice == "5":
            delete_entry()
        elif choice == "0":
            break
        else:
            print(" Неверный выбор!")

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()

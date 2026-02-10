import sqlite3

conn = sqlite3.connect("games.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    genre TEXT,
    year INTEGER
)
""")
conn.commit()

def add_game():
    title = input("Название игры: ")
    genre = input("Жанр: ")
    year = input("Год: ")

    cursor.execute(
        "INSERT INTO games (title, genre, year) VALUES (?, ?, ?)",
        (title, genre, year)
    )
    conn.commit()
    print("Игра добавлена!")

def show_games():
    cursor.execute("SELECT * FROM games")
    games = cursor.fetchall()

    print("\nСписок игр:")
    for game in games:
        print(game)

def search_game():
    name = input("Введите название для поиска: ")

    cursor.execute(
        "SELECT * FROM games WHERE title LIKE ?",
        ("%" + name + "%",)
    )

    results = cursor.fetchall()

    if results:
        print("\nНайдено:")
        for game in results:
            print(game)
    else:
        print("Игра не найдена.")

def delete_game():
    game_id = input("Введите ID игры для удаления: ")

    cursor.execute(
        "DELETE FROM games WHERE id = ?",
        (game_id,)
    )
    conn.commit()

    print("Игра удалена (если ID существовал).")

def update_game():
    game_id = input("Введите ID игры для изменения: ")

    new_title = input("Новое название: ")
    new_genre = input("Новый жанр: ")
    new_year = input("Новый год: ")

    cursor.execute(
        """
        UPDATE games
        SET title = ?, genre = ?, year = ?
        WHERE id = ?
        """,
        (new_title, new_genre, new_year, game_id)
    )
    conn.commit()

    print("Игра обновлена.")

def menu():
    while True:
        print("\n--- МЕНЮ ---")
        print("1. Добавить игру")
        print("2. Показать все игры")
        print("3. Найти игру")
        print("4. Удалить игру")
        print("5. Изменить игру")
        print("0. Выход")

        choice = input("Выбор: ")

        if choice == "1":
            add_game()
        elif choice == "2":
            show_games()
        elif choice == "3":
            search_game()
        elif choice == "4":
            delete_game()
        elif choice == "5":
            update_game()
        elif choice == "0":
            break
        else:
            print("Неверный выбор.")


menu()

conn.close()

import pygame
import time
import random
import psycopg2

# Подключение к базе данных
conn = psycopg2.connect(
    dbname="neondb",
    user="neondb_owner",
    password="npg_JZb8Lvet1RVB",
    host="ep-damp-wave-a4h3sjnf-pooler.us-east-1.aws.neon.tech",
    port="5432",
    sslmode="require"
)
cur = conn.cursor()

# Создание таблиц (если ещё нет)
def create_tables():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_score (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            score INTEGER,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()

# Получение или создание пользователя
def get_or_create_user():
    username = input(" Введите имя пользователя: ")
    cur.execute("SELECT id FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    if user:
        print(" Добро пожаловать обратно!")
        return user[0]
    else:
        cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING id", (username,))
        conn.commit()
        print("Новый пользователь создан.")
        return cur.fetchone()[0]

# Сохранение результата в базу
def save_score(user_id, score):
    print(f" Сохраняем результат в БД: {score}")
    cur.execute("INSERT INTO user_score (user_id, score) VALUES (%s, %s)", (user_id, score))
    conn.commit()
    print(" Результат сохранён в базу данных.")

# Инициализация Pygame
pygame.init()
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
background_color = (204, 51, 255)

dis_width = 800
dis_height = 600
dis = pygame.display.set_mode((dis_width, dis_height))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
snake_block = 10
snake_speed = 15
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)

def Your_score(score):
    value = score_font.render("Score: " + str(score), True, black)
    dis.blit(value, [0, 0])

def our_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(dis, black, [x[0], x[1], snake_block, snake_block])

def message(msg, color):
    mesg = font_style.render(msg, True, color)
    dis.blit(mesg, [dis_width / 6, dis_height / 3])

# Главный цикл игры
def gameLoop(user_id):
    game_over = False
    game_close = False

    x1 = dis_width / 2
    y1 = dis_height / 2

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1

    foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
    foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0

    while not game_over:
        while game_close:
            dis.fill(background_color)
            message("You lost! Press Q to Quit or C to Play Again", white)
            Your_score(Length_of_snake - 1)
            pygame.display.update()

            # сохраняем в БД при проигрыше
            save_score(user_id, Length_of_snake - 1)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    elif event.key == pygame.K_c:
                        gameLoop(user_id)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_score(user_id, Length_of_snake - 1)  # сохраняем при выходе
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0

        if x1 >= dis_width or x1 < 0 or y1 >= dis_height or y1 < 0:
            game_close = True

        x1 += x1_change
        y1 += y1_change
        dis.fill(background_color)
        pygame.draw.rect(dis, green, [foodx, foody, snake_block, snake_block])
        snake_Head = [x1, y1]
        snake_List.append(snake_Head)

        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        our_snake(snake_block, snake_List)
        Your_score(Length_of_snake - 1)

        pygame.display.update()

        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
            foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0
            Length_of_snake += 1

        clock.tick(snake_speed)

    pygame.quit()
    quit()

# Запуск
if __name__ == "__main__":
    create_tables()
    user_id = get_or_create_user()
    gameLoop(user_id)

    # Закрываем соединение
    cur.close()
    conn.close()

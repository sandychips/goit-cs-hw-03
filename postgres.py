
import psycopg2
from faker import Faker

# Підключення до бази даних
conn = psycopg2.connect(
    dbname="your_dbname",
    user="your_username",
    password="your_password",
    host="your_host",
    port="your_port"
)

cur = conn.cursor()

# Створення таблиць
create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);
"""

create_status_table = """
CREATE TABLE IF NOT EXISTS status (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);
"""

create_tasks_table = """
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    status_id INTEGER REFERENCES status(id),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);
"""

cur.execute(create_users_table)
cur.execute(create_status_table)
cur.execute(create_tasks_table)

conn.commit()

# Заповнення таблиць випадковими даними
fake = Faker()

# Додавання статусів
statuses = ['new', 'in progress', 'completed']
for status in statuses:
    cur.execute("INSERT INTO status (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (status,))

# Додавання користувачів та завдань
for _ in range(10):
    fullname = fake.name()
    email = fake.email()
    cur.execute("INSERT INTO users (fullname, email) VALUES (%s, %s) RETURNING id", (fullname, email))
    user_id = cur.fetchone()[0]
    
    for _ in range(5):
        title = fake.sentence()
        description = fake.text()
        status_id = fake.random_int(min=1, max=3)
        cur.execute("INSERT INTO tasks (title, description, status_id, user_id) VALUES (%s, %s, %s, %s)",
                    (title, description, status_id, user_id))

conn.commit()

# Виконання запитів

# Отримати всі завдання певного користувача
def get_tasks_by_user(user_id):
    cur.execute("SELECT * FROM tasks WHERE user_id = %s", (user_id,))
    return cur.fetchall()

# Вибрати завдання за певним статусом
def get_tasks_by_status(status_name):
    cur.execute("SELECT * FROM tasks WHERE status_id = (SELECT id FROM status WHERE name = %s)", (status_name,))
    return cur.fetchall()

# Оновити статус конкретного завдання
def update_task_status(task_id, new_status):
    cur.execute("UPDATE tasks SET status_id = (SELECT id FROM status WHERE name = %s) WHERE id = %s", (new_status, task_id))
    conn.commit()

# Отримати список користувачів, які не мають жодного завдання
def get_users_with_no_tasks():
    cur.execute("SELECT * FROM users WHERE id NOT IN (SELECT user_id FROM tasks)")
    return cur.fetchall()

# Додати нове завдання для конкретного користувача
def add_task_for_user(user_id, title, description, status_name):
    cur.execute("INSERT INTO tasks (title, description, status_id, user_id) VALUES (%s, %s, (SELECT id FROM status WHERE name = %s), %s)",
                (title, description, status_name, user_id))
    conn.commit()

# Отримати всі завдання, які ще не завершено
def get_incomplete_tasks():
    cur.execute("SELECT * FROM tasks WHERE status_id != (SELECT id FROM status WHERE name = 'completed')")
    return cur.fetchall()

# Видалити конкретне завдання
def delete_task(task_id):
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()

# Знайти користувачів з певною електронною поштою
def find_users_by_email(email_pattern):
    cur.execute("SELECT * FROM users WHERE email LIKE %s", (email_pattern,))
    return cur.fetchall()

# Оновити ім'я користувача
def update_user_name(user_id, new_name):
    cur.execute("UPDATE users SET fullname = %s WHERE id = %s", (new_name, user_id))
    conn.commit()

# Отримати кількість завдань для кожного статусу
def get_task_count_by_status():
    cur.execute("SELECT status_id, COUNT(*) FROM tasks GROUP BY status_id")
    return cur.fetchall()

# Отримати завдання, які призначені користувачам з певною доменною частиною електронної пошти
def get_tasks_by_email_domain(email_domain):
    cur.execute("SELECT tasks.* FROM tasks JOIN users ON tasks.user_id = users.id WHERE users.email LIKE %s", (email_domain,))
    return cur.fetchall()

# Отримати список завдань, що не мають опису
def get_tasks_without_description():
    cur.execute("SELECT * FROM tasks WHERE description IS NULL")
    return cur.fetchall()

# Вибрати користувачів та їхні завдання, які є у статусі 'in progress'
def get_users_and_tasks_in_progress():
    cur.execute("SELECT users.*, tasks.* FROM users JOIN tasks ON users.id = tasks.user_id WHERE tasks.status_id = (SELECT id FROM status WHERE name = 'in progress')")
    return cur.fetchall()

# Отримати користувачів та кількість їхніх завдань
def get_users_and_task_counts():
    cur.execute("SELECT users.id, users.fullname, COUNT(tasks.id) FROM users LEFT JOIN tasks ON users.id = tasks.user_id GROUP BY users.id")
    return cur.fetchall()

cur.close()
conn.close()

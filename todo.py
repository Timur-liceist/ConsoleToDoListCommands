import json
import sys
from datetime import datetime, timedelta

# Файл для хранения задач
TODO_FILE = "todo.json"

# Преобразует строку в формат даты YYYY-MM-DD
def parse_date(date_str):
    date_str = date_str.strip().lower()
    if date_str == "today":
        return datetime.now().strftime("%Y-%m-%d")
    elif date_str == "tomorrow":
        return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        # Проверим, что это валидная дата
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            raise ValueError(f"❌ Неверный формат даты: '{date_str}'. Используйте ГГГГ-ММ-ДД, 'today' или 'tomorrow'.")

# Загрузка задач из файла
def load_tasks():
    try:
        with open(TODO_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Сохранение задач в файл
def save_tasks(tasks):
    with open(TODO_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

# Добавление новой задачи
def add_task(description, due_date_str=None):
    tasks = load_tasks()

    due_date = None
    if due_date_str:
        try:
            due_date = parse_date(due_date_str)
        except ValueError as e:
            print(e)
            return

    task = {
        "id": len(tasks) + 1,
        "description": description,
        "due_date": due_date,
        "completed": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"✅ Задача добавлена (ID: {task['id']}): {description} | Срок: {due_date or 'не указан'}")

# Просмотр всех задач
def list_tasks():
    tasks = load_tasks()
    if not tasks:
        print("📭 Список задач пуст.")
        return

    print("\n📋 Список задач:")
    print("-" * 80)
    for task in tasks:
        status = "✔️" if task["completed"] else "⭕"
        due = task["due_date"] or "—"
        created = task["created_at"]
        print(f"[{status}] ID:{task['id']} | {task['description']}")
        print(f"      Срок: {due} | Создана: {created}")
        print()
    print("-" * 80)

# Отметить задачу как выполненную
def complete_task(task_id):
    tasks = load_tasks()
    found = False
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            found = True
            break
    if found:
        save_tasks(tasks)
        print(f"🎉 Задача ID:{task_id} отмечена как выполненная.")
    else:
        print(f"❌ Задача с ID:{task_id} не найдена.")

# Удаление задачи
def delete_task(task_id):
    tasks = load_tasks()
    tasks_before = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]
    if len(tasks) < tasks_before:
        save_tasks(tasks)
        print(f"🗑️ Задача ID:{task_id} удалена.")
    else:
        print(f"❌ Задача с ID:{task_id} не найдена.")

# Фильтрация задач по дате (внутренняя)
def filter_tasks_by_date(target_date_str):
    tasks = load_tasks()
    filtered = []
    try:
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
    except ValueError:
        return []

    for task in tasks:
        if not task["due_date"] or task["completed"]:
            continue
        try:
            task_date = datetime.strptime(task["due_date"], "%Y-%m-%d")
            if task_date.date() == target_date.date():
                filtered.append(task)
        except ValueError:
            continue
    return filtered

# Показать задачи на сегодня
def show_today():
    today_str = datetime.now().strftime("%Y-%m-%d")
    tasks = filter_tasks_by_date(today_str)
    if not tasks:
        print("📭 На сегодня нет активных задач.")
        return
    print(f"\n📅 Задачи на сегодня ({today_str}):")
    print("-" * 60)
    for task in tasks:
        print(f"🔹 ID:{task['id']} | {task['description']}")
    print("-" * 60)

# Показать задачи на завтра
def show_tomorrow():
    tomorrow_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    tasks = filter_tasks_by_date(tomorrow_str)
    if not tasks:
        print("📭 На завтра нет активных задач.")
        return
    print(f"\n📅 Задачи на завтра ({tomorrow_str}):")
    print("-" * 60)
    for task in tasks:
        print(f"🔹 ID:{task['id']} | {task['description']}")
    print("-" * 60)

# Перенос задач на указанное количество минут
def reschedule_tasks(date_key, minutes):
    try:
        minutes = int(minutes)
    except ValueError:
        print("❌ Количество минут должно быть числом.")
        return

    # Преобразуем ключ (today/tomorrow/дата) в строку YYYY-MM-DD
    try:
        target_date = parse_date(date_key)
    except ValueError as e:
        print(e)
        return

    tasks = load_tasks()
    updated_count = 0

    for task in tasks:
        if not task["due_date"] or task["completed"]:
            continue
        if task["due_date"] == target_date:
            try:
                dt = datetime.strptime(task["due_date"], "%Y-%m-%d")
                new_dt = dt + timedelta(minutes=minutes)
                task["due_date"] = new_dt.strftime("%Y-%m-%d")
                updated_count += 1
            except ValueError:
                continue

    if updated_count > 0:
        save_tasks(tasks)
        action = "вперёд" if minutes > 0 else "назад"
        print(f"🔄 Перенесено {updated_count} задач(и) с даты {target_date} на {abs(minutes)} мин. {action}.")
    else:
        print(f"❌ Нет активных задач на дату {target_date} для переноса.")

# Помощь / справка
def show_help():
    help_text = """

📌 To-Do List — Команды:

todo.py add "Описание" ["YYYY-MM-DD"|"today"|"tomorrow"]
    Добавить задачу. Дата необязательна.

todo.py list
    Все задачи.

todo.py today
    Задачи на сегодня.

todo.py tomorrow
    Задачи на завтра.

todo.py complete <ID>
    Отметить как выполненную.

todo.py delete <ID>
    Удалить задачу.

todo.py reschedule <date|today|tomorrow> <минуты>
    Перенести задачи на указанное кол-во минут вперёд/назад.
    Пример: todo.py reschedule today 60
            todo.py reschedule tomorrow -30

todo.py help
    Показать справку.

📌 To-Do List — Команды (полные и сокращения):

add "Описание" ["дата"]   | a "..." ["..."]     — Добавить задачу
list                     | l                   — Все задачи
today                    | td                  — Задачи на сегодня
tomorrow                 | tm                  — Задачи на завтра
complete <ID>            | c <ID>              — Отметить как выполненную
delete <ID>              | d <ID>              — Удалить задачу
reschedule <дата> <мин>  | r <дата> <мин>      — Перенести задачи на минуты
help                     | h                   — Показать справку

📌 Поддерживаемые форматы дат: ГГГГ-ММ-ДД, 'today', 'tomorrow' (и их сокращения)
Пример: python todo.py a "Позвонить" tomorrow
        python todo.py r td 30
    """
    print(help_text)

# Словарь сокращений
ALIASES = {
    'a': 'add',
    'l': 'list',
    'td': 'today',
    'tm': 'tomorrow',
    'c': 'complete',
    'd': 'delete',
    'r': 'reschedule',
    'h': 'help'
}

# Основная логика
def main():
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()
    # Заменяем сокращение на полную команду
    full_command = ALIASES.get(command, command)

    if full_command == "add":
        if len(sys.argv) < 3:
            print("❌ Укажите описание задачи.")
            return
        description = sys.argv[2]
        due_date_str = sys.argv[3] if len(sys.argv) > 3 else None
        add_task(description, due_date_str)

    elif full_command == "list":
        list_tasks()

    elif full_command == "today":
        show_today()

    elif full_command == "tomorrow":
        show_tomorrow()

    elif full_command == "complete":
        if len(sys.argv) < 3:
            print("❌ Укажите ID задачи.")
            return
        try:
            task_id = int(sys.argv[2])
            complete_task(task_id)
        except ValueError:
            print("❌ ID должен быть числом.")

    elif full_command == "delete":
        if len(sys.argv) < 3:
            print("❌ Укажите ID задачи.")
            return
        try:
            task_id = int(sys.argv[2])
            delete_task(task_id)
        except ValueError:
            print("❌ ID должен быть числом.")

    elif full_command == "reschedule":
        if len(sys.argv) != 4:
            print("❌ Использование: reschedule <дата> <минуты>")
            return
        date_key = sys.argv[2]
        minutes = sys.argv[3]
        reschedule_tasks(date_key, minutes)

    elif full_command == "help":
        show_help()

    else:
        print("❌ Неизвестная команда. Используйте: todo.py help")

if __name__ == "__main__":
    main()

def agent_task(task):

    # 1. Планування
    plan = ask_ai([
        {"role": "system", "content": "Ти AI-агент. Створи план виконання задачі крок за кроком."},
        {"role": "user", "content": task}
    ])

    # 2. Витяг ключових запитів
    queries = ask_ai([
        {"role": "system", "content": "Виділи 3 пошукові запити для цієї задачі."},
        {"role": "user", "content": task}
    ]).split("\n")

    # 3. Пошук по кожному запиту
    all_results = []
    for q in queries[:3]:
        try:
            res = search_articles(q)
            all_results.extend(res)
        except:
            pass

    # 4. Аналіз
    analysis = ask_ai([
        {"role": "system", "content": "Проаналізуй інформацію і виділи головне."},
        {"role": "user", "content": str(all_results)}
    ])

    # 5. Фінальне рішення
    final = ask_ai([
        {"role": "system", "content": "Дай конкретні дії і як заробити гроші з цього."},
        {"role": "user", "content": f"""
Задача: {task}

План:
{plan}

Дані:
{analysis}
"""}
    ])

    return f"""
📌 ПЛАН:
{plan}

🔎 ПОШУК:
{queries}

📊 АНАЛІЗ:
{analysis}

💰 РІШЕННЯ:
{final}
"""

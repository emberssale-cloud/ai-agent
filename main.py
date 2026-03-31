import os
import requests
from telegram.ext import Updater, MessageHandler, Filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ---------- AI ----------
def ask_ai(messages):
    res = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "mistralai/mixtral-8x7b-instruct",  # 🔥 модель
            "messages": messages
        }
    )
    return res.json()['choices'][0]['message']['content']


# ---------- SEARCH ----------
def search_articles(query):
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    data = requests.get(url).json()

    results = []
    for topic in data.get("RelatedTopics", [])[:8]:
        if "Text" in topic:
            results.append(topic["Text"])

    return results


# ---------- AGENT ----------
def agent_task(task):

    # 1. План
    plan = ask_ai([
        {"role": "system", "content": "Ти AI-агент. Розбий задачу на чіткі кроки."},
        {"role": "user", "content": task}
    ])

    # 2. Пошук
    articles = search_articles(task)

    # 3. Аналіз кожного
    summaries = []
    for art in articles:
        summary = ask_ai([
            {"role": "system", "content": "Коротко проаналізуй текст (1-2 речення)."},
            {"role": "user", "content": art}
        ])
        summaries.append(f"- {summary}")

    # 4. Фінальний звіт
    final = ask_ai([
        {"role": "system", "content": "Ти бізнес-аналітик. Збери фінальний звіт."},
        {"role": "user", "content": f"""
Задача: {task}

План:
{plan}

Аналіз:
{summaries}

Зроби:
1. Висновки
2. Рекомендації
"""}
    ])

    return f"📌 ПЛАН:\n{plan}\n\n📊 АНАЛІЗ:\n" + "\n".join(summaries) + f"\n\n✅ ВИСНОВОК:\n{final}"


# ---------- TELEGRAM ----------
def handle(update, context):
    text = update.message.text
    reply = agent_task(text)
    update.message.reply_text(reply)


updater = Updater(TELEGRAM_TOKEN, use_context=True)
updater.dispatcher.add_handler(MessageHandler(Filters.text, handle))

print("Agent started...")
updater.start_polling()
updater.idle()

import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

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
            "model": "mistralai/mixtral-8x7b-instruct",
            "messages": messages
        }
    )
    return res.json()['choices'][0]['message']['content']


# ---------- SEARCH ----------
def search_articles(query):
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    data = requests.get(url).json()

    results = []
    for topic in data.get("RelatedTopics", [])[:5]:
        if "Text" in topic:
            results.append(topic["Text"])

    return results


# ---------- AGENT ----------
def agent_task(task):

    plan = ask_ai([
        {"role": "system", "content": "Розбий задачу на кроки."},
        {"role": "user", "content": task}
    ])

    articles = search_articles(task)

    summaries = []
    for art in articles:
        summary = ask_ai([
            {"role": "system", "content": "Коротко поясни (1 речення)."},
            {"role": "user", "content": art}
        ])
        summaries.append(f"- {summary}")

    final = ask_ai([
        {"role": "system", "content": "Зроби висновок і рекомендації."},
        {"role": "user", "content": f"{plan}\n{summaries}"}
    ])

    return f"📌 ПЛАН:\n{plan}\n\n📊 АНАЛІЗ:\n" + "\n".join(summaries) + f"\n\n✅ ВИСНОВОК:\n{final}"


# ---------- TELEGRAM ----------
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    reply = agent_task(text)
    await update.message.reply_text(reply)


app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, handle))

print("Agent started...")
app.run_polling()

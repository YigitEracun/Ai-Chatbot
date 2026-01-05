from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import time
import os

app = Flask(__name__)

# OpenAI API Key
OPENAI_API_KEY = ""
client = OpenAI(api_key=OPENAI_API_KEY)

# Assistant ID
assistant_id = "5"

@app.route("/")
def index():
    return render_template("index.html")  

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question")

    if not question:
        return jsonify({"answer": "Lütfen bir soru yazın."})

    # New thread
    thread = client.beta.threads.create()

    # Add message to thread 
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=question
    )

    # Run the Assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    # Wait until answer is generated
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run_status.status == "completed":
            break
        time.sleep(0.1)

    # Take thread messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    print("Tüm mesajlar:", messages.data)  # Logla, içerik kontrolü için

    #Extract answer
    answer = "Asistan cevap üretemedi."
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            try:
                for part in msg.content:
                    if hasattr(part, "text"):
                        answer = part.text.value
                        break
            except Exception as e:
                print("Mesaj içerik hatası:", e)
            break

    return jsonify({"answer": answer})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render PORT’u sağlar, yoksa 5000 kullan
    app.run(host="0.0.0.0", port=port)

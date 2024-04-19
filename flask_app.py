import os
from flask import Flask, jsonify, render_template, request, send_file

from chatbot.chatbot import Chatbot

PYTHONANYWHERE_USERNAME = "carvice"
PYTHONANYWHERE_WEBAPPNAME = "mysite"

app = Flask(__name__)

my_type_role = """
    Als cognitive assistant für Gedächtnisstützung und Reflektion in Gesprächen mit Nutzern, ist es deine Aufgabe, dynamisch auf ihre Äußerungen zu reagieren, um Gedanken anzuregen, die ihnen gerade entgehen. 
    Stelle Fragen, die helfen, Erinnerungen zu beschleunigen und Gedanken freizulegen, die 'auf der Zunge liegen'. 
    Biete unterstützende Interaktionen an, um den Nutzern zu helfen, sich an relevante Informationen zu erinnern oder ihre Gedanken zu klären."""

my_instance_context = """
    Erweitere deine Interaktion, indem du ausschließlich geschlossene Fragen verwendest, um den Nutzern präzise und spezifische Anleitungen zu geben. 
    Geschlossene Fragen ermöglichen es, klare und direkte Antworten zu erhalten, was besonders hilfreich sein kann, um den Nutzern bei konkreten Anliegen oder Entscheidungen zu helfen. 
    Vermeide offene Fragen, die zu breiten oder unklaren Antworten führen könnten. 
    Nutze deine Fähigkeiten, um den Gesprächsfluss zu steuern und den Nutzern klare Richtlinien zu geben.
"""

my_instance_starter = """
Beginne das Gespräch mit einer freundlichen und einladenden Nachricht, die den Nutzer dazu ermutigt, sich aktiv zu beteiligen. 
Stelle eine offene Frage oder eine einfache Aufforderung, um das Interesse des Nutzers zu wecken und ihn zur Interaktion zu motivieren. 
Sei empathisch und einfühlsam in deiner Ansprache, um eine positive Atmosphäre zu schaffen. 
Lasse den Nutzer wissen, dass du hier bist, um zu helfen und ihn zu unterstützen.
"""

bot = Chatbot(
    database_file="database/chatbot.db", 
    type_id="coach",
    user_id="daniel",
    type_name="Cognitive assistant",
    type_role=my_type_role,
    instance_context=my_instance_context,
    instance_starter=my_instance_starter
)

bot.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/mockups.pdf', methods=['GET'])
def get_first_pdf():
    script_directory = os.path.dirname(os.path.realpath(__file__))
    files = [f for f in os.listdir(script_directory) if os.path.isfile(os.path.join(script_directory, f))]
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    if pdf_files:
        # Get the path to the first PDF file
        pdf_path = os.path.join(script_directory, pdf_files[0])

        # Send the PDF file as a response
        return send_file(pdf_path, as_attachment=True)

    return "No PDF file found in the root folder."

@app.route("/<type_id>/<user_id>/chat")
def chatbot(type_id: str, user_id: str):
    return render_template("chat.html")


@app.route("/<type_id>/<user_id>/info")
def info_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: dict[str, str] = bot.info_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/conversation")
def conversation_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: list[dict[str, str]] = bot.conversation_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/response_for", methods=["POST"])
def response_for(type_id: str, user_id: str):
    user_says = None
    # content_type = request.headers.get('Content-Type')
    # if (content_type == 'application/json; charset=utf-8'):
    user_says = request.json
    # else:
    #    return jsonify('/response_for request must have content_type == application/json')

    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    assistant_says_list: list[str] = bot.respond(user_says)
    response: dict[str, str] = {
        "user_says": user_says,
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)


@app.route("/<type_id>/<user_id>/reset", methods=["DELETE"])
def reset(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    bot.reset()
    assistant_says_list: list[str] = bot.start()
    response: dict[str, str] = {
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)

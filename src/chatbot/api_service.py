from flask import Flask, request, jsonify, send_from_directory
from data_access import get_disease_info, find_doctor_by_specialty
from dialogue_manager import DialogueManager
from flask import render_template
import os

dialogue_manager = DialogueManager()

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/style.css")
def style():
    return send_from_directory(os.path.join(app.template_folder), "style.css")

@app.route("/script.js")
def script():
    return send_from_directory(os.path.join(app.template_folder), "script.js")

@app.route("/disease", methods=["GET"])
def disease_info():
    name = request.args.get("name")
    info = get_disease_info(name)
    return jsonify(info or {})

@app.route("/doctors", methods=["GET"])
def doctor_list():
    specialty = request.args.get("specialty")
    doctors = find_doctor_by_specialty(specialty)
    return jsonify(doctors)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data["message"]
    response = dialogue_manager.get_response(user_message)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
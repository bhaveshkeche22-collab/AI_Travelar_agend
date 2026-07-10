from flask import Flask, request, jsonify, render_template
from agent.traveler_agend import ask_travel_agent
from database.mysql import save_chat_history, get_chat_history

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/history", methods=["GET"])
def history():
    try:
        rows = get_chat_history()
        return jsonify({"history": rows})
    except Exception as e:
        print("History ERROR:", e)
        return jsonify({"history": []}), 500


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"response": "No JSON received."}), 400

        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"response": "Please enter a message."}), 400

        result = ask_travel_agent(user_message)
        ai_response = result["output"]

        try:
            save_chat_history(user_message, ai_response)
        except Exception as db_err:
            print("Could not save chat history:", db_err)

        return jsonify({
            "response": ai_response,
            "cards": result.get("cards", [])
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"response": f"Backend Error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
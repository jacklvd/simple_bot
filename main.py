from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import os

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = os.path.join(app.root_path, "conversations")
Session(app)


@app.route("/")
def index():
    session.clear()
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    question = request.form["question"].strip().lower()

    if (
        "start" in question
        or "begin" in question
        or "hello" in question
        or "hi" in question
    ):
        session["step"] = "ask_first_name"
        return jsonify({"answer": "Hi! What's your first name?"})

    if "step" not in session:
        return jsonify(
            {"answer": "Please type 'start' or 'hello' to begin the enquiry process."}
        )

    if session["step"] == "ask_first_name":
        # Capitalize the first name before storing it
        session["first_name"] = question.capitalize()
        session["step"] = "ask_last_name"
        return jsonify(
            {"answer": f"Great {session['first_name']}! What's your last name?"}
        )

    if session["step"] == "ask_last_name":
        session["last_name"] = question.capitalize()
        session["step"] = "ask_email"
        return jsonify({"answer": "Thanks! Now, what's your email address?"})

    if session["step"] == "ask_email":
        session["email"] = question
        session["step"] = "answer_questions"
        return jsonify(
            {"answer": "Thank you! You can now ask me any questions about the college."}
        )

    if "end" in question:
        user_info = f"User Info: {session.get('first_name', '')} {session.get('last_name', '')} & {session.get('email', '')}"
        creator_info = "Chatbox Creator: Jack Vo & volg@mail.uc.edu"
        clear_chat_prompt = "Would you like to clear the chat history? (yes/no)"
        # Store the final message before clearing the data
        final_message = f"{user_info}. {creator_info}. {clear_chat_prompt}"
        # Set a flag to indicate the next step is to wait for user response about clearing the chat
        session["step"] = "clear_chat"
        return jsonify({"answer": final_message})

    if session.get("step") == "clear_chat":
        # Check user response for clearing the chat
        if "yes" in question:
            session.clear()
            return jsonify(
                {"answer": "Chat history has been cleared.", "clear_chat": True}
            )
        else:
            session.clear()
            return jsonify({"answer": "Chat history will be preserved."})

    # Example answers to questions
    if session["step"] == "answer_questions":
        # Your existing conditionals for answering questions
        if (
            "football team" in question
            or "college football team" in question
            or "football" in question
            or "college football" in question
        ):
            answer = "Yes, our college has a football team. The college football team is called the Bearcat."
        elif (
            "computer science major" in question
            or "computer science program" in question
            or "cs major" in question
            or "cs program" in question
            or "computer science" in question
        ):
            answer = "Yes, we offer a Computer Science major. CS is a popular major at our college."
        elif (
            "in-state tuition" in question
            or "tuition for in-state" in question
            or "tuition" in question
        ):
            answer = "The in-state tuition is $10,000 per year. We also offer financial aid and scholarships!"
        elif (
            "on campus housing" in question
            or "dorms" in question
            or "housing options" in question
            or "campus housing" in question
            or "housing" in question
        ):
            answer = "Yes, we have on-campus housing options. We have 3 dorms: A, B, and C. Each dorm has a different style and price."
        else:
            answer = "I'm sorry, I don't have the information on that. Please contact admissions@uc.edu for more details."
        # Append user information to the answer
        # user_info = f" (Asked by {session['first_name']} {session['last_name']}, {session['email']})"
        following_question = (
            "You can ask me more questions or type 'end' to end the conversation."
        )
        return jsonify({"answer": answer + f"\n" + following_question})

    return jsonify(
        {
            "answer": "I'm not sure how to answer that. Can you try asking something else?"
        }
    )


if __name__ == "__main__":
    # Ensure the 'conversations' directory exists
    os.makedirs(app.config["SESSION_FILE_DIR"], exist_ok=True)
    app.run(debug=True)

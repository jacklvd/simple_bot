from flask import Flask, render_template, request, jsonify, make_response
import uuid
import re

app = Flask(__name__)


# In-memory storage for chat states
chat_states = {}
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


@app.route("/")
def index():
    user_id = request.cookies.get("user_id")
    if not user_id:
        # Generate a unique user_id using uuid
        user_id = str(uuid.uuid4())
        chat_states[user_id] = {"step": "welcome"}  # Initialize the chat state
        response = make_response(render_template("index.html"))
        response.set_cookie(
            "user_id", user_id, max_age=60 * 60 * 24
        )  # Set the cookie to expire in 1 day
        return response
    if user_id not in chat_states:
        # In case the cookie exists but the state was lost, reinitialize the state
        chat_states[user_id] = {"step": "welcome"}
    return render_template("index.html")


def get_chat_state(user_id):
    return chat_states.setdefault(user_id, {"step": "welcome"})


def save_chat_state(user_id, state):
    chat_states[user_id] = state


def clear_chat_state(user_id):
    if user_id in chat_states:
        # Clear the user's chat state
        del chat_states[user_id]


@app.route("/ask", methods=["POST"])
def ask():
    user_id = request.cookies.get("user_id")
    print(chat_states)
    if not user_id or user_id not in chat_states:
        return jsonify(
            {"answer": "There was an error with your session. Please refresh the page."}
        )

    state = chat_states.get(user_id, {"step": "welcome"})
    question = request.form["question"].strip().lower()

    if state["step"] == "welcome" or any(
        word in question for word in ["start", "begin", "hello", "hi"]
    ):
        state["step"] = "ask_first_name"
        save_chat_state(user_id, state)
        return jsonify({"answer": "Hi! What's your first name?"})

    elif state["step"] == "ask_first_name":
        state["first_name"] = question.capitalize()
        state["step"] = "ask_last_name"
        save_chat_state(user_id, state)
        return jsonify(
            {"answer": f"Great {state['first_name']}! What's your last name?"}
        )

    elif state["step"] == "ask_last_name":
        state["last_name"] = question.capitalize()
        state["step"] = "ask_email"
        save_chat_state(user_id, state)
        return jsonify({"answer": "Thanks! Now, what's your email address?"})

    elif state["step"] == "ask_email":
        if not EMAIL_REGEX.match(question):
            # If the email doesn't match the pattern, ask for it again
            return jsonify({"answer": "Please enter a valid email address."})
        else:
            # If the email is valid, save it and proceed
            state["email"] = question
            state["step"] = "answer_questions"
            save_chat_state(user_id, state)
            return jsonify(
                {
                    "answer": "Thank you! You can now ask me any questions about the college."
                }
            )

    elif (
        "end" in question
        or "stop" in question
        or "quit" in question
        or "bye" in question
    ):
        if (
            state.get("step") != "prompt_clear_ui"
        ):  # Check if it's the first 'end' message
            # If it's the first 'end', prompt the user to clear the chat history
            user_info = f"User Info: {state.get('first_name', '')} {state.get('last_name', '')} & {state.get('email', '')}"
            creator_info = "Chatbox Creator: Jack Vo & volg@mail.uc.edu"
            final_message = f"{user_info}. {creator_info}"
            state["step"] = "prompt_clear_ui"
            save_chat_state(user_id, state)
            clear_chat_prompt = "Would you like to clear the chat history? (yes/no)"
            return jsonify(
                {"answer": final_message, "prompt_clear_chat": clear_chat_prompt}
            )
        else:
            # If it's not the first 'end', clear the state regardless of user's response
            clear_chat_state(user_id)
            return jsonify(
                {"answer": "Chat history has been cleared.", "clear_chat": True}
            )

    elif state["step"] == "prompt_clear_ui":
        if "yes" in question:
            # If user confirms to clear the UI, clear the chat state and set flag
            clear_chat_state(user_id)
            return jsonify(
                {"answer": "Chat history has been cleared.", "clear_chat": True}
            )
        elif "no" in question:
            # If user chooses not to clear the UI, just end the chat without clearing
            clear_chat_state(user_id)
            return jsonify({"answer": "Chat ended without clearing history."})
        else:
            # If the response is not 'yes' or 'no', remind the user of the options
            return jsonify(
                {
                    "answer": "Please respond with 'yes' to clear the chat history or 'no' to keep it."
                }
            )

    elif state["step"] == "answer_questions":
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
        following_question = (
            "You can ask me more questions or type 'end' to end the conversation."
        )
        return jsonify({"answer": answer + f"\n" + following_question})
    else:
        return jsonify(
            {
                "answer": "I'm not sure how to answer that. Can you try asking something else?"
            }
        )


if __name__ == "__main__":
    app.run(debug=True)

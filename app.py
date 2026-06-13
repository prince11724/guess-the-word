import sys

try:
    from flask import Flask, render_template, request, session  # type: ignore[import]
except ImportError:
    print("Error: Flask is not installed.")
    print("Install it with: pip install flask")
    sys.exit(1)

import random

app = Flask(__name__)
app.secret_key = "secret123"


# LOAD WORDS FROM FILE
def load_words(category):
    word_data = {}

    try:
        with open(f"{category}.txt", "r", encoding="utf-8") as file:
            for line in file.read().splitlines():

                if "|" in line:
                    word, description = line.split("|", 1)

                    word_data[word.strip().lower()] = description.strip()

    except:
        pass

    return word_data


# GET RANDOM WORD
def get_random_word(word_data):

    if not word_data:
        return ""

    return random.choice(list(word_data.keys()))


@app.route("/", methods=["GET", "POST"])
def home():

    # INIT SESSION SAFELY
    session.setdefault("started", False)
    session.setdefault("level", 1)
    session.setdefault("guess_count", 0)
    session.setdefault("hint_count", 0)
    session.setdefault("score", 0)
    session.setdefault("category", "")
    session.setdefault("word_data", {})
    session.setdefault("secret", "")

    message = ""
    guessed_word = ""

    if request.method == "POST":

        action = request.form.get("action")

        # START GAME
        if action == "start":

            category = request.form.get("category", "animals")

            word_data = load_words(category)

            if not word_data:
                message = "❌ No words found in file!"

                return render_template(
                    "index.html",
                    started=False,
                    message=message,
                    attempts=5,
                    score=0,
                    level=1,
                    category="",
                    secret="",
                    guessed_word="",
                    game_over=False
                )

            session["category"] = category
            session["word_data"] = word_data
            session["secret"] = get_random_word(word_data)

            session["level"] = 1
            session["guess_count"] = 0
            session["hint_count"] = 0
            session["score"] = 0
            session["started"] = True

            message = "🎮 Game Started!"

        # RESTART
        elif action == "restart":

            word_data = session.get("word_data", {})

            session["secret"] = get_random_word(word_data)
            session["guess_count"] = 0
            session["hint_count"] = 0

            message = "🔄 Restarted!"

        # GUESS
        elif action == "guess":

            guess = request.form.get("guess", "").lower().strip()

            guessed_word = guess

            if session["guess_count"] >= 5:

                message = f"💀 Game Over! Word was {session['secret']}"

            elif not guess:

                message = "⚠️ Enter a word"

            elif len(guess) != len(session["secret"]):

                message = f"⚠️ Word must be {len(session['secret'])} letters"

            else:

                session["guess_count"] += 1

                if guess == session["secret"]:

                    session["score"] += 10
                    session["level"] += 1

                    message = f"🎉 Correct! Level {session['level']}"

                    session["secret"] = get_random_word(
                        session["word_data"]
                    )

                    session["guess_count"] = 0
                    session["hint_count"] = 0

                elif session["guess_count"] >= 5:

                    message = f"💀 Game Over! Word was {session['secret']}"

                else:

                    message = "❌ Wrong Guess"

        # HINT
        elif action == "hint":

            secret = session.get("secret", "")
            hint_count = session.get("hint_count", 0)

            if not secret:

                message = "⚠️ No word selected"

            else:

                hint_count += 1
                session["hint_count"] = hint_count

                if hint_count == 1:

                    message = f"💡 First Letter: {secret[0]}"

                elif hint_count == 2:

                    message = f"💡 Random Letter: {random.choice(secret)}"

                elif hint_count == 3:

                    word_data = session.get("word_data", {})

                    description = word_data.get(
                        secret.lower(),
                        "No description available."
                    )

                    message = f"💡 Description: {description}"

                else:

                    message = f"💡 Length: {len(secret)} letters"

        # HOME RESET
        elif action == "home":

            session.clear()

            message = "Choose Category"

    return render_template(
        "index.html",
        started=session.get("started"),
        message=message,
        attempts=max(
            0,
            5 - session.get("guess_count", 0)
        ),
        score=session.get("score", 0),
        level=session.get("level", 1),
        category=session.get("category", ""),
        secret=session.get("secret", ""),
        guessed_word=guessed_word,
        game_over=session.get("guess_count", 0) >= 5
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
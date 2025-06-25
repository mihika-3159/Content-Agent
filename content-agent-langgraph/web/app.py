from flask import Flask, render_template, request, redirect, url_for, flash
import os
from src.agent import app as content_agent_app  # Assuming agent.py compiles your LangGraph app

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace for production

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'web', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        topic = request.form.get("topic")
        image = request.files.get("image")
        platforms = request.form.getlist("platforms")

        if not topic or not platforms:
            flash("Topic and platform selection are required.")
            return redirect(url_for("index"))

        image_path = None
        if image and image.filename != "":
            filename = image.filename
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(image_path)

        # Run LangGraph agent (or trigger pipeline)
        initial_state = {
            "topic": topic,
            "platforms": platforms,
            "schedule_time": None,
            "caption": None,
            "content": None,
            "image_url": None,
            "retrieved_docs": None
        }

        final_state = content_agent_app.invoke(initial_state)
        flash("Post content generated successfully.")
        flash(f"Caption: {final_state['caption']}")
        flash(f"Content: {final_state['content']}")
        flash(f"Image URL: {final_state['image_url']}")
        return redirect(url_for("index"))

    return render_template("index.html")

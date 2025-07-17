from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import sys
import traceback

# Fix the import path so 'src' is visible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the compiled LangGraph app
from src.agent import app as content_agent_app

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_in_production'

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'web', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        topic = request.form.get("topic")
        image = request.files.get("image")
        platforms = request.form.getlist("platforms")
        schedule_option = request.form.get("schedule_option")
        schedule_time = request.form.get("schedule_time")
        target_industry = request.form.get("target_industry", "").strip()
        post_mode = request.form.get("post_mode")  # 'text-only' or 'image'

        if not topic or not platforms:
            flash("Topic and platform selection are required.")
            return redirect(url_for("index"))

        # Handle image upload if provided
        image_url = None
        from src.utils.cloudinary_uploader import upload_image_to_cloudinary
        if post_mode == "image" and image and image.filename:
            filename = image.filename
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(image_path)
            image_url = upload_image_to_cloudinary(image_path)
            if not image_url:
                flash("❌ Failed to upload image to Cloudinary.")
                return redirect(url_for("index"))
        elif post_mode == "image" and "linkedin" in platforms:
            flash("⚠️ LinkedIn only supports text-only posts. Image will be ignored.")
            post_mode = "text-only"

        final_schedule_time = schedule_time if schedule_option == "later" else None

        initial_state = {
            "topic": topic,
            "platforms": platforms,
            "schedule_time": final_schedule_time,
            "target_industry": target_industry if target_industry else None,
            "caption": None,
            "content": None,
            "image_url": image_url,
            "image_mode": post_mode,
            "retrieved_docs": None,
            "hashtags": None,
        }

        try:
            final_state = content_agent_app.invoke(initial_state)

            flash("✅ Post content generated successfully.")
            flash(f"📝 Caption: {final_state.get('caption', 'No caption generated')}")
            flash(f"📄 Content: {final_state.get('content', 'No content generated')}")
            flash(f"🏷 Hashtags: {final_state.get('hashtags', 'No hashtags')}")
            if final_state.get("image_url"):
                flash(f"🖼️ Image URL: {final_state['image_url']}")

            # AJAX support
            if request.headers.get('Content-Type') == 'application/json' or request.is_json:
                return jsonify({
                    'success': True,
                    'caption': final_state.get('caption', ''),
                    'content': final_state.get('content', ''),
                    'hashtags': final_state.get('hashtags', ''),
                    'image_url': final_state.get('image_url', ''),
                    'message': 'Content generated successfully!'
                })

        except Exception as e:
            error_message = f"❌ Error generating content: {str(e)}"
            flash(error_message)
            traceback.print_exc()

            if request.headers.get('Content-Type') == 'application/json' or request.is_json:
                return jsonify({'success': False, 'error': error_message}), 500

        return redirect(url_for("index"))

    return render_template("index.html")

@app.route("/api/generate", methods=["POST"])
def api_generate():
    try:
        data = request.get_json()
        if not data or not data.get('topic') or not data.get('platforms'):
            return jsonify({
                'success': False,
                'error': 'Topic and platforms are required'
            }), 400

        initial_state = {
            "topic": data.get('topic'),
            "platforms": data.get('platforms'),
            "schedule_time": data.get('schedule_time'),
            "caption": None,
            "content": None,
            "image_url": None,
            "retrieved_docs": None
        }

        final_state = content_agent_app.invoke(initial_state)

        return jsonify({
            'success': True,
            'caption': final_state.get('caption', ''),
            'content': final_state.get('content', ''),
            'image_url': final_state.get('image_url', ''),
            'message': 'Content generated successfully!'
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
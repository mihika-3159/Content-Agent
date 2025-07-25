from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        topic = request.form.get('topic')
        industry = request.form.get('industry')
        platforms = request.form.getlist('platforms')
        schedule = request.form.get('schedule') == 'yes'
        schedule_time = request.form.get('schedule_time') if schedule else None
        image_mode = request.form.get('image_mode')
        image_url = None

        if image_mode == 'image' and 'image' in request.files:
            image_file = request.files['image']
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
            image_file.save(image_path)
            from src.utils.cloudinary_uploader import upload_image_to_cloudinary
            image_url = upload_image_to_cloudinary(image_path)

        session['initial_state'] = {
            "topic": topic,
            "target_industry": industry or None,
            "platforms": platforms,
            "schedule_time": schedule_time,
            "caption": None,
            "content": None,
            "image_url": image_url,
            "retrieved_docs": None,
            "image_mode": image_mode if image_mode == 'text-only' else 'upload',
            "hashtags": None
        }

        return redirect(url_for('generate'))

    return render_template('index.html')

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
@app.route('/generate', methods=['GET', 'POST'])
def generate():
    state = session.get('initial_state')
    if not state:
        return redirect(url_for('index'))

    # Invoke agent to generate caption, content, hashtags
    final_state = content_agent_app.invoke(state)
    session['final_state'] = final_state

    return render_template('edit.html', state=final_state)

@app.route('/edit', methods=['POST'])
def edit():
    state = session.get('final_state')
    if not state:
        return redirect(url_for('index'))

    updated_caption = request.form.get('caption')
    updated_content = request.form.get('content')

    state['caption'] = updated_caption
    state['content'] = updated_content
    session['final_state'] = state

    return redirect(url_for('mention'))

@app.route('/mention', methods=['GET', 'POST'])
def mention():
    state = session.get('final_state')
    if not state:
        return redirect(url_for('index'))

    if request.method == 'POST':
        mention_text = request.form.get('mention_text', '').strip()
        if mention_text:
            state['caption'] += f"\n\n{mention_text}"
        session['final_state'] = state
        return redirect(url_for('submit'))

    return render_template('mention.html', state=state)

@app.route('/submit')
def submit():
    state = session.get('final_state')
    if not state:
        return redirect(url_for('index'))

    content_agent_app.invoke(state)  # Final post or schedule
    return render_template('success.html', state=state)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
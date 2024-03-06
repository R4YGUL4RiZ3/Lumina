import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload():
    upload_dir = "./.cache"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    if 'audio' not in request.files:
        return jsonify({'messages': 'No seleted file'}), 400
    file = request.files['audio']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(upload_dir, filename))
        return jsonify({'message': 'Sucessfully saved current audio clip'}), 200

if __name__ == "__main__":
    app.run(debug=True)

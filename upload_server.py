from flask import Flask, request
import os

app = Flask(__name__)

UPLOAD_DIR = "data"

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    path = os.path.join(UPLOAD_DIR, "probe_capture.txt")
    file.save(path)
    return "File uploaded successfully"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
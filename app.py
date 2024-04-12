from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
import subprocess
import os
import uuid
# Ensure this utility is properly defined
from openai_utils import generate_qutip_code

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    question = ''
    code = ''
    if request.method == 'POST':
        question = request.form['question']
        code = generate_qutip_code(question)
    # Ensure that variables are correctly passed to the template
    return render_template('index.html', question=question, code=code)


@app.route('/run_code', methods=['POST'])
def run_code():
    code = request.json.get('code', '')
    if not code:
        return jsonify({'error': 'No code provided'}), 400

    filename = f'execute_{uuid.uuid4()}.py'
    try:
        with open(filename, 'w') as f:
            f.write(code)
        result = subprocess.run(['python3', filename],
                                capture_output=True, text=True, timeout=30)
        os.remove(filename)  # Clean up the file
        if result.stderr:
            return jsonify({'error': result.stderr})
        return jsonify({'output': result.stdout})
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Execution time exceeded limit'}), 500
    except Exception as e:
        if os.path.exists(filename):
            os.remove(filename)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
import subprocess
import os  # Import os module for file operations
from openai_utils import generate_qutip_code

load_dotenv()  # Ensure .env file is in the root or specify path

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        question = request.form['question']
        code = generate_qutip_code(question)
        return render_template('index.html', question=question, code=code, answer='')
    return render_template('index.html', question='', code='', answer='')


@app.route('/run_code', methods=['POST'])
def run_code():
    code = request.json.get('code')
    if not code:
        return jsonify({'error': 'No code provided'}), 400

    filename = 'execute.py'
    with open(filename, 'w') as f:
        f.write(code)

    try:
        result = subprocess.run(['python3', filename],
                                capture_output=True, text=True, timeout=30)
        # Delete the file after executing it
        os.remove(filename)
        if result.stderr:
            return jsonify({'error': result.stderr, 'stdout': result.stdout})
        return jsonify({'output': result.stdout})
    except subprocess.TimeoutExpired:
        os.remove(filename)
        return jsonify({'error': 'Execution time exceeded limit'}), 500
    except Exception as e:
        os.remove(filename)
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

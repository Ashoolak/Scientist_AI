from flask import Flask, request, render_template
from openai import OpenAI
from logics.quantum_logic import handle_quantum_query
import re
import ast

client = OpenAI(api_key='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')


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        question = request.form['question']
        response = handle_query(question)
        return render_template('index.html', question=question, answer=response)
    return render_template('index.html', question='', answer='')


def handle_query(query):
    if is_quantum_query(query):
        response = client.chat.completions.create(model="gpt-4-0125-preview",
                                                  messages=[
                                                      {"role": "system",
                                                       "content": "You are a helpful assistant."},
                                                      {"role": "user",
                                                       "content": f"""Given a quantum optics problem description: "{query}", Directly provide the simulation parameters in the following format and nothing else: 
                                                                    "H: [[NUM, NUM], [NUM, NUM]], rho0: [NUM, NUM], tlist: [NUM, NUM, NUM], c_ops: [[[NUM, NUM], [NUM, NUM]]]".
                                                                    """}
                                                  ],
                                                  temperature=0)
        response_text = response.choices[0].message.content.strip()
        variables = parse_gpt_response(response_text)

        print(f"Received quantum query: {variables}")
        answer = handle_quantum_query(variables)
    else:
        # Handle general query
        answer = handle_general_query(query)
    return answer


def handle_general_query(query):
    response = client.chat.completions.create(model="gpt-4-0125-preview",
                                              messages=[
                                                  {"role": "system",
                                                   "content": "You are a helpful assistant."},
                                                  {"role": "user",
                                                   "content": query}
                                              ],
                                              temperature=0)
    return response.choices[0].message.content.strip()


def is_quantum_query(query):
    query = query.lower()
    # Simple keyword check for demonstration
    keywords = ['quantum', 'entanglement', 'qubit', 'superposition']
    return any(keyword in query.lower() for keyword in keywords)


def parse_gpt_response(response_text):
    variables = {}
    print(response_text)

    # Regex patterns adjusted for the new response format
    patterns = {
        'H': r"H: (\[\[.*?\]\])",
        'rho0': r"rho0: (\[.*?\])",
        'tlist': r"tlist: (\[.*?\])",
        'c_ops': r"c_ops: (\[\[\[.*?\]\]\])"
    }

    for var, pattern in patterns.items():
        match = re.search(pattern, response_text)
        if match:
            # Use ast.literal_eval for safe evaluation of the string representation
            try:
                variables[var] = ast.literal_eval(match.group(1))
            except ValueError as e:
                print(f"Error parsing {var}: {e}")

    return variables


if __name__ == '__main__':
    app.run(debug=True)


# question = 'I have a quantum optics problem to solve. consider a single qubit quantum system is driven by markovian noise described by  lindbladian equation:  d\rho/dt = -i[X,\rho]+0.5 Z \rho Z- 0.5\rho. Use QuTip to Canculate the density matrix \rho at time t=2. The qubit is initialy in the ground state |0> at t=0. Only output the number. Think through and do it step by step.'

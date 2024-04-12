from openai import OpenAI
import os
import re

api_key = os.getenv("OPENAI_KEY")
client = OpenAI(api_key=api_key)


def generate_qutip_code(question):
    try:
        response = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": "You are a world-class quantum physicist."},
                {"role": "user", "content": f'Given a quantum optics problem description: "{question}", directly provide the QuTiP Python code without any additional text that could break the code.'}
            ],
            temperature=0
        )
        code = response.choices[0].message.content.strip()
        # Properly handle code extraction by removing unnecessary characters
        code = re.sub(r'^```python\n', '', code)
        code = re.sub(r'\n```$', '', code)
        return code
    except Exception as e:
        return f"Error: {str(e)}"

import openai
from flask import Flask, request, render_template

# Set up OpenAI API credentials and model ID
openai.api_key = "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"
model_id = "text-davinci-003"

# Connect to GPT-3.5 API
def generate_response(prompt):
    query = "write me the best 5 different content ideas to develop videos about: " + prompt
    response = openai.Completion.create(
        engine=model_id,
        prompt=query,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()

# Set up Flask web app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def generate():
    prompt = request.form['prompt']
    response = generate_response(prompt)
    return render_template('index.html', prompt=prompt, response=response)

if __name__ == '__main__':
    app.run(debug=True)
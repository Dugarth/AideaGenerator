import openai
from flask import Flask, request, render_template, make_response
import re
import os

# Set up OpenAI API credentials and model ID
openai.api_key = "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"
model_id = "text-davinci-003"

# Define a function to extract solutions from GPT-4's response
def extract_solutions(text):
    try:
        # The pattern matches a letter (A-Z) or a digit (0-9), followed by a ')' or a '.'
        pattern = r'([A-Z0-9]\)|[A-Z0-9]\.)'
        items = [x.strip() for x in re.split(pattern, text) if x.strip()]

        solutions = {}
        key = None
        for item in items:
            if re.match(pattern, item):
                key = item  # We've found a new solution, so update the key
            elif key:
                solutions[key] = item  # We're in the body of a solution, so add the text to this solution
                key = None  # Reset the key so we don't add text to this solution any more

        return solutions
    except Exception as e:
        print(f"Error while extracting solutions: {e}")
        return {}

# Connect to GPT-3.5 API
def generate_response(prompt):
    query = "write me the best 5 different content ideas to develop videos about: " + prompt+". Make a detailed plan for each idea"
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
    response_parts = [part.strip() for part in response.split('\n') if part.strip()]
    if len(response_parts) < 5 or len(response_parts) > 7:
        return render_template('index.html', prompt=prompt, error="Response was not in expected format")
    if len(response_parts) == 5:
        part1, part2, part3, part4, part5 = response_parts
    else:
        part1, part2, part3, part4, part5 = response_parts[:5]
    solutions = extract_solutions(response)
    return render_template('index.html', prompt=prompt, 
                           part1=part1, part2=part2, part3=part3, part4=part4, part5=part5,
                           solutions=solutions)

@app.route('/download', methods=['POST'])
def download():
    prompt = request.form['prompt']
    response = generate_response(prompt)
    filename = f"{prompt}.txt"
    file_path = os.path.join(app.root_path, 'downloads', filename)
    with open(file_path, 'w') as f:
        f.write(response)
    response = make_response(open(file_path).read())
    response.headers.set('Content-Disposition', 'attachment', filename=filename)
    response.headers.set('Content-Type', 'text/plain')
    return response

@app.route('/download_idea', methods=['POST'])
def download_idea():
    prompt = request.form['prompt']
    idea = request.form['idea']
    filename = f"{prompt} - {idea}.txt"
    file_path = os.path.join(app.root_path, 'downloads', filename)
    with open(file_path, 'w') as f:
        f.write(idea)
    response = make_response(open(file_path).read())
    response.headers.set('Content-Disposition', 'attachment', filename=filename)
    response.headers.set('Content-Type', 'text/plain')
    return response

# Create the downloads folder if it does not exist
if not os.path.exists('downloads'):
    os.makedirs('downloads')

if __name__ == '__main__':
    app.run(debug=True)
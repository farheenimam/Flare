from flask import Flask, render_template, request, jsonify, redirect, url_for
from ibm_watsonx_ai.foundation_models import Model
import os
from dotenv import load_dotenv

app = Flask(__name__)

def get_credentials():
    return {
        "url": os.getenv("IBM_URL"),
        "apikey": os.getenv("IBM_APIKEY")
    }
    

# Define Model Id and Parameters for Different Language Pairs
model_configs = {
    "en-kr": {
        "model_id": "ibm/granite-20b-multilingual",
        "prompt": "Translate the following text from English to Korean:\n\nText: {text}\nTranslation:"
    },
    "kr-en": {
        "model_id": "ibm/granite-20b-multilingual",
        "prompt": "Translate the following text from Korean to English:\n\nText: {text}\nTranslation:"
    },
    "fr-en": {
        "model_id": "ibm/granite-20b-multilingual",
        "prompt": "Translate the following text from French to English:\n\nText: {text}\nTranslation:"
    },
    "es-en": {
        "model_id": "ibm/granite-20b-multilingual",
        "prompt": "Translate the following text from Spanish to English:\n\nText: {text}\nTranslation:"
    },
}

# Define Function to Get the Model Object
def get_model(lang_pair):
    config = model_configs.get(lang_pair, model_configs["kr-en"])
    model = Model(
        model_id=config["model_id"],
        params={
            "decoding_method": "greedy",
            "max_new_tokens": 20,
            "repetition_penalty": 1,
            "stop_sequences": ["\n"]
        },
        credentials=get_credentials(),
        project_id=os.getenv("IBM_PROJECT_ID")
    )
    return model, config["prompt"]

# Providing the input Prompt
def translate_text(text, lang_pair):
    model, prompt_template = get_model(lang_pair)
    prompt_input = prompt_template.format(text=text)
    generated_response = model.generate_text(prompt=prompt_input, guardrails=False)
    return generated_response

@app.route('/', methods=['GET', 'POST'])
def index():
    lang_pair = request.args.get('lang_pair', 'kr-en')  # Get language pair from query parameters
    if request.method == 'POST':
        text = request.form.get('text', '')
        translated_text = translate_text(text, lang_pair)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check if the request is an AJAX request
            return jsonify({'translated_text': translated_text})
        return render_template('index.html', translated_text=translated_text, lang_pair=lang_pair)
    return render_template('index.html', translated_text=None, lang_pair=lang_pair)

@app.route('/set_lang_pair/<lang_pair>', methods=['GET'])
def set_lang_pair(lang_pair):
    # Redirect to the main page with the selected language pair
    return redirect(url_for('index', lang_pair=lang_pair))

if __name__ == '__main__':
    app.run(debug=True)

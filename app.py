from flask import Flask, request, send_from_directory
from flask_cors import CORS
import orjson
import openai
import os
import sqlite3
import re

from categorise import categorise
from generate_schema import process_schema

from gpt import gpt
from gpt import ModeEnum
from prompt_store import get_data_prompt, get_graph_prompt
from utils import sql_to_json

app = Flask(__name__)
CORS(app)

@app.route('/data', methods=['POST'])
def index():
    data_assistant = gpt(ModeEnum.DATA)
    response = data_assistant.prompt(get_data_prompt(request.json.get('prompt', None)))
    results = []
    if response:
        # Open the database
        conn = sqlite3.connect('db/db.db', check_same_thread=False)
        cursor = conn.cursor()
        print(response)
        # use the generated_text to query the database
        try:
            # Fetch all rows and convert them to dictionaries
            cursor.execute(response)
            results = sql_to_json(cursor)
        except SyntaxError as se:
                # analyse the syntax error. if it's not valid sql, continue. if the columns are incorrect, refactor via prompting
            results = {'message': 'invalid sql', 'type': 'error'}
        except sqlite3.OperationalError as oe:
            print(oe)
            if 'column:' in str(oe).split(' '):
                results = {'message': f'{oe}', 'type': 'error'}
            # retry the prompt, pointing out the error
                response = data_assistant.prompt(
                    "the sql contains columns that don't exist. can you rewrite it and make sure it adheres to the above schema? reply strictly with sql only"
                )
                print('new response: ', response)
                cursor.execute(response.split(':')[1].split(';')[0])
                results = sql_to_json(cursor) if sql_to_json(cursor) > 0 else results
        except Exception as e:
            results = {'message' : str(e), 'type': 'error'}
            print(e)
    return orjson.dumps(results), {'Content-Type': 'application/json'}

@app.route('/graph', methods=['POST'])
def graph():
        print('graph request received')
        raw_results = request.json.get('data', None)
        result_schema = process_schema(raw_results)
        second_prompt = f"""given the data in a variable named raw_results that adheres to this jsonschema: {result_schema} and is in a list
        give an example of charts.js code that could display the data. try to pick the most appropriate chart type. 
        the document id for the canvas is 'myChart'. 
        the output must only include the <script> tag. 
        you must not define raw_results in the code.
        never declare a raw_results variable as it already exists
        do not include fetch or an api call. only methods to process the data and the chart itself.
        usr 'var' to declare variables and never 'const' 
        return code only"""
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {'role': 'system', 'content': 'you are an assistant that helps generate code to retrieve and display data. you return all code in <script> tags'},
            {"role": "user", "content": f'{second_prompt}'}
            ],
            temperature=0
        )

        chart_script = response.choices[0].message['content']
        # process script to only get the <script> tags and contents
        script_regex = re.compile(r'<script>(.*?)</script>', re.DOTALL)
        script_match = script_regex.search(chart_script)

        if script_match:
            chart_script = script_match.group(1) #f'<script>{script_match.group(1)}</script>'
        return orjson.dumps({'script': chart_script}), {'Content-Type': 'application/json'}

# Path for our main Svelte page
@app.route("/")
def base():
    return send_from_directory('client/public', 'index.html')

# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory('client/public', path)

if __name__ == "__main__":
    app.run(debug=True)
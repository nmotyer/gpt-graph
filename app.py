from flask import Flask, request
from flask_cors import CORS
import orjson
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
        graph_assistant = gpt(ModeEnum.GRAPH)
        second_prompt = get_graph_prompt(process_schema(request.json.get('data', None)))
        chart_script = graph_assistant.prompt(second_prompt)
        # process script to only get the <script> tag contents
        script_regex = re.compile(r'<script>(.*?)</script>', re.DOTALL)
        script_match = script_regex.search(chart_script)
        if script_match:
            chart_script = script_match.group(1) #f'<script>{script_match.group(1)}</script>'
        return orjson.dumps({'script': chart_script}), {'Content-Type': 'application/json'}

if __name__ == "__main__":
    app.run(debug=True)
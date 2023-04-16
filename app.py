from flask import Flask, request, send_from_directory
from flask_cors import CORS
import orjson
import openai
import os
import sqlite3
import re
from categorise import categorise
from generate_schema import process_schema

app = Flask(__name__)
CORS(app)
creds = ''
try:
    with open('credentials.json', 'r') as cbytes:
        creds = orjson.loads(cbytes.read())['key']
except IOError:
    pass
openai.api_key = os.environ.get("OPENAI_API_KEY", creds)

@app.route('/data', methods=['POST'])
def index():
    results = []

    # print(request.json)

    prompt = request.json.get('prompt', None)
    if prompt:
        # augment the prompt
        prompt = f"""given a sqlite3 database with 4 tables,
        users (id integer primary key, first_name text, last_name text, organisation_id int, date_enrolled text )
        organisations (id integer primary key, parent_id integer, name text), 
        publications (id INTEGER PRIMARY KEY, title TEXT NOT NULL, date_published DATE NOT NULL, publisher_name TEXT NOT NULL) and
        publication_authorship (id INTEGER PRIMARY KEY, author_id INTEGER, publication_id INTEGER, FOREIGN KEY(author_id) REFERENCES users(id), FOREIGN KEY(publication_id) REFERENCES publications(id)),
        generate sql for {prompt} . return sql only"""
        # Open the database
        conn = sqlite3.connect('db/db.db', check_same_thread=False)
        cursor = conn.cursor()

        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {'role': 'system', 'content': 'you are an assistant that helps generate sql to retrieve data. you return code only. do not provide notes'},
            {"role": "user", "content": f'{prompt}'}
            ],
        temperature=0
    )
        print(response.choices[0].message['content'])
        # use the generated_text to query the database
        try:
            # Fetch all rows and convert them to dictionaries
            cursor.execute(response.choices[0].message['content'])

            columns = [desc[0] for desc in cursor.description]
            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))
                results.append(row_dict)
        except SyntaxError as se:
                # analyse the syntax error. if it's not valid sql, continue. if the columns are incorrect, refactor via prompting
            results = {'message': 'invalid sql', 'type': 'error'}
        except sqlite3.OperationalError as oe:
            print(oe)
            if 'column:' in str(oe).split(' '):
                results = {'message': f'{oe}', 'type': 'error'}
            # retry the prompt, pointing out the error
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {'role': 'system', 'content': 'you are an assistant that helps generate sql to retrieve data. you return code only. do not provide notes'},
                        {"role": "user", "content": f'{prompt}'},
                        {'role': 'assistant', 'content': f"{response.choices[0].message['content']}"},
                        {"role": "user", "content": "the sql contains columns that don't exist. can you rewrite it and make sure it adheres to the above schema? reply strictly with sql only"},
                        ],
                    temperature=0
                )
                new_results = []
                print('new response: ', response.choices[0].message['content'])
                cursor.execute(response.choices[0].message['content'].split(':')[1].split(';')[0])
                columns = [desc[0] for desc in cursor.description]
                for row in cursor.fetchall():
                    row_dict = dict(zip(columns, row))
                    new_results.append(row_dict)
                results = new_results if len(new_results) > 0 else results


        except Exception as e:
            results = {'error' : str(e)}
            print('general error')
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
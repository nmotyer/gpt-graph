from flask import Flask
from flask_cors import CORS
import orjson
import sqlite3
import re
from flask_socketio import SocketIO, emit

from categorise import categorise
from generate_schema import process_schema

from gpt import gpt
from gpt import ModeEnum
from prompt_store import get_data_prompt, get_graph_prompt, get_idea_prompt
from utils import sql_to_json, summarise_json

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('data')
def handle_data(message):
    data_assistant = gpt(ModeEnum.DATA)
    response = data_assistant.prompt(get_data_prompt(message.get('prompt', None)))
    results = []
    retry = False

    if response:
        conn = sqlite3.connect('/home/nick/code/alex/db/data.db', check_same_thread=False)
        cursor = conn.cursor()
        emit('response', {'message': response, 'type': 'message'}, json=True)

        try:
            cursor.execute(response)
            results = sql_to_json(cursor)
        except SyntaxError as se:
            results = {'message': 'invalid sql', 'type': 'error'}
        except sqlite3.OperationalError as oe:
            # print the error
            print(oe)
            # make frontend aware there is an issue
            emit('response', {'type': 'error', 'message': 'invalid columns detected. retrying...'})
            # set a flag to retry
            retry = True
        except Exception as e:
            results = {'message' : str(e), 'type': 'error'}
            print(e)
    if retry:
            cursor.close()
            conn.close()
            new_conn = sqlite3.connect('/home/nick/code/alex/db/data.db', check_same_thread=False)
            new_cursor = new_conn.cursor()
            response = data_assistant.prompt(
                "the sql contains columns that don't exist. can you rewrite it and make sure it adheres to the above schema? reply strictly with sql only"
            )
            print('new response: ', response)
            new_cursor.execute(response) # .split(':')[1].split(';')[0]
            results = sql_to_json(new_cursor)
            emit('response', {'message': response, 'type': 'message'}, json=True)
    emit('response', {'result': results, 'type': 'result', 'topic': 'data'}, json=True)

@socketio.on('graph')
def handle_graph(message):
    graph_assistant = gpt(ModeEnum.GRAPH)
    data_description = summarise_json(process_schema(message.get('data')), message.get('data'))
    second_prompt = get_graph_prompt(process_schema(message.get('data', None)), data_description)
    chart_script = graph_assistant.prompt(second_prompt)

    script_regex = re.compile(r'<script>(.*?)</script>', re.DOTALL)
    script_match = script_regex.search(chart_script)
    if script_match:
        chart_script = script_match.group(1)
    print('sending graph script')

    emit('response', {'result': chart_script.replace('```', ''), 'type': 'result', 'topic': 'graph'}, json=True)

@socketio.on('idea')
def handle_idea(message):
    idea_assistant = gpt(ModeEnum.IDEA)
    response = idea_assistant.prompt(message.get('data', get_idea_prompt()))
    emit('response', {'message': response, 'type': 'message', 'topic': 'idea'}, json=True)

@socketio.on('suggest_title')
def handle_title(message):
    idea_assistant = gpt(ModeEnum.IDEA)
    response = idea_assistant.prompt(f"""given this text:\n{message.get('data')}\n Suggest a title of a report about this data""")
    emit('response', {'result': response, 'type': 'result', 'topic': 'title'}, json=True)

@socketio.on('summarise')
def handle_summary(message):
    idea_assistant = gpt(ModeEnum.IDEA)
    summary_json, _ = summarise_json(process_schema(message.get('data')), message.get('data'))
    response = idea_assistant.prompt(f"""given this json: 
    {orjson.dumps(summary_json).decode('utf-8')}
    from a database about the university of melbourne and the title of the data: {message.get('title', '')}, please summarise the data and point our any trends""", False)
    print(response)
    emit('response', {'message': response, 'type': 'message', 'topic': 'summary'}, json=True)

@socketio.on('ambiguous')
def handle_ambiguity(message):
    idea_assistant = gpt(ModeEnum.IDEA)
    response = idea_assistant.prompt(message.get('data', f"""given this text from a user: 
    {message}
    is it more likely the query pertains to data or to a visualisation of the data?"""), False)
    emit('response', {'message': response, 'type': 'message', 'topic': 'summary'}, json=True)

if __name__ == "__main__":
    socketio.run(app)
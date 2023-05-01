from flask import Flask
from flask_cors import CORS
import orjson
import sqlite3
import re
from flask_socketio import SocketIO, emit
from itertools import chain

from categorise import categorise
from generate_schema import process_schema

from gpt import gpt
from gpt import ModeEnum
from prompt_store import get_data_prompt, get_graph_prompt, get_idea_prompt, get_modify_graph_prompt
from utils import sql_to_json, summarise_json

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# activate the assistants
data_assistant = gpt(ModeEnum.DATA)
graph_assistant = gpt(ModeEnum.GRAPH)
idea_assistant = gpt(ModeEnum.IDEA)

# some extra lists holding history for data and graph
data_history = []
graph_history = []

@socketio.on('data')
def handle_data(message):
    response = data_assistant.prompt(get_data_prompt(message.get('prompt', None)))
    results = []
    retry = False

    if response:
            # Split the input SQL string into separate statements
        statements = response.strip().split(';')
        if statements[-1] == '':
            statements.pop()
        conn = sqlite3.connect('/home/nick/code/alex/db/data.db', check_same_thread=False)
        cursor = conn.cursor()
        emit('response', {'message': response, 'type': 'message'}, json=True)

        try:
            for statement in statements:
                # Execute the statement and store the results
                cursor.execute(statement)
                result = sql_to_json(cursor)
                results.append(result)
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
            statements = response.strip().split(';')
            if statements[-1] == '':
                statements.pop()
            print('new response: ', response)
            for statement in statements:
                new_cursor.execute(response) # .split(':')[1].split(';')[0]
                result = sql_to_json(new_cursor)
                results.append(result)
            emit('response', {'message': response, 'type': 'message'}, json=True)
    emit('response', {'result': list(chain.from_iterable(results)), 'type': 'result', 'topic': 'data'}, json=True)

@socketio.on('graph')
def handle_graph(message, skip_data_prompting: bool = False):
    if skip_data_prompting:
        chart_script = graph_assistant.prompt(get_modify_graph_prompt(message.get('prompt')))
        print(orjson.dumps(graph_assistant.messages, orjson.OPT_INDENT_2))
    else:
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
    response = idea_assistant.prompt(message.get('data', get_idea_prompt()))
    emit('response', {'message': response, 'type': 'message', 'topic': 'idea'}, json=True)

@socketio.on('suggest_title')
def handle_title(message):
    title_assistant = gpt(ModeEnum.IDEA)
    response = title_assistant.prompt(f"""given this text:\n{message.get('data')}\n Suggest a title of a report about this data""")
    emit('response', {'result': response, 'type': 'result', 'topic': 'title'}, json=True)

@socketio.on('summarise')
def handle_summary(message):
    summary_json, _ = summarise_json(process_schema(message.get('data')), message.get('data'))
    response = idea_assistant.prompt(f"""given this json: 
    {orjson.dumps(summary_json).decode('utf-8')}
    from a database about the university of melbourne and the title of the data: {message.get('title', '')}, please summarise the data and point our any trends""", False)
    print(response)
    emit('response', {'message': response, 'type': 'message', 'topic': 'summary'}, json=True)

@socketio.on('ambiguous')
def handle_ambiguity(message):
    response = idea_assistant.prompt(message.get('data', f"""given this text from a user: 
    {message}
    is it more likely the query pertains to data/query or to a visualisation of the data? please reply with one of 'data', 'graph' or 'neither' """), False)
    print(response)
    if response.strip().lower()[0] == 'd':
        redo_data(message)
    elif response.strip().lower()[0] == 'g':
        redo_graph(message)
    else:
        pass


def redo_data(message):
    emit('response', {'message': 'preparing a new query...', 'type': 'message', 'topic': 'ambiguity'}, json=True)
    handle_data(message)
    return

def redo_graph(message):
    emit('response', {'message': 'preparing a new graph...', 'type': 'message', 'topic': 'ambiguity'}, json=True)
    handle_graph(message, True)
    return

if __name__ == "__main__":
    socketio.run(app)
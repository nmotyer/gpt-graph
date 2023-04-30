from utils import generate_sql_schema, summarise_json
import sqlite3

# retrieve db schema for the below prompts
db = sqlite3.connect('/home/nick/code/alex/db/data.db', check_same_thread=False)
sql_schema = generate_sql_schema(db.cursor())
db.close()

def get_data_prompt(prompt: str) -> str:
    return f"""given a sqlite3 database with these tables:
        {sql_schema},
        generate sql for {prompt} . Do not use aggregate functions in any WHERE clauses.
        never return IDs in output unless asked.
        Do not add columns you don't know exist and make sure to respect foreign keys in the given schema.
        Be creative but the SQL must be correct, not nessesary to use all tables.
        Never use COUNT(citation_counts_by_year.X) or COUNT(citations.X). Never count citations.
        The end goal is to attempt to graph the output, try and limit dimensions and never include ID columns in the output.
        return sql only"""

def get_graph_prompt(result_schema: dict, key_description: str = None) -> str:
    return f"""given the data in a variable named raw_results that adheres to this jsonschema: {result_schema} and is in a list
        give an example of charts.js code that could display the data. try to pick the most appropriate chart type.
        {key_description if key_description else ''}
        if there are more than 1 dataset, bar or line give all a different colour.
        if the data appears to have dates try to use a line graph.
        the document id for the canvas is 'myChart'. 
        the output must only include the <script> tag. 
        you must not define raw_results in the code.
        never declare a raw_results variable as it already exists
        do not include php or use JSON.parse.
        do not include fetch or an api call. only methods to process the data and the chart itself.
        usr 'var' to declare variables and never 'const' 
        return code only"""

def get_idea_prompt() -> str:
    return f"""given a sqlite3 database with these tables:
    {sql_schema}
        give some ideas/names for reports that would be useful for a university aiming for funding for certain departments and growth"""

def get_data_description() -> str:
    return summarise_json()
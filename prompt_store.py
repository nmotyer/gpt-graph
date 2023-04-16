def get_data_prompt(prompt: str) -> str:
    return f"""given a sqlite3 database with 4 tables,
        users (id integer primary key, first_name text, last_name text, organisation_id int, date_enrolled text )
        organisations (id integer primary key, parent_id integer, name text), 
        publications (id INTEGER PRIMARY KEY, title TEXT NOT NULL, date_published DATE NOT NULL, publisher_name TEXT NOT NULL) and
        publication_authorship (id INTEGER PRIMARY KEY, author_id INTEGER, publication_id INTEGER, FOREIGN KEY(author_id) REFERENCES users(id), FOREIGN KEY(publication_id) REFERENCES publications(id)),
        generate sql for {prompt} . return sql only"""

def get_graph_prompt(result_schema: dict) -> str:
    return f"""given the data in a variable named raw_results that adheres to this jsonschema: {result_schema} and is in a list
        give an example of charts.js code that could display the data. try to pick the most appropriate chart type. 
        the document id for the canvas is 'myChart'. 
        the output must only include the <script> tag. 
        you must not define raw_results in the code.
        never declare a raw_results variable as it already exists
        do not include fetch or an api call. only methods to process the data and the chart itself.
        usr 'var' to declare variables and never 'const' 
        return code only"""
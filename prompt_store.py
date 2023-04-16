def get_data_prompt(prompt: str) -> str:
    return f"""given a sqlite3 database with 4 tables,
        users (id integer primary key, first_name text, last_name text, organisation_id int, date_enrolled text )
        organisations (id integer primary key, parent_id integer, name text), 
        publications (id INTEGER PRIMARY KEY, title TEXT NOT NULL, date_published DATE NOT NULL, publisher_name TEXT NOT NULL) and
        publication_authorship (id INTEGER PRIMARY KEY, author_id INTEGER, publication_id INTEGER, FOREIGN KEY(author_id) REFERENCES users(id), FOREIGN KEY(publication_id) REFERENCES publications(id)),
        generate sql for {prompt} . return sql only"""

def get_graph_prompt(raw_results) -> str:
    return 
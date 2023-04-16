import sqlite3
def sql_to_json(cursor: sqlite3.Cursor) -> list[dict]:
    results = []
    if cursor:
        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            results.append(row_dict)
    return results

def summarise_json(json_schema:dict, json_data:dict) -> dict:
    # use the json schema to find number fields

    # find the min and max of the number fields

    # use the json schema to find text fields

    # see if the text fields can be grouped (check duplicate values)



    return

def generate_sql_schema(cursor: sqlite3.Cursor) -> str:
    # Query the sqlite_master table to retrieve the schema information
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
    return  ''.join(row[0]+'\n' for row in cursor.fetchall()).replace('CREATE TABLE', '')

if __name__ == '__main__':
    db = sqlite3.connect('db/db.db', check_same_thread=False)
    print(generate_sql_schema(db.cursor()))
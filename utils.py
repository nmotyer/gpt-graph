import sqlite3
from generate_schema import process_schema
import orjson
import random
from datetime import datetime

def is_date(string, format='%Y-%m-%d'):
    try:
        if len(string) == 2:
            datetime.strptime(string, '%m')
        if len(string) == 4:
            datetime.strptime(string, '%Y')
        else:
            datetime.strptime(string, format)
        return True
    except ValueError:
        return False

def sql_to_json(cursor: sqlite3.Cursor) -> list[dict]:
    results = []
    if cursor:
        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            results.append(row_dict)
    return results

def summarise_json(json_schema:dict, json_data:list[dict]) -> dict:
    # use the json schema to find number fields
    number_fields = [field for field in json_schema['properties'].keys() if json_schema['properties'][field]['type'] == 'number']
    # find the min and max of the number fields

    # check if any string fields are dates
    check_date_fields = [field for field in json_schema['properties'].keys() if json_schema['properties'][field]['type'] == 'string']
    date_fields = []
    text_fields = []
    for check_date_field in check_date_fields:
        temp_check = []
        for obj in json_data[:9]:
            temp_check.append(is_date(obj[check_date_field]))
        if False in temp_check:
            text_fields.append(check_date_field)
        else:
            date_fields.append(check_date_field)
    
    # see if the text fields can be grouped (check duplicate values)
        
    print(number_fields)
    print(date_fields)
    print(text_fields)
    return

def generate_sql_schema(cursor: sqlite3.Cursor) -> str:
    # Query the sqlite_master table to retrieve the schema information
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
    return  ''.join(row[0]+'\n' for row in cursor.fetchall()).replace('CREATE TABLE', '')

if __name__ == '__main__':
    db = sqlite3.connect('db/db.db', check_same_thread=False)
    print(generate_sql_schema(db.cursor()))

    cursor = db.cursor()
    cursor.execute(
        """SELECT o.name AS organisation_name, 
            strftime('%Y', date_enrolled) AS year_enrolled, 
            COUNT(*) AS enrollment_count
        FROM users u
        JOIN organisations o ON u.organisation_id = o.id
        WHERE date_enrolled BETWEEN '2000-01-01' AND '2023-12-31'
        GROUP BY o.name, year_enrolled
        ORDER BY o.name, year_enrolled;"""
                   )
    data = sql_to_json(cursor)
    schema = process_schema(data)
    with open('debug/schema.json', 'wb') as sb:
        sb.write(orjson.dumps(schema,option=orjson.OPT_INDENT_2))
    with open('debug/data.json', 'wb') as sb:
        sb.write(orjson.dumps(data,option=orjson.OPT_INDENT_2))
    summary_data = summarise_json(schema, data)

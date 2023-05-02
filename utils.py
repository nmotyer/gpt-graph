import sqlite3
from generate_schema import process_schema
import orjson
import random
from datetime import datetime

def is_date(value, format='%Y-%m-%d'):
    if isinstance(value, (int, float)):
        value = str(int(value))
    elif not isinstance(value, str):
        return False

    try:
        if len(value) == 2:
            datetime.strptime(value, '%m')
        elif len(value) == 4:
            datetime.strptime(value, '%Y')
        else:
            datetime.strptime(value, format)
        return True
    except ValueError:
        return False
    
def find_min_max(json_data: list[dict], key_to_use: str) -> list[dict]:
# Sort the JSON data by the key to be used
    sorted_json_data = sorted(json_data, key=lambda x: x[key_to_use])

    # Calculate the median value and find the JSON closest to it
    total = len(sorted_json_data)
    middle = total // 2
    if total % 2 == 0:
        median_value = (sorted_json_data[middle - 1][key_to_use] + sorted_json_data[middle][key_to_use]) / 2
        median_json = sorted_json_data[middle - 1:middle + 1]
    else:
        median_value = sorted_json_data[middle][key_to_use]
        median_json = [sorted_json_data[middle]]

    # Find JSON with min value (which is the first item in the sorted array)
    min_json = sorted_json_data[0]

    # Find JSON with max value (which is the last item in the sorted array)
    max_json = sorted_json_data[-1]

    # Get 8 JSON closest to the median value
    if len(median_json) == 1:
        closest_json = sorted_json_data[:middle] + sorted_json_data[middle + 1:]
    else:
        closest_json = sorted_json_data[:middle - 1] + sorted_json_data[middle + 1:]
    if len(closest_json) < 8: 
        sample_size = len(closest_json)
    else: 
        sample_size = 8
    if sample_size > 0:
        random_json = random.sample(closest_json, k=sample_size)
    else:
        return closest_json
    random_json.insert(0, min_json)
    random_json.append(max_json)
    return random_json

def has_duplicates(json_data: list[dict], field: str) -> bool:
    seen_values = set()
    for json_obj in json_data:
        value = json_obj.get(field)
        if value is not None and isinstance(value, str):
            if value in seen_values:
                return True
            seen_values.add(value)
    return False

def can_group(json_data: list[dict], fields: list[str]) -> list[str]:
    return [field for field in fields if has_duplicates(json_data, field)]

def join_with_and(words: list[str]) -> str:
    if len(words) == 0:
        return ""
    elif len(words) == 1:
        return words[0]
    elif len(words) == 2:
        return " and ".join(words)
    else:
        return ", ".join(words[:-1]) + ", and " + words[-1]
def generate_field_description(number_fields: list[str] = [],
                               date_fields: list[str] = [],
                               group_fields: list[str] = [],
                               text_fields: list[str] = []) -> str:
    return f"""in the data described by the jsonschema:
{join_with_and(number_fields)} {'are numbers' if len(number_fields) > 0 else ''}
{join_with_and(date_fields)} {'are dates and should be the x-axis' if len(date_fields) > 0 else ''}
{join_with_and(group_fields)} {'contains duplicate values within their own fields and each unique value should be its own dataset possible' if len(group_fields) > 0 else ''}
{join_with_and(text_fields)} {'are string values' if len(text_fields) > 0 else ''}"""

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
    date_names = ['year', 'month', 'day', 'year_published']
    for field in json_schema['properties'].keys():
        print(field)
    number_fields = [field for field in json_schema['properties'].keys() if json_schema['properties'][field]['type'] == 'number' and field not in date_names]
    # find the min, max and median of the number fields and return json rows that contain those or are nearest to those values
    if len(number_fields) > 0:
        candidate_json = find_min_max(json_data, number_fields[0])
    else:
        if len(json_data) < 8:
            sample_size = len(json_data)
        else:
            sample_size = 8
        candidate_json = random.choices(json_data, k=sample_size)

    # check if any string fields are dates
    check_date_fields = [field for field in json_schema['properties'].keys() if json_schema['properties'][field]['type'] == 'string']
    check_date_fields += [field for field in json_schema['properties'].keys() if field in date_names]
    date_fields = []
    text_fields = []
    can_group_fields = []
    for check_date_field in check_date_fields:
        temp_check = []
        for obj in candidate_json:
            temp_check.append(is_date(obj[check_date_field]))
        if False in temp_check:
            text_fields.append(check_date_field)
        else:
            date_fields.append(check_date_field)
    
    # see if the text fields can be grouped (check duplicate values)

    can_group_fields = can_group(json_data, text_fields)
        
    print(generate_field_description(number_fields, date_fields, can_group_fields, text_fields))
    return candidate_json, generate_field_description(number_fields, date_fields, can_group_fields, text_fields)

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

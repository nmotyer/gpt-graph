import sqlite3
def sql_to_json(cursor: sqlite3.Cursor) -> list[dict]:
    results = []
    if cursor:
        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            results.append(row_dict)
    return results
import sqlite3
import os
import random
import datetime
from faker import Faker

insert = os.environ.get('INSERT', False)

db = sqlite3.connect('db.db')

db.execute('CREATE TABLE IF NOT EXISTS users (id integer primary key, first_name text, last_name text, organisation_id int, date_enrolled text )')
db.execute('CREATE TABLE IF NOT EXISTS organisations (id integer primary key, parent_id integer, name text)')
db.execute('CREATE TABLE IF NOT EXISTS publications (id INTEGER PRIMARY KEY, title TEXT NOT NULL, date_published DATE NOT NULL, publisher_name TEXT NOT NULL);')
db.execute("CREATE TABLE IF NOT EXISTS publication_authorship (id INTEGER PRIMARY KEY, author_id INTEGER, publication_id INTEGER, FOREIGN KEY(author_id) REFERENCES users(id), FOREIGN KEY(publication_id) REFERENCES publications(id));")

# Generate fake publication titles and publisher names using the Faker library
fake = Faker()
titles = list(set([fake.sentence() for _ in range(100000)]))
publisher_names = [fake.company() for _ in range(12)]

def generate_random_date(start_year: int = 2010, end_year: int = 2023) -> str:
    start_date = datetime.date(start_year, 1, 1)
    end_date = datetime.date(end_year, 12, 31)

    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    random_date = start_date + datetime.timedelta(days=random_days)
    return random_date.strftime('%Y-%m-%d')

if insert:
    # Insert mock data into the organisations table
    organisations = [
        ('Faculty of Science', None),
        ('Faculty of Medicine', None),
        ('Faculty of Law', None),
        ('Faculty of Engineering', None),
        ('Faculty of Business', None),
        ('Faculty of Arts', None),
        ('Faculty of Social Sciences', None),
        ('Faculty of Education', None),
        ('Faculty of Information Technology', None),
        ('Faculty of Environmental Sciences', None),
        ('Department of Physics', 1),
        ('Department of Chemistry', 1),
        ('Department of Biology', 1),
        ('Department of Anatomy', 2),
        ('Department of Pediatrics', 2),
        ('Department of Surgery', 2),
        ('Department of Civil Engineering', 4),
        ('Department of Mechanical Engineering', 4),
        ('Department of Electrical Engineering', 4),
        ('Department of Accounting', 5),
        ('Department of Marketing', 5),
        ('Department of Finance', 5),
        ('Department of Anthropology', 7),
        ('Department of Sociology', 7),
        ('Department of Psychology', 7),
        ('Department of Curriculum Studies', 8),
        ('Department of Educational Psychology', 8),
        ('Department of Special Education', 8),
        ('Department of Computer Science', 9),
        ('Department of Information Systems', 9),
        ('Department of Software Engineering', 9),
        ('Department of Environmental Studies', 10),
        ('Department of Geography', 10),
        ('Department of Geology', 10)
    ]
    for org in organisations:
        db.execute('INSERT INTO organisations (name, parent_id) VALUES (?, ?)', org)

    # Insert mock data into the users table
    first_names = [
                    'John', 'Jane', 'Bob', 'Alice', 'Charlie', 'Samantha', 'Mike', 'Emily', 'David', 'Lena', 
                    'William', 'Olivia', 'Peter', 'Eva', 'Frank', 'Julia', 'Jack', 'Isabella', 'George', 'Mia',
                    'Harry', 'Sophia', 'Tom', 'Grace', 'Ryan'
                   ]
    last_names = [
                    'Smith', 'Doe', 'Johnson', 'Williams', 'Jones', 'Brown', 'Garcia', 'Lee', 'Harris', 'Davis', 
                    'Anderson', 'Wilson', 'Miller', 'Wilson', 'Campbell', 'Ross', 'Taylor', 'Murphy', 'King', 'Green', 
                    'Evans', 'Collins', 'Hall', 'Turner', 'Scott'
                  ]
    for i in range(1, 10001):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        # assign each user randomly to a department
        org_id = random.randint(1, len(organisations))
        date_string = generate_random_date()
        db.execute('INSERT INTO users (id, first_name, last_name, organisation_id, date_enrolled) VALUES (?, ?, ?, ?, ?)', (i, first_name, last_name, org_id, date_string))

    # Generate rows of mock data for the publications table
    data = []
    for i in range(100000):
        title = titles[i]
        date_published = generate_random_date(2000, 2023)
        publisher_name = random.choice(publisher_names)
        data.append((i+1, title, date_published, publisher_name))
    db.commit()

    # Insert the mock data into the 'publications' table
    db.executemany('INSERT INTO publications VALUES (?, ?, ?, ?)', data)

    c = db.cursor()
    c.execute("SELECT id FROM users")
    author_ids = [row[0] for row in c.fetchall()]
    

    c.execute("SELECT id FROM publications")
    publication_ids = [row[0] for row in c.fetchall()]

    values = [(random.choice(author_ids), random.choice(publication_ids)) for i in range(700000)]
    db.executemany("INSERT INTO publication_authorship (author_id, publication_id) VALUES (?, ?)", values)




db.commit()
db.close()
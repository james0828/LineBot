import psycopg2
from settings import SETTINGS

host = SETTINGS['DB_HOST']
dbname = SETTINGS['DB_NAME']
user = SETTINGS['DB_USER']
password = SETTINGS['DB_PASS']
sslmode = "require"

conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)

conn = psycopg2.connect(conn_string)
print("Connection established")

cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS MESSAGE_QUEUE, TODO_LIST;")
print("Finished dropping table (if existed)")

# Create a table
cursor.execute("""
  CREATE TABLE MESSAGE_QUEUE(
    id serial PRIMARY KEY,
    room_id VARCHAR(200),
    msg VARCHAR(5000),
    finished boolean default(FALSE)
  );""")

cursor.execute("""
  CREATE TABLE TODO_LIST (
    id serial PRIMARY KEY,
    room_id VARCHAR(200),
    content VARCHAR(5000),
    finished boolean default(FALSE),
    is_bot boolean default(FALSE),
    CONSTRAINT unique_room_id_content UNIQUE(room_id, content)
  );""")

cursor.execute("""INSERT INTO TODO_LIST (room_id, content) VALUES ('123', '456')""")
cursor.execute("""INSERT INTO TODO_LIST (room_id, content, finished) VALUES ('123', '45656', True)""")

try:
  cursor.execute("""SELECT * FROM TODO_LIST WHERE FINISHED = %s AND room_id = %s ORDER BY FINISHED ASC""", (False, '123'))
  print(cursor.fetchall())
except Exception as e:
  print(e)


print("Finished creating table")

# Clean up
conn.commit()
cursor.close()
conn.close()
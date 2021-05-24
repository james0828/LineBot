from settings import SETTINGS
import psycopg2

INSERT_MESSAGE_QUEUE = """
INSERT INTO MESSAGE_QUEUE (room_id, msg) VALUES (%s, %s)
"""

QUERY_MESSAGE_QUEUE = """
SELECT * FROM MESSAGE_QUEUE WHERE FINISHED = FALSE ORDER BY ID ASC
"""

UPDATE_MESSAGE = """
UPDATE MESSAGE_QUEUE SET FINISHED = TRUE WHERE ID = %s
"""

INSERT_TODO_LIST = """
INSERT INTO TODO_LIST (room_id, content) VALUES (%s, %s)
"""

UPDATE_TODO_LIST = """
UPDATE TODO_LIST SET FINISHED = NOT FINISHED WHERE room_id = %s AND CONTENT = %s
"""

QUERY_TODO_LIST = """
SELECT * FROM TODO_LIST WHERE room_id = %s AND FINISHED = %s ORDER BY FINISHED ASC
"""

QUERY_ALL_TODO_LIST = """
SELECT * FROM TODO_LIST WHERE room_id = %s ORDER BY ID ASC
"""

DELETE_TODO_LIST = """
DELETE FROM TODO_LIST WHERE room_id = %s AND content = %s
"""

class DB:
  def __init__(self):
    self.connect_database()
  
  def connect_database(self):
    host = SETTINGS['DB_HOST']
    dbname = SETTINGS['DB_NAME']
    user = SETTINGS['DB_USER']
    password = SETTINGS['DB_PASS']
    sslmode = "require"

    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)
    
    self.conn = psycopg2.connect(conn_string)
    self.cursor = self.conn.cursor()

  def close_database(self):
    self.cursor.close()
    self.conn.close()
  
  def commit(self):
    self.conn.commit()
  
  def rollback(self):
    self.conn.rollback()

  def insert_message(self, room_id, msg):
    self.cursor.execute(INSERT_MESSAGE_QUEUE, (room_id, msg))
    self.commit()
  
  def update_message(self, id):
    self.cursor.execute(UPDATE_MESSAGE, (id,))
    self.commit()

  def query_message(self):
    self.cursor.execute(QUERY_MESSAGE_QUEUE)
    return self.cursor.fetchall()
  
  def insert_todo_list(self, room_id, content):
    try:
      self.cursor.execute(INSERT_TODO_LIST, (room_id, content))
      self.commit()
      return True
    except:
      self.rollback()
      return False
  
  def update_todo_list(self, room_id, content):
    self.cursor.execute(UPDATE_TODO_LIST, (room_id, content))
    self.commit()
    return True
  
  def query_todo_list(self, room_id, status=None):
    if status is None:
      self.cursor.execute(QUERY_ALL_TODO_LIST, (room_id,))
    else:
      self.cursor.execute(QUERY_TODO_LIST, (room_id, status))
    
    return self.cursor.fetchall()
  
  def delete_todo_list(self, room_id, content):
    self.cursor.execute(DELETE_TODO_LIST, (room_id, content))
    self.commit()
    return True
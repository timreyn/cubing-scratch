from absl import flags
import mysql.connector

FLAGS = flags.FLAGS

flags.DEFINE_bool('debug', False, 'Debug db queries.')

db = mysql.connector.connect(
  host='localhost',
  user='root',
  password='',
  database='wca')

def run(query, cursor=None):
  if not cursor:
    cursor = db.cursor()
  if FLAGS.debug:
    printed_query = '\n'.join([line.strip() for line in query.split('\n')])
    print(printed_query)
  cursor.execute(query)
  for row in cursor.fetchall():
    yield row
  if FLAGS.debug:
    print('%d rows returned.' % cursor.rowcount)

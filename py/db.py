from absl import flags
from dateutil import parser
import mysql.connector
import os

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

def latest_export():
  export = os.path.dirname(os.path.realpath(__file__)) + '/../latest_export'
  with open(export) as f:
    return f.read().strip()

def credit(markdown):
  export = latest_export()
  export_datetime = parser.parse(export.split('_')[-1])
  if markdown:
    export = export.replace('_', '\_')
  return 'This information is based on competition results owned and maintained by the World Cube Association, published at %s as of %s (version %s).' % ('<https://worldcubeassociation.org/results>' if markdown else 'https://worldcubeassociation.org/results', export_datetime.strftime('%B %d, %Y'), export)

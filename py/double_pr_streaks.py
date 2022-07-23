from absl import app
from absl import flags
import collections

from db import db
import formatters

FLAGS = flags.FLAGS

flags.DEFINE_string('event_id', '333', 'Event to use.', short_name='e')
flags.DEFINE_integer('num', 20, 'Number to output.')

NO_TIME = 999999999999999

def main(argv):
  cursor = db.cursor()
  if FLAGS.event_id != 'all':
    cursor.execute('SELECT personId, best, average FROM Results JOIN Competitions ON Results.competitionId=Competitions.id JOIN RoundTypes ON Results.roundTypeId=RoundTypes.id WHERE eventId = "%s" ORDER BY personId ASC, startDate ASC, rank ASC' % (FLAGS.event_id))
  else:
    cursor.execute('SELECT CONCAT(personId, ",", eventId), best, average FROM Results JOIN Competitions ON Results.competitionId=Competitions.id JOIN RoundTypes ON Results.roundTypeId=RoundTypes.id ORDER BY 1 ASC, startDate ASC, rank ASC')
  top_n = []

  current_person_id = None
  streak = 0
  pr_single = NO_TIME
  pr_average = NO_TIME
  for row in cursor.fetchall():
    personId = row[0]
    best = row[1]
    average = row[2]
    if personId != current_person_id:
      top_n += [(current_person_id, streak)]
      current_person_id = personId
      streak = 0
      pr_single = NO_TIME
      pr_average = NO_TIME
    if best <= pr_single and best > 0 and average <= pr_average and average > 0:
      streak += 1
      pr_single = best
      pr_average = average
    else:
      top_n += [(current_person_id, streak)]
      streak = 0
      if best <= pr_single and best > 0:
        pr_single = best
      if average <= pr_average and average > 0:
        pr_average = average
    top_n = sorted(top_n, key=lambda i: i[1] * -1)[:FLAGS.num]
  top_n += [(current_person_id, streak)]
  top_n = sorted(top_n, key=lambda i: i[1] * -1)[:FLAGS.num]

  for person_id, streak in top_n:
    print(person_id, streak)


if __name__ == '__main__':
  app.run(main)

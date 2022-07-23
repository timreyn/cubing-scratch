from absl import app
from absl import flags

from db import db

FLAGS = flags.FLAGS

flags.DEFINE_string('event_id', '333', 'Event to use.', short_name='e')
flags.DEFINE_integer('time', 2000, 'Time to beat.')
flags.DEFINE_boolean('average', False, 'If true, use averages.')
flags.DEFINE_integer('num', 20, 'Number to output.')
flags.DEFINE_boolean('active_only', False, 'If true, only output currently running streaks.')

def main(argv):
  cursor = db.cursor()
  if FLAGS.average:
    cursor.execute('SELECT personId, competitionId, average FROM Results JOIN Competitions ON Results.competitionId=Competitions.id JOIN RoundTypes ON Results.roundTypeId=RoundTypes.id WHERE eventId = "%s" ORDER BY personId ASC, startDate ASC, rank ASC' % (FLAGS.event_id))
  else:
    cursor.execute('SELECT personId, competitionId, value1, value2, value3, value4, value5 FROM Results JOIN Competitions ON Results.competitionId=Competitions.id JOIN RoundTypes ON Results.roundTypeId=RoundTypes.id WHERE eventId = "%s" ORDER BY personId ASC, startDate ASC, rank ASC' % (FLAGS.event_id))
  top_n = []

  current_person_id = None
  streak = 0
  streak_start = ''
  for row in cursor.fetchall():
    personId = row[0]
    competitionId = row[1]
    times = row[2:]
    if personId != current_person_id:
      if streak:
        top_n += [(current_person_id, streak, streak_start, 'n/a')]
      current_person_id = personId
      streak = 0
      streak_start = ''
    for time in times:
      if time == 0 or time == -2:
        continue
      if time < FLAGS.time and time != -1:
        streak += 1
        if streak == 1:
          streak_start = competitionId
      else:
        if streak and not FLAGS.active_only:
          top_n += [(current_person_id, streak, streak_start, competitionId)]
        streak = 0
        streak_start = ''
    top_n = sorted(top_n, key=lambda i: i[1] * -1)[:FLAGS.num]
  top_n += [(current_person_id, streak, streak_start, 'n/a')]
  top_n = sorted(top_n, key=lambda i: i[1] * -1)[:FLAGS.num]

  for person_id, streak, start, end in top_n:
    print('%s: %d (%s - %s)' % (person_id, streak, start, end))


if __name__ == '__main__':
  app.run(main)

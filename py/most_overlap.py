# Compute the competitions with the most overlap.
# https://www.facebook.com/groups/439995439706174/posts/1625099454529094/

from absl import app
from absl import flags
import collections

from db import db

FLAGS = flags.FLAGS

flags.DEFINE_integer('top_n', 25, 'Number of competition pairs to return.')

def main(argv):
  cursor = db.cursor()
  cursor.execute('SELECT DISTINCT personId, competitionId FROM Results')
  competition_to_persons = collections.defaultdict(list)
  for row in cursor:
    competition_to_persons[row[1]] += [row[0]]
  competitions_sorted = sorted(competition_to_persons.keys(), key=lambda c: len(competition_to_persons[c]) * -1)
  out = []
  for i, ci in enumerate(competitions_sorted):
    pi = competition_to_persons[ci]
    print('Considering %s (%d)' % (ci, len(pi)))
    if len(out) == FLAGS.top_n and len(pi) < out[-1][2]:
      break
    for j in range(0, i):
      cj = competitions_sorted[j]
      pj = competition_to_persons[cj]
      num = len([x for x in pi if x in pj])
      if len(out) < FLAGS.top_n:
        out += [(ci, cj, num)]
        out.sort(key = lambda x: x[2], reverse=True)
        print(out)
      elif num > out[-1][2]:
        out.pop(-1)
        out += [(ci, cj, num)]
        out.sort(key = lambda x: x[2], reverse=True)
        print(out)
  for x in out:
    print(x[0], x[1], x[2])

if __name__ == '__main__':
  app.run(main)

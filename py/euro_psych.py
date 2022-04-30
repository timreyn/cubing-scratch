from absl import app
from absl import flags
import collections
import datetime
import json
import requests

import common
import db
import formatters

FLAGS = flags.FLAGS

flags.DEFINE_string('registration_site', 'https://api.wca2022.eu/graphql', 'URL for registration site.')

event_name_to_id = {
  '2x2x2': '222',
  '3x3x3': '333',
  '4x4x4': '444',
  '5x5x5': '555',
  '6x6x6': '666',
  '7x7x7': '777',
  '3x3x3 Blindfolded': '333bf',
  '3x3x3 One-handed': '333oh',
  'Fewest Moves': '333fm',
  'Clock': 'clock',
  'Megaminx': 'minx',
  'Pyraminx': 'pyram',
  'Skewb': 'skewb',
  'Square-1': 'sq1',
  'Multi BLD': '333mbf',
  '4x4x4 Blindfolded': '444bf',
  '5x5x5 Blindfolded': '555bf',
}

qualifications = {
  '444': 6000,
  '555': 11000,
  '666': 21000,
  '777': 28500,
  '333oh': 3000,
  '333bf': 18000,
  'minx': 12000,
  'sq1': 2500,
  'clock': 1200
}

qualification_counts = {
  '333fm': 60,
  '444bf': 25,
  '555bf': 25,
  '333mbf': 25,
}

event_id_to_name = {v: k for k, v in event_name_to_id.items()}

NA = 9999999999

def main(argv):
  body = {
    "operationName": "PublicCompetitorsList",
    "variables": {"page": 1, "first": 1200},
    "query": "query PublicCompetitorsList($first: Int!, $page: Int!) {\n  publicCompetitors(first: $first, page: $page) {\n    data {\n      events {\n        id\n        full_name\n        __typename\n      }\n      first_name\n      id\n      last_name\n      wca_id\n      nationality\n      __typename\n    }\n    paginatorInfo {\n      ...fullPaginator\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment fullPaginator on PaginatorInfo {\n  count\n  currentPage\n  firstItem\n  hasMorePages\n  lastItem\n  lastPage\n  perPage\n  total\n  __typename\n}\n"}
  r = requests.post(FLAGS.registration_site, json = body)
  person_names = {}
  psych = collections.defaultdict(dict)
  for entry in json.loads(r.text)['data']['publicCompetitors']['data']:
    person_names[entry['wca_id']] = entry['first_name'] + ' ' + entry['last_name']
    for event in entry['events']:
      psych[event_name_to_id[event['full_name']]][entry['wca_id']] = NA

  for row in db.run('SELECT personId, eventId, best FROM (SELECT * FROM RanksAverage WHERE eventId NOT LIKE "%%bf" AND eventId != "333fm" UNION ALL SELECT * FROM RanksSingle WHERE eventId LIKE "%%bf" OR eventId="333fm") AS res WHERE personId IN (%s)' % ','.join(["\"%s\"" % x for x in person_names.keys()])):
    personId = row[0]
    eventId = row[1]
    best = row[2]
    if personId in psych[eventId]:
      psych[eventId][personId] = best

  events = [row for row in db.run('SELECT id, name FROM Events ORDER BY rank ASC')]

  print('Last generated ' + datetime.datetime.now(datetime.timezone.utc).isoformat())
  print()

  for event in events:
    eventId = event[0]
    passed_qualification = False
    if eventId not in event_id_to_name:
      continue
    print('# ' + event[1])
    for i, entry in enumerate(sorted(psych[eventId].items(), key=lambda e: e[1])):
      if not passed_qualification:
        if eventId in qualifications and entry[1] > qualifications[eventId]:
          passed_qualification = True
        elif eventId in qualification_counts and (i + 1) > qualification_counts[eventId]:
          passed_qualification = True
        elif entry[1] == NA:
          passed_qualification = True
        if passed_qualification:
          print('=============================================')
      if entry[1] != NA:
        print('%d. %s (%s) (%s)' % (i+1, person_names[entry[0]], entry[0], formatters.FormatTime(entry[1], eventId, 'bf' not in eventId)))
      else:
        print('%d. %s (%s)' % (i+1, person_names[entry[0]], entry[0]))
    print('')


if __name__ == '__main__':
  app.run(main)

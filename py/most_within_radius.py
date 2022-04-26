# Compute the location with the most competitions in a year within 250 km.
# https://www.facebook.com/groups/439995439706174/posts/1620451491660557/
#
# We start with a 4x4 grid of regions of the world, divided by lat + lon.
#
# For each region we generate two lists of competitions:
# -Competitions within --max_distance of the center (actual_pts)
# -Competitions within --max_distance + region.diameter() of the center (possible_pts)
#
# If actual_pts is the highest we've seen, this is our new best.
# If possible_pts is bigger than any actual_pts we've seen, then a point in this region
# might be optimal. So keep searching: subdivide it into a 4x4 grid, and consider each
# of those 16 regions.
# If actual_pts == possible_pts, we don't need to subdivide further. The center we found is
# at least as good as any other point in the region.

from absl import app
from absl import flags

from db import db
import common

FLAGS = flags.FLAGS

flags.DEFINE_integer('year', 2019, 'Year to use.')
flags.DEFINE_integer('max_distance', 250, 'Number of kilometers.')
flags.DEFINE_integer('divisions', 4, 'Divide the grid by this each time.')
flags.DEFINE_integer('min_count', 20, 'Only consider regions with at least this many.')
flags.DEFINE_integer('min_lat', -90, 'min latitude')
flags.DEFINE_integer('max_lat', 90, 'max latitude')
flags.DEFINE_integer('min_lon', -180, 'min longitude')
flags.DEFINE_integer('max_lon', 180, 'max longitude')

NOT_NEAR = 0
NEAR_REGION = 1
NEAR_CENTER = 2

class Region(object):
  def __init__(self, min_lat, max_lat, min_lon, max_lon):
    self.min_lat = min_lat
    self.max_lat = max_lat
    self.min_lon = min_lon
    self.max_lon = max_lon
    self.possible_pts = []
    self.actual_pts = []

  def divide(self, divisions, max_distance):
    out = []
    lat_size = (self.max_lat - self.min_lat) / divisions
    lon_size = (self.max_lon - self.min_lon) / divisions
    for i in range(divisions):
      for j in range(divisions):
        r = Region(self.min_lat + lat_size * i, self.min_lat + lat_size * (i + 1),
                   self.min_lon + lon_size * j, self.min_lon + lon_size * (j + 1))
        for pt in self.possible_pts:
          res = r.near_center(pt[0], pt[1], max_distance)
          if res == NEAR_CENTER:
            r.actual_pts += [pt]
            r.possible_pts += [pt]
          elif res == NEAR_REGION:
            r.possible_pts += [pt]
        out += [r]
    return out

  def diameter(self):
    return max(common.distance(self.min_lat, self.min_lon, self.max_lat, self.max_lon),
               common.distance(self.min_lat, self.max_lon, self.max_lat, self.min_lon))

  def near_center(self, lat, lon, max_distance):
    center_lat = (self.min_lat + self.max_lat) / 2
    center_lon = (self.min_lon + self.max_lon) / 2
    d = common.distance(lat, lon, center_lat, center_lon)
    if d < max_distance:
      return NEAR_CENTER
    elif d < max_distance + self.diameter() / 2:
      return NEAR_REGION
    else:
      return NOT_NEAR

def main(argv):
  cursor = db.cursor()
  cursor.execute('SELECT latitude, longitude FROM Competitions WHERE year = ' + str(FLAGS.year) + ' AND NOT cancelled')
  all_competitions = [[row[0] / 1e6, row[1] / 1e6] for row in cursor.fetchall()]

  initial_region = Region(FLAGS.min_lat, FLAGS.max_lat, FLAGS.min_lon, FLAGS.max_lon)
  initial_region.possible_pts = all_competitions

  best_region = None
  best_possible = 0
  best_actual = 0

  candidates = [initial_region]
  while candidates:
    r = candidates.pop(0)
    print('Considering [%.02f, %.02f, %.02f, %.02f] (d=%.02f) with [%d, %d]' % (r.min_lat, r.max_lat, r.min_lon, r.max_lon, r.diameter(), len(r.possible_pts), len(r.actual_pts)))
    if len(r.possible_pts) < best_actual:
      continue
    if len(r.possible_pts) == len(r.actual_pts):
      print('Done')
      continue
    for r2 in r.divide(FLAGS.divisions, FLAGS.max_distance):
      if len(r2.actual_pts) > best_actual or (len(r2.actual_pts) == best_actual and len(r2.possible_pts) < best_possible):
        print('New best [%.02f, %.02f, %.02f, %.02f] with [%d, %d]' % (r2.min_lat, r2.max_lat, r2.min_lon, r2.max_lon, len(r2.possible_pts), len(r2.actual_pts)))
        best_region = r2
        best_possible = len(r2.possible_pts)
        best_actual = len(r2.actual_pts)
      if len(r2.possible_pts) > max(best_actual, FLAGS.min_count):
        candidates += [r2]
  print('Best [%.04f, %.04f, %.04f, %.04f] [%.04f, %.04f] with [%d, %d]' %
        (best_region.min_lat, best_region.max_lat,
         best_region.min_lon, best_region.max_lon,
         (best_region.max_lat + best_region.min_lat) / 2,
         (best_region.max_lon + best_region.min_lon) / 2,
         len(best_region.possible_pts), len(best_region.actual_pts)))
  


if __name__ == '__main__':
  app.run(main)

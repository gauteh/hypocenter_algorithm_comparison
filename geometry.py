#! /usr/bin/python
#
# author: Gaute Hope <eg@gaute.vetsj.com> / 2014-06-09
#
# Coordinate and projections of geometry
#

import sys, os

sys.path.append ('/home/gaute/dev/nersc/acoustic_processing/')
from utils.coordinates import * # from acoustic_processing (nersc)

import logging as ll

import numpy as np
import scipy as sc

from pyproj import Geod
g = Geod (ellps = 'WGS84')

class Geometry:
  def __init__ (self, reference, stations, earthquake, velocities):
    ll.info ("geometry: setting up..")
    self.reference = reference
    self.stations  = stations
    self.earthquake = earthquake
    self.velocities = velocities

    self.calculate_distances ()
    self.calculate_degrees ()
    self.assert_degree_distances ()

  def calculate_distances (self):
    ## figure out distances between earthquakes to stations
    self.distances = []
    for s in self.stations:
      #_a, _b, dist = g.inv (s[0], s[1], e[0], e[1])

      dist = np.linalg.norm(np.array(self.earthquake[:2]) - np.array(s[1:3]))
      self.distances.append (dist)

    ll.info ("=> distances: " + str(self.distances))

  def assert_degree_distances (self):
    pass

  def calculate_degrees (self):
    """ calculate station positions in degrees as offset km from reference point """

    # azimuths: direction of vectors is used as azimuth
    #           since the reference point is set to be in
    #           coordinates 0, 0.

    ll.debug ("=> calulcating station positions in degrees..")
    self.stationsd = []
    for s in self.stations:
      d  = np.linalg.norm(np.array(s[1:3]))
      az = np.arctan2(s[1], s[2]) * 180 / np.pi
      ll.debug ("{}: {}, azimuth: {}, distance: {}".format(s[0], s[1:3], az, d))

      lon, lat, backaz = g.fwd (self.reference[0], self.reference[1], az, d * 1000.0)
      self.stationsd.append ([s[0], lon, lat, s[3]])

    ll.info ("=> stations (deg):")
    for s in self.stationsd:
      ll.info ("  {}: {}, {}, {}".format(*s))



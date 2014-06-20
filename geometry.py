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

  def calculate_degrees (self):
    pass

  def assert_degree_distances (self):
    pass

  def stations_degrees (self):
    """ calculate station positions in degrees as offset km from reference point """
    pass


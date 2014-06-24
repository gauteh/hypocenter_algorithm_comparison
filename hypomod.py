#! /usr/bin/python
#
# author: Gaute Hope <eg@gaute.vetsj.com> / 2014-06-09
#
# Class for interfacing with HYPOMOD (forward modelling for HYPOSAT)
#

import os, sys
import numpy as np
import scipy as sc

import logging as ll

from subprocess import check_call, check_output

sys.path.append ('/home/gaute/dev/nersc/acoustic_processing/')
from utils.coordinates import *

class Hypomod:
  def __init__ (self, outdir, geometry):
    ll.info ("== setting up HYPOMOD")
    self.outdir = outdir
    self.bin    = 'hypomod'

    self.geometry   = geometry
    self.velocity   = geometry.velocities
    self.stations   = geometry.stations
    self.earthquake = geometry.earthquake

    self.create_parameter_file ()
    self.create_velocity_file ()
    #self.create_input_file ()
    self.create_stations_file ()

  def create_parameter_file (self):
    ll.debug ("hypomod: creating parameter file..: hyposat-parameter")
    with open (os.path.join (self.outdir, 'hyposat-parameter'), 'w') as pfd:
      # write standard parameters. note that these are tuned
      # for the test case this program was created for: local earthquakes with
      # small array.
      pfd.write ('''\
  hyposat-parameter

GLOBAL MODEL                       : iasp91
**GLOBAL MODEL                       : ak135

LOCAL OR REGIONAL MODEL            : regional.vmod
PHASE INDEX FOR LOCAL MODEL        : 3333
CRUST 5.1                          : 0
CRUST 5.1 PATH                     : /nice/disk2/SOFTWARE/HYPOSAT/data/

OUTPUT OF REGIONAL MODEL (DEF 0)   : 0

STATION FILE                       : ./stations.dat
STATION CORRECTION FILE            : _

P-VELOCITY TO CORRECT ELEVATION    : 4
S-VELOCITY TO CORRECT ELEVATION    : 3.3

RG GROUP-VELOCITY (DEF 2.5  [km/s]): 2.5
LG GROUP-VELOCITY (DEF 3.5  [km/s]): 3.5752

LQ GROUP-VELOCITY (DEF 4.4  [km/s]):  4.4
LR GROUP-VELOCITY (DEF 3.95 [km/s]):  3.95

STARTING SOURCE TIME (EPOCHAL TIME): 0.
STARTING TIME ERROR       [s]      : 0.

STARTING SOURCE DEPTH     [km]     : 5.000
DEPTH FLAG (f,b,d,F,B,D)           : f

STARTING SOURCE LATITUDE  [deg]    : 89.87
STARTING LATITUDE ERROR   [deg]    : 0.001

STARTING SOURCE LONGITUDE [deg]    : 135.0
STARTING LONGITUDE ERROR  [deg]    : 0.001

MAGNITUDE CALCULATION (DEF 0)      : 0
P-ATTENUATION MODEL (G-R or V-C)   : V-C
S-ATTENUATION MODEL (IASPEI or R-P): R-P

MAXIMUM # OF ITERATIONS            : 60
# TO SEARCH OSCILLATIONS (DEF 4)   : 6

LOCATION ACCURACY [km] (DEFAULT 1) : 0.5
CONSTRAIN SOLUTION (0/1)           : 0

CONFIDENCE LEVEL  (68.3 - 99.99 %) : 95.
EPICENTER ERROR ELLIPSE (DEF 1)    : 1

MAXIMUM AZIMUTH ERROR     [deg]    : 20.
MAXIMUM SLOWNESS ERROR    [s/deg]  : 2.

SLOWNESS [S/DEG] ( 0 = APP. VEL)   : 1

FLAG USING TRAVEL-TIME DIFFERENCES : 1

INPUT FILE NAME (DEF hyposat-in)   : _

OUTPUT FILE NAME (DEF hyposat-out) : _
OUTPUT SWITCH  (YES = 1, DEFAULT)  : 1
OUTPUT LEVEL                       : 4
'''
      )

  def create_velocity_file (self):
    # set up velocity model
    ll.debug ("hypomod: create velocity model file..: regional.vmod")

    # skip doubles unless MOHO or CONR
    vels = []
    for v in self.velocity:
      if len(vels) > 0 and vels[-1][0] == v[0] and (vels[-1][3] != 'MOHO' and vels[-1][3] != 'CONR'):
        vels[-1] = v
      else:
        vels.append (v)

    with open (os.path.join (self.outdir, 'regional.vmod'), 'w') as vfd:
      vfd.write ("20.\n") # maximum distance [deg] to use this model in free format
      for v in vels:
        if v[3] == 'MOHO':
          layer = "MOHO"
        elif v[3] == 'CONR':
          layer = "CONR"
        else:
          layer = ""
        vfd.write ("{0:>10.3f}{1:>10.4f}{2:>10.4f}{3}\n".format(v[0], v[1], v[2], layer))

      # this follows the format:
      """
20.                                    | maximum distance [deg] to use this model in free format
     0.000    1.5000    1.5000         | depth [km], vp, vs [km/s] in format (3F10.3)
     3.000    5.8000    3.2000
    20.000    5.8000    3.2000CONR     |  "   + mark for the 'Conrad'
    20.000    6.5000    3.6000                       in format (3F10.3,A4)
    30.000    6.8000    3.9000MOHO     |  "   + mark for the 'Moho'
    30.000    8.1000    4.5000
    77.500    8.0500    4.4000
   120.000    8.1000    4.5000
      """

  def create_stations_file (self):
    # set up stations
    ll.debug ("hypomod: create stations file..")
    with open (os.path.join (self.outdir, 'stations.dat'), 'w') as sfd:
      for s in self.geometry.stationsd:
        lon = decimaldegree_ddmmss (abs(s[1])) + 'E' if s[1] >= 0 else 'W'
        lat = decimaldegree_ddmmss (abs(s[2])) + 'N' if s[2] >= 0 else 'S'
        sfd.write ("{0:<6s}{1:>8} {2:>8} {3:6.1f}\n".format(s[0], lat, lon, s[3]))


  def calculate_times (self):
    out = check_output ("hypomod", cwd = self.outdir, shell = True)
    out = out.decode ('ascii')

  """
  def create_input_file (self):
    # set up stations
    ll.debug ("hypomod: create input file..")
    with open (os.path.join (self.outdir, 'hyposat-in'), 'w') as ifd:
      pass
  """




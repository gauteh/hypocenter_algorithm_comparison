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

    self.set_geometry (geometry)

  def set_geometry (self, geometry):
    self.geometry   = geometry
    self.velocity   = geometry.velocities
    self.stations   = geometry.stations
    self.earthquake = geometry.earthquake

    self.create_parameter_file ()
    self.create_velocity_file ()
    self.create_input_file ()
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

STARTING SOURCE DEPTH     [km]     : {depth:.4f}
DEPTH FLAG (f,b,d,F,B,D)           : f

STARTING SOURCE LATITUDE  [deg]    : {lat:<.3f}
STARTING LATITUDE ERROR   [deg]    : 0.001

STARTING SOURCE LONGITUDE [deg]    : {lon:<.3f}
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
'''.format (lon = self.geometry.earthquaked[0], lat = self.geometry.earthquaked[1], depth = -self.geometry.earthquaked[2])
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
        lon = decimaldegree_ddmmss (s[1], 'E')
        lat = decimaldegree_ddmmss (s[2], 'N')

        llon = ""
        k = 0
        while k < lon.find('.')-1:
          if lon[k] == '0':
            llon += " "
          else:
            break
          k += 1

        llon += lon[k:]
        lon = llon

        llat = ""
        k = 0
        while k < lat.find('.')-1:
          if lat[k] == '0':
            llat += " "
          else:
            break
          k += 1

        llat += lat[k:]
        lat = llat

        sfd.write ("{0:<5s} {1:>9}{2:>10} {3:6.1f}\n".format(s[0], lat, lon, s[3]))

  def calculate_times (self):
    ll.info ("=> hypomod: running HYPOMOD..")
    check_output ("hypomod", cwd = self.outdir, shell = True)

    return self.parse_times ()

  def parse_times (self):
    ll.debug ("=> hypomod: parsing result..")
    stationlines = []
    with open(os.path.join (self.outdir, 'hypomod-out'), 'r') as ofd:
      start = False
      for l in ofd.readlines ():
        if 'Stat' in l:
          start = True
          continue

        if start:
          if 'Travel-time differences:' in l:
            break
          elif len(l.strip ()) > 0:
            stationlines.append (l)

    stationlines = [[k.strip() for k in l.split (' ') if len(k.strip()) > 0] for l in stationlines]

    ttimes = []
    for s in self.stations:
      pht = []
      for l in (ll for ll in stationlines if ll[0] == s[0]):
        # station name, phase name, ttime
        pht.append ([s[0], l[3], -float(l[8])])
      ttimes.append (pht)

    return ttimes

  def create_input_file (self):
    # set up stations
    ll.debug ("hypomod: create input file..")
    with open (os.path.join (self.outdir, 'hyposat-in'), 'w') as ifd:
      # write header
      ifd.write ("HYP_ALG_COMPARE_TEST\n")
      for s in self.stations:
        # phases are hard coded
        for ph in ['P', 'S']:
          ifd.write ("{:<5} {}        1970 01 01 00 00 00.000 0.000 -999.0 00.0 -999.0  0.00 T__D__\n".format (s[0], ph))

''' the format of the hyposat-in files are, we set all interesting
    phases to unix time 0. the residual should then be the traveltime:
03-2300-00L.S201209_JOB_ID_02
GAK2  P        1970 01 01 00 00 04.390 0.000 -999.0 00.0 -999.0  0.00 T__D__
GAK2  S        1970 01 01 00 00 06.230 0.000 -999.0 00.0 -999.0  0.00 T__D__
GAK4  P        1970 01 01 00 00 03.200 0.000 -999.0 00.0 -999.0  0.00 T__D__
GAK4  S        1970 01 01 00 00 04.080 0.000 -999.0 00.0 -999.0  0.00 T__D__
GAK3  P        1970 01 01 00 00 03.890 0.000 -999.0 00.0 -999.0  0.00 T__D__
GAK3  S        1970 01 01 00 00 05.320 0.000 -999.0 00.0 -999.0  0.00 T__D__
'''




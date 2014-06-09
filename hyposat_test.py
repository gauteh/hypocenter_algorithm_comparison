#! /usr/bin/python
#
# author: Gaute Hope <eg@gaute.vetsj.com> / 2014-06-07
#
# Test hyposat output vs. hypocenter and TauP for given
# setup.
#
#
# Requirements:
# - numpy and scipy
# - HYPOSAT     (as provided by SEISAN)
# - HYPOMOD     (as provided by SEISAN) (forward modelling for HYPOSAT)
# - HYPOCENTER  (as provided by SEISAN)
# - TTLAYER     (as provided by SEISAN) (forward modelling for HYPOCENTER)
# - TauP
#

## This program will set up a test geometry of stations and
## a earthquake. Synthetic traveltimes will then be generated
## using the forward modelling packages for HYPOSAT, HYPOCENTER
## and TauP.
##
## Arbitrary input geometries may be specified, but the parameters for the
## solvers are tweaked for local stations and earthquakes (
## ~10-30 km distances) and relatively shallow depths (~ 5-10 km).


import os, sys
import argparse

import numpy as np
import scipy as sc

from subprocess import check_call

from taup_time import *

from pyproj import Geod
g = Geod (ellps = 'WGS84')

parser = argparse.ArgumentParser (description = "Test HYPOSAT against the HYPOCENTER and TauP packages (author: Gaute Hope <eg@gaute.vetsj.com> / 2014-06-07)")

parser.add_argument ('-g', '--geometry', default = 'geometry_setup.job',
    help = 'Geometry of stations and earthquake position, see sample geometry_setup.job')
parser.add_argument ('-v', '--vel', default = 'vel.csv',
    help = 'Input velocity model for P and S velocity (depth,velp,vels in km), see sample vel.csv.')
parser.add_argument ('-o', '--out', default = 'out',
    help = 'Output directory for plots, reports and generated files.')

parser.add_argument ("-pf", "--phase-file", default = 'phases.dat',
    help = "File with list of phases.")

args = parser.parse_args ()
outdir      = args.out
geometry    = args.geometry
vel         = args.vel
phasef      = args.phase_file

## Output
print ("output directory: %s" % outdir)

# do a few simple sanity checks..
for f in [geometry, vel, phasef]:
  if not os.path.exists (f):
    print ("could not find input file: %s" % f)
    sys.exit (1)

if not os.path.exists (outdir):
  print ("creating outdir..")
  os.makedirs (outdir, exist_ok = True)

if not os.path.isdir (outdir):
  print ("output directory is not a directory.")
  sys.exit (1)

## Set up geometry from input
print ("loading geometry: %s.." % geometry)
reference   = None
stations    = []
earthquake  = []

with open(geometry, 'r') as fd:
  for l in fd.readlines ():
    l = l.strip()
    if len(l) > 0 and l[0] != "#":
      s = l.split (',')
      if s[0] == "R":
        if reference is not None:
          print ("=> reference already set")
          sys.exit (1)
        else:
          reference = [float(s[2]), float(s[3])]

      elif s[0] == "S":
        stations.append ( [s[1], float(s[2]), float(s[3]), float(s[4])] )

      elif s[0] == "E":
        earthquake =  [float(s[1]), float(s[2]), float(s[3])]

if reference is None:
  print ("=> no reference specified.")
  sys.exit (1)

if len(stations) == 0:
  print ("=> no stations specified.")
  sys.exit (1)

if len(earthquake ) == 0:
  print ("=> no earthquake  specified.")
  sys.exit (1)

print ("=> reference: %f, %f" % (reference[0], reference[1]))
print ("=> stations (km):")
for s in stations:
  print ("  {}: {}, {}, {}".format(*s))

print ("=> earthquake: {}, {}, {}".format(*earthquake))

## Load velocity model
print ("loading velocity model: %s.. (km and km/s)" % vel)
velocity = []
with open(vel, 'r') as fd:
  for l in fd.readlines():
    l = l.strip()
    if len(l) > 0 and l[0] != "#":
      s = [ss.strip() for ss in l.split (',')]
      velocity.append ( [float(s[0]), float(s[1]), float(s[2]), s[3]] )

for l in velocity:
  print ("  depth: {:>4}, velp: {:>5}, vels: {:>5} ({})".format(*l))

## figure out distances between earthquakes to stations
distances = []
for s in stations:
  #_a, _b, dist = g.inv (s[0], s[1], e[0], e[1])

  dist = np.linalg.norm(np.array(earthquake[:2]) - np.array(s[1:3]))
  distances.append (dist)

print ("=> distances: " + str(distances))

print ("== setting up TauP")
print ("=> generate velocity model for TauP..: taup_regional.nd")

taup_vel_a = os.path.join (outdir, "taup_regional.nd")
with open (taup_vel_a, 'w') as fd:
  for v in velocity:
    fd.write ("%1.1f %1.1f %1.1f\n" % (v[0], v[1], v[2]))
    if v[3] == "seafloor":
      fd.write ("seafloor\n")
    elif v[3] == "MOHO":
      fd.write ("mantle\n")

# generate taup model
check_call ("taup_create -nd taup_regional.nd", cwd = outdir, shell = True)

## Calculate traveltimes using TauP
t = TauPTime (outdir, "taup_regional.nd", "../phases.dat", stations,
              earthquake)

taup_times = t.calculate_times ()

## write out traveltimes from TauP
taup_ttimes_f = os.path.join (outdir, "taup_ttimes.dat")
with open(taup_ttimes_f, 'w') as fd:
  for s, tt in zip(stations, t.times):
    for ph in tt:
      fd.write ("{station},{phase},{time},{distance}\n".format(
                station = s[0], phase = ph[0], time = ph[1],
                distance = ph[2]))





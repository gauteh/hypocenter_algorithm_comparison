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
## solvers are tweaked for local stations and earthquakes (~10-30 km distances)


import os, sys
import argparse

parser = argparse.ArgumentParser (description = "Test HYPOSAT against the HYPOCENTER and TauP packages (author: Gaute Hope <eg@gaute.vetsj.com> / 2014-06-07)")

parser.add_argument ('-g', '--geometry', default = 'geometry_setup.job',
    help = 'Geometry of stations and earthquake position, see sample geometry_setup.job')
parser.add_argument ('-v', '--vel', default = 'vel.csv',
    help = 'Input velocity model for P and S velocity (depth,velp,vels in meters), see sample vel.csv.')
parser.add_argument ('-o', '--out', default = 'out',
    help = 'Output directory for plots, reports and generated files.')

parser.add_argument ("-nt", "--skip-generate-taup-times", action = 'store_false', dest = 'taup_generate',
    help = "Provide TauP times manually, useful in case you don't have TauP installed" )

args = parser.parse_args ()
outdir      = args.out
geometry    = args.geometry
vel         = args.vel

## Output
print ("output directory: %s" % outdir)

# do a few simple sanity checks..
for f in [geometry, vel]:
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
earthquakes = []

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
        earthquakes.append ( [s[1], float(s[2]), float(s[3]), float(s[4])] )

if reference is None:
  print ("=> no reference specified.")
  sys.exit (1)

if len(stations) == 0:
  print ("=> no stations specified.")
  sys.exit (1)

if len(earthquakes) == 0:
  print ("=> no earthquakes specified.")
  sys.exit (1)

print ("=> reference: %f, %f" % (reference[0], reference[1]))
print ("=> stations:")
for s in stations:
  print ("  {}: {}, {}, {}".format(*s))

print ("=> earthquakes:")
for e in earthquakes:
  print ("  {}: {}, {}, {}".format(*e))

## Load velocity model
print ("loading velocity model: %s.." % vel)

if args.taup_generate:
  print ("generating taup times..")


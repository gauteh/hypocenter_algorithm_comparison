#! /usr/bin/python
#
# author: Gaute Hope <eg@gaute.vetsj.com> / 2014-06-07
#
# Test hyposat output vs. hypocenter and TauP for given
# setup.
#
## This program will set up a test geometry of stations and
## a earthquake. Synthetic traveltimes will then be generated
## using the forward modelling packages for HYPOSAT, HYPOCENTER
## and TauP.
##
## Arbitrary input geometries may be specified, but the parameters for the
## solvers are tweaked for local stations and earthquakes (
## ~10-30 km distances) and relatively shallow depths (~ 5-10 km).
##
## Currently only HYPOSAT and TauP interfaces are completed.
##


import os, sys
import argparse
import logging as ll

import numpy as np
import scipy as sc

from subprocess import check_call

from taup       import *
from hypomod    import *
from ttlayer    import *
from geometry   import *

parser = argparse.ArgumentParser (description = "Test HYPOSAT against the HYPOCENTER and TauP packages (author: Gaute Hope <eg@gaute.vetsj.com> / 2014-06-07)")

parser.add_argument ('-g', '--geometry', default = 'geometry_setup.job',
    help = 'Geometry of stations and earthquake position, see sample geometry_setup.job')
parser.add_argument ('-v', '--vel', default = 'vel.csv',
    help = 'Input velocity model for P and S velocity (depth,velp,vels in km), see sample vel.csv.')
parser.add_argument ('-o', '--out', default = 'out',
    help = 'Output directory for plots, reports and generated files.')

parser.add_argument ("-pf", "--phase-file", default = 'phases.dat',
    help = "File with list of phases.")


## Output
rootLogger = ll.getLogger()
rootLogger.setLevel (ll.DEBUG)

logFormatter = ll.Formatter("[%(levelname)-5.5s] %(message)s")
consoleHandler = ll.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

class HyComp:
  def __init__ (self, outdir, geometryf, vel, phasef):
    ll.info ("output directory: %s" % outdir)

    self.outdir     = outdir
    self.geometryf  = geometryf
    self.vel        = vel
    self.phasef     = phasef

    # do a few simple sanity checks..
    for f in [geometryf, vel, phasef]:
      if not os.path.exists (f):
        ll.error ("could not find input file: %s" % f)
        sys.exit (1)

    if not os.path.exists (outdir):
      ll.warn ("creating outdir..")
      os.makedirs (outdir, exist_ok = True)

    if not os.path.isdir (outdir):
      ll.error ("output directory is not a directory.")
      sys.exit (1)

    logFormatter = ll.Formatter("%(asctime)s [%(levelname)-5.5s] %(message)s")
    fileHandler = ll.FileHandler("{0}/log".format(outdir))
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    version = VERSION if ('VERSION' in locals()) else check_output("git describe --always --tags --abbrev=8", shell = True).decode('ascii').strip()
    ll.info ("hypocenter algorithm comparison: version: %s" % version)

    ## Set up geometry from input
    ll.info ("loading geometry: %s.." % geometryf)
    reference   = None
    stations    = []
    earthquake  = []

    with open(geometryf, 'r') as fd:
      for l in fd.readlines ():
        l = l.strip()
        if len(l) > 0 and l[0] != "#":
          s = l.split (',')
          if s[0] == "R":
            if reference is not None:
              ll.debug ("=> reference already set")
              sys.exit (1)
            else:
              reference = [float(s[2]), float(s[3])]

          elif s[0] == "S":
            stations.append ( [s[1], float(s[2]), float(s[3]), float(s[4])] )

          elif s[0] == "E":
            earthquake =  [float(s[1]), float(s[2]), float(s[3])]

    if reference is None:
      ll.error ("=> no reference specified.")
      sys.exit (1)

    if len(stations) == 0:
      ll.error ("=> no stations specified.")
      sys.exit (1)

    if len(earthquake ) == 0:
      ll.error ("=> no earthquake  specified.")
      sys.exit (1)

    ll.info ("=> reference: %f, %f" % (reference[0], reference[1]))

    ll.info ("=> stations (km):")
    for s in stations:
      ll.info ("  {}: {}, {}, {}".format(*s))

    ll.info ("=> earthquake: {}, {}, {}".format(*earthquake))

    ## Load velocity model
    ll.info ("loading velocity model: %s.. (km and km/s)" % vel)
    velocity = []
    with open(vel, 'r') as fd:
      for l in fd.readlines():
        l = l.strip()
        if len(l) > 0 and l[0] != "#":
          s = [ss.strip() for ss in l.split (',')]
          velocity.append ( [float(s[0]), float(s[1]), float(s[2]), s[3]] )

    for l in velocity:
      ll.info ("  depth: {:>4}, velp: {:>5}, vels: {:>5} ({})".format(*l))

    self.geometry = Geometry (reference, stations, earthquake, velocity)

  def calculate_ttimes (self, regen_velocity = True):
    ## Calculate traveltimes using TauP
    self.taup = TauP (self.outdir, self.geometry, os.path.abspath(self.phasef), regen_velocity)

    self.taup_ttimes = self.taup.calculate_times ()

    ## write out traveltimes from TauP
    taup_ttimes_f = os.path.join (self.outdir, "taup_ttimes.dat")
    with open(taup_ttimes_f, 'w') as fd:
      for ph in self.taup.times:
        fd.write ("{station},{phase},{time},{distance}\n".format(
                  station = ph[0], phase = ph[1], time = ph[2],
                  distance = ph[3]))

    ## set up HYPOMOD
    self.hypomod = Hypomod (self.outdir, self.geometry)
    self.hypomod_ttimes = self.hypomod.calculate_times ()

    ### set up TTLAYER
    #self.ttlayer = TTlayer (self.outdir, self.geometry)

if __name__ == '__main__':
  args        = parser.parse_args ()
  outdir      = args.out
  geometry    = args.geometry
  vel         = args.vel
  phasef      = args.phase_file

  hc = HyComp (outdir, geometry, vel, phasef)
  hc.calculate_ttimes ()


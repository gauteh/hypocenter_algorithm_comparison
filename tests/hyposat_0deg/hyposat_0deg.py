#! /usr/bin/python
#
# author: Gaute Hope <eg@gaute.vetsj.com> / 2014-06-07
#
# Test hypomod output vs. TauP for a range of distances.
#
## Set up a range of distances, starting from close < 1km to 100 km
## epicentral distance and calculate traveltimes using HYPOMOD and
## TauP.

import os, sys
import logging as ll

import numpy as np
import scipy as sc

import matplotlib.pyplot as plt

from subprocess import check_call, TimeoutExpired

sys.path.append (os.path.abspath('.'))
sys.path.append (os.path.abspath('..'))
sys.path.append (os.path.abspath('../..'))

from hyp_alg_comp   import *
from taup           import *
from hypomod        import *
from ttlayer        import *
from geometry       import *

phasef      = 'phases.dat'         # only used by TauP
velf        = 'vel.csv'
geometryf   = 'geometry_setup.job' # only used for initial setup

# set up HyComp
hyc = HyComp ('out', geometryf, velf, phasef)

eq = np.array([10., 2., -80.])
sta = [['STA', 10., 10., 0] ]

reference   = hyc.geometry.reference
velocities  = hyc.geometry.velocities

case = 1

ll.info ('**=> testing %d: station with latitude: %f' % (case, sta[0][2]))
hyc.geometry.setup (reference, sta, eq, velocities)
hy = Hypomod (hyc.outdir, hyc.geometry)
ttimes = hy.calculate_times ()

ll.info ('**=> done.')
case = case + 1
print (ttimes)

sta = [['STA', 0., 11., 0] ]
eq = np.array([0., 5., -80.])
ll.info ('**=> testing %d: equal longitude = 0, station with latitude: %f' % (case, sta[0][2]))
hyc.geometry.setup (reference, sta, eq, velocities)
hy = Hypomod (hyc.outdir, hyc.geometry)
ttimes = hy.calculate_times ()

ll.info ('**=> done.')
case = case + 1
print (ttimes)

sta = [['STA', 1., 0., 0] ]
eq = np.array([1., 1., -80.])
ll.info ('**=> testing %d: equal longitude = 1, station with latitude: %f' % (case, sta[0][2]))
hyc.geometry.setup (reference, sta, eq, velocities)
hy = Hypomod (hyc.outdir, hyc.geometry)
ttimes = hy.calculate_times ()

ll.info ('**=> done.')
case = case + 1
print (ttimes)

sta = [['STA', 12., 1., 0] ]
eq = np.array([10., 1., -80.])
ll.info ('**=> testing %d: equal latitude = 1, station with latitude: %f' % (case, sta[0][2]))
hyc.geometry.setup (reference, sta, eq, velocities)
hy = Hypomod (hyc.outdir, hyc.geometry)
ttimes = hy.calculate_times ()

ll.info ('**=> done.')
case = case + 1
print (ttimes)


# apparentely latitude 0N for both station and eq results in an infinite loop
sta = [['STA', 12., 0., 0] ]
eq = np.array([10., 0., -80.])
ll.info ('**=> testing %d: equal latitude = 0, station with latitude: %f' % (case, sta[0][2]))
hyc.geometry.setup (reference, sta, eq, velocities)
hy = Hypomod (hyc.outdir, hyc.geometry)
to = 10.
ll.info ('timeout: %f' % to)
try:
  ttimes = hy.calculate_times (timeout = to)
  ll.info ('**=> done.')
  print (ttimes)
except TimeoutExpired:
  ll.error ('**=> hypomod timed out, infinite loop?')

case = case + 1


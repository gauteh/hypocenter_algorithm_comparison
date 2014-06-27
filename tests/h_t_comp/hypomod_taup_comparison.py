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

from subprocess import check_call

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

## set up range to test
s0 = 0.0   # km, start
s1 = 100.1 # km, stop
ds = 50.0  # km, delta

direction = np.array([0., 1.0]) # to move station

eq = np.array([10.0, 10., -20.])

reference   = hyc.geometry.reference
velocities  = hyc.geometry.velocities

distances = []
ptimes    = []
stimes    = []

for d in np.arange (s0, s1, ds):
  ll.info ("compare: testing distance {}..".format (d))

  sta = np.zeros((1,3))
  sta[0,:2] = d * direction + eq[:2]
  sta = sta.ravel()

  # assert distance
  dist = np.linalg.norm(eq[:2] - sta[:2])
  np.testing.assert_equal (dist, d)
  sta = [['STA', sta[0], sta[1], sta[2]]]
  ll.debug (" => station: {}".format (sta))

  ll.debug (" => setting up geometry..")
  hyc.geometry.setup (reference, sta, eq, velocities)

  hyc.calculate_ttimes ()

  taup_times = hyc.taup_ttimes
  hypomod_times = hyc.hypomod_ttimes

  distances.append (d)

  try:
    pt = float(next(t[2] for t in taup_times if t[1] == 'p'))
  except:
    pt = np.nan

  ptimes.append ([pt, hypomod_times[0][0][2]])

  try:
    st = float(next(t[2] for t in taup_times if t[1] == 's4.6p'))
  except:
    st = np.nan

  stimes.append ([st, hypomod_times[0][1][2]])

distances = np.array(distances)
ptimes    = np.array(ptimes)
stimes    = np.array(stimes)

print (distances)
print (ptimes)
print (stimes)

## plot travel times
plt.figure (1)
plt.clf ()

plt.plot (distances, ptimes[:,0], label = 'TauP (P)')
plt.plot (distances, ptimes[:,1], label = 'Hypomod (P)')

plt.plot (distances, stimes[:,0], label = 'TauP (S)')
plt.plot (distances, stimes[:,1], label = 'Hypomod (S)')

plt.xlabel ('Distance [km]')
plt.ylabel ('Time [s]')
plt.title ('Travel time over distance')

plt.legend ()
plt.tight_layout ()

plt.show (False)
plt.savefig ('out/traveltimes.png')
ll.info ("=> traveltimes plotted in: out/traveltimes.png")

## save results
ll.info ("=> traveltimes saved to: out/traveltimes.csv")
data = np.concatenate ([distances.reshape((3,1)), ptimes, stimes], 1)
np.savetxt ('out/traveltimes.csv', data, '%f', delimiter = ',')


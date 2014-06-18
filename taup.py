#! /usr/bin/python
#
# author: Gaute Hope <eg@gaute.vetsj.com> / 2014-06-09
#
# Class for interfacing with taup_time
#


import os, sys
import numpy as np
import scipy as sc

import logging as ll

from subprocess import check_call, check_output

class TauP:
  times = []

  def __init__ (self, outdir, velocity, phasef, stations, earthquake):
    """
    Set up everything needed for running taup_time,
    file names are relative to outdir.
    """
    ll.info ("== setting up TauP")

    self.outdir     = outdir
    self.velocity   = velocity
    self.velf       = ""
    self.phasef     = phasef
    self.stations   = stations
    self.earthquake = earthquake

    self.create_velocity_model ()
    self.distances  = self.calculate_distances ()

  def create_velocity_model (self):
    ll.info ("=> generate velocity model for TauP..: taup_regional.nd")

    self.velf = os.path.join (self.outdir, "taup_regional.nd")
    with open (self.velf, 'w') as fd:
      for v in self.velocity:
        fd.write ("%1.1f %1.1f %1.1f\n" % (v[0], v[1], v[2]))
        if v[3] == "seafloor":
          fd.write ("seafloor\n")
        elif v[3] == "MOHO":
          fd.write ("mantle\n")

    # generate taup model
    check_output ("taup_create -nd taup_regional.nd", cwd = self.outdir, shell = True)

  def calculate_distances (self):
    ## figure out distances between earthquakes to stations
    distances = []
    for s in self.stations:
      #_a, _b, dist = g.inv (s[0], s[1], e[0], e[1])

      dist = np.linalg.norm(np.array(self.earthquake[:2]) - np.array(s[1:3]))
      distances.append (dist)

    return distances

  def calculate_times (self):
    self.times = []
    for s,d in zip(self.stations, self.distances):
      self.times.append (self.calculate_time (s, d))

    return self.times


  def calculate_time (self, station, dist):
    ll.info ("taup: calculating travel times for: {}".format(station[0]))


    cmd = "taup_time -mod {vel} -h {depth} -km {dist} -pf {pf}".format (
           vel = os.path.basename(self.velf).replace (".nd", ""), depth = -self.earthquake[2],
           dist = dist, pf = self.phasef)


    out = check_output (cmd, cwd = self.outdir, shell = True)
    out = out.decode ('ascii')

    out = out.splitlines ()
    out = out[5:]

    ph = []
    for l in out:
      if len(l.strip()) > 0:
        ph.append (self.parse_phase (l))

    return ph

  def parse_phase (self, ph):
    """
    parse a phase line
    """

    l = ph.split ()
    dist = l[0] # in degrees
    name = l[2]
    time = l[3]

    return [name, time, dist]






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
  times = None

  def __init__ (self, outdir, geometry, phasef):
    """
    Set up everything needed for running taup_time,
    file names are relative to outdir.
    """
    ll.info ("== setting up TauP")

    self.outdir     = outdir
    self.phasef     = phasef
    self.set_geometry (geometry)

  def set_geometry (self, geometry, regen_velocity = True):
    self.geometry   = geometry
    self.velocity   = geometry.velocities
    self.velf       = ""
    self.stations   = geometry.stations
    self.earthquake = geometry.earthquake

    if regen_velocity:
      self.create_velocity_model ()

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

  def calculate_times (self):
    self.times = []
    for s,d in zip(self.stations, self.geometry.distances):
      for ph in self.calculate_time (s, d):
        self.times.append (ph)

    return self.times


  def calculate_time (self, station, dist):
    ll.info ("taup: calculating travel times for: {}".format(station[0]))


    cmd = "taup_time -mod {vel} -h {depth} -km {dist:.3f} -pf {pf}".format (
           vel = os.path.basename(self.velf).replace (".nd", ""), depth = -self.earthquake[2],
           dist = dist, pf = self.phasef)

    #print (cmd)

    out = check_output (cmd, cwd = self.outdir, shell = True)
    out = out.decode ('ascii')

    out = out.splitlines ()
    out = out[5:]

    ph = []
    for l in out:
      if len(l.strip()) > 0:
        p = self.parse_phase (l)
        p.insert (0, station[0])
        ph.append (p)

    return ph

  def parse_phase (self, ph):
    """
    parse a phase line
    """

    l = ph.split ()
    dist = l[0] # in degrees
    name = l[2]
    time = l[3]

    #print (time)

    return [name, time, dist]






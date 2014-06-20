#! /usr/bin/python
#
# author: Gaute Hope <eg@gaute.vetsj.com> / 2014-06-09
#
# Class for interfacing with TTLAYER
#

import os, sys
import numpy as np
import scipy as sc

import logging as ll

from subprocess import check_call, check_output

class TTlayer:
  def __init__ (self, outdir, geometry):
    ll.info ("== setting up TTlayer")
    self.outdir = outdir
    self.bin    = 'ttlayer'

    self.geometry   = geometry
    self.velocity   = geometry.velocities
    self.stations   = geometry.stations
    self.earthquake = geometry.earthquake

    self.create_input_file ()

  def create_input_file (self):
    ll.debug ("ttlayer: creating input file..")
    with open (os.path.join (self.outdir, 'mp.hyp'), 'w') as ifd:
      ll.debug ("ttlayer: ..set up standard parameters")
      # write standard parameters. note that these are tuned
      # for the test case this program was created for: local earthquakes with
      # small array.
      ifd.write ('''\
RESET TEST(02)=500.0
RESET TEST(07)=-3.0
RESET TEST(08)=2.6
RESET TEST(09)=0.001
RESET TEST(11)=99.0
RESET TEST(13)=5.0
RESET TEST(34)=1.5
RESET TEST(35)=2.5
RESET TEST(36)=0.0
RESET TEST(41)=20000.0
RESET TEST(43)=5.0
RESET TEST(51)=3.6
RESET TEST(50)=1.0
RESET TEST(56)= 1.0
RESET TEST(58)= 99990.0
RESET TEST(40)=0.0
RESET TEST(60)=0.0
RESET TEST(71)=1.0
RESET TEST(75)=1.0
RESET TEST(76)=0.910
RESET TEST(77)=0.00087
RESET TEST(78)=-1.67
RESET TEST(79)=1.0
RESET TEST(80)=3.0
RESET TEST(81)=1.0
RESET TEST(82)=1.0
RESET TEST(83)=1.0
RESET TEST(88)=1.0
RESET TEST(85)=0.1
RESET TEST(91)=0.1


'''
      )

      # set up velocity model
      ll.debug ("ttlayer: ..set up velocity model")

      # set up stations
      ll.debug ("ttlayer: ..set up station coordinates")




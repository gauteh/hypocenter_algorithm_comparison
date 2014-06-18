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

class Hypomod:
  def __init__ (self, outdir):
    self.outdir = outdir


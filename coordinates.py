#! /usr/bin/python
#
# Author: Gaute Hope <eg@gaute.vetsj.com> / 2012-11-27
#
# Coordinate utility functions

import math

def ddmm_mm_decimaldegree (s, d):
  # input:  8059.59
  # output: 80.9931667
  # s is decimalminute.fractionalminutes string
  # d is north/south or east/west indicator

  minu = float (s[s.find('.') -2:])
  deg  = float (s[:s.find ('.') - 2])

  deg += minu / 60.0

  if d == 'S' or d == 'W':
    deg *= -1.0

  return deg

def decimaldegree_ddmmss (s, dir = None):
  # input:  80.99, dir can be north or east (N or E)
  # output: 805835.4, direction is lost if dir is None
  sign  = 1 if s >= 0 else -1 
  s     = abs (s)
  deg   = math.floor (s)
  mint  = (s - deg) * 60.0
  min   = math.floor (mint)
  sec   = (mint - min) * 60.0

  if dir is None:
    r = '%02d%02d%04.1f' % (deg, min, sec)
  else:
    if dir == 'N':
      d = 'N' if sign > 0 else 'S'
      r = '%02d%02d%04.1f%s' % (deg, min, sec, d)
    elif dir == 'E':
      d = 'E' if sign > 0 else 'W'
      r = '%02d%02d%04.1f%s' % (deg, min, sec, d)
    else:
      raise ArgumentError ("unknown direction specifier")

  return r

def ddmmss_decimaldegree (s):
  # inverse of above
  s = s.replace (' ', '0') # space -> 0

  n = s.find ('.')
  sec = s[n -2:-1]
  d   = s[-1]
  min = s[n - 4: n - 2]
  deg = s[: n - 4]

  r  = float (deg)
  r += float (min) / 60.0
  r += float (sec) / 60.0 / 60.0

  if d == 'S' or d == 'W':
    r *= -1.0

  return r

# outputs degrees with decimal minutes, without
# decimal point and with three digits (suitable for hypocenter)
def decimaldegree_ddmm_mmm (s):
  deg   = math.floor (s)
  mint  = (s - deg) * 60.0
  min   = math.floor (mint)
  mind  = (mint - min) * 1000

  r = '%02d%02d%03d' % (deg, min, mind)

  return r

def dddCmm_mmmHl_decimaldegree (s):
  # input:  78�16.290'N or 014�40.090'E
  # output: 78.1231231 (or something)

  s = s.strip ()
  n = s.find ('.') # dec point

  if n == 5:
    # latitude (2 digits in degree)
    deg = s[0:2]
    mm  = s[3:-2]
  else:
    # longitude (3 digits in degree)
    deg = s[0:3]
    mm  = s[4:-2]

  return ddmm_mm_decimaldegree (deg + mm, s[-1])


def ddNEmm_mm_decimaldegree (s):
  # input: 82N32.322
  # output: decimal degrees

  s = s.strip()

  n = s.find('N')
  if n < 0:
    n = s.find ('S')

  if n < 0:
    n = s.find ('E')

  if n < 0:
    n = s.find ('W')

  if n < 0:
    raise ValueError ("No direction specifier.")

  dd = int(s[:n])
  dir = s[n]
  min = float(s[n+1:])

  ddmm_mmm = ("%02d%09.6f" % (dd, min))
  return ddmm_mm_decimaldegree (ddmm_mmm, dir)








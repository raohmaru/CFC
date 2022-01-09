# Python Scripts for the Card Fighters' Clash definition for OCTGN
# Copyright (C) 2019  Raohmaru

# This python script is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this script. If not, see <http://www.gnu.org/licenses/>.

import clr
clr.AddReference("System")
from System import Random

#---------------------------------------------------------------------------
# Random functions
# 
# Somehow, random module is not available in OCTGN, so this a custom implementation.
#---------------------------------------------------------------------------

from math import log as _log, ceil as _ceil

class RRRandom(Random):
   def random(self):
      """
      Get the next random number in the range [0.0, 1.0).
      https://docs.microsoft.com/en-us/dotnet/api/system.random.sample
      """
      return self.Sample()


   def randInt(self, a, b):
      """
      Return random integer in range [a, b], including both end points.
      """
      if b <= a:
         raise ValueError("second argument must be greater than the first")
      return int(round(a + self.Sample() * (b - a)))


   def choice(self, seq):
      """
      Choose a random element from a non-empty sequence.
      """
      return seq[int(self.random() * len(seq))]


   def sample(self, population, k):
      """
      Chooses k unique random elements from a population sequence.
      https://github.com/python/cpython/blob/2.7/Lib/random.py#L275
      """
      n = len(population)
      if not 0 <= k <= n:
         raise ValueError("sample larger than population")
      random = self.random
      _int = int
      result = [None] * k
      setsize = 21      # size of a small set minus size of an empty list
      if k > 5:
         setsize += 4 ** _ceil(_log(k * 3, 4)) # table size for big sets
      if n <= setsize or hasattr(population, "keys"):
         # An n-length list is smaller than a k-length set, or this is a
         # mapping type so the other algorithm wouldn't work.
         pool = list(population)
         for i in xrange(k):       # invariant:  non-selected at [0,n-i)
            j = _int(random() * (n-i))
            result[i] = pool[j]
            pool[j] = pool[n-i-1]   # move non-selected item into vacancy
      else:
         try:
            selected = set()
            selected_add = selected.add
            for i in xrange(k):
               j = _int(random() * n)
               while j in selected:
                  j = _int(random() * n)
               selected_add(j)
               result[i] = population[j]
         except (TypeError, KeyError):   # handle (at least) sets
            if isinstance(population, list):
               raise
            return self.sample(tuple(population), k)
      return result

#---------------------------------------------------------------------------

try:
   import random
except (IOError, ImportError):
   random = RRRandom()

# Python Scripts for the Card Fighters' Clash definition for OCTGN
# Copyright (C) 2022 Raohmaru

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

#---------------------------------------------------------------------------
# FakePlayer class
#---------------------------------------------------------------------------

class FakePlayer(object):
   def __init__(self):
      self._id = 0
      self.name = 'Dan Hibiki'
      self.isInverted = True
      self.HP = StartingHP
      self.SP = 0
      
   def getGlobalVariable(self, name):
      return me.getGlobalVariable(name)
      
   def get_Name(self):
      return self.name
      
   def ToString(self):
      return self.name
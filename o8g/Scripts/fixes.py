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
# Game engine fixes
#---------------------------------------------------------------------------

# Fix card properties of type Integer which returns a string instead of an integer
# https://octgn.16bugs.com/projects/3602/bugs/188805
cardPropertiesType = {}
for prop in _api.CardProperties():
   # Map the property name to its type
   cardPropertiesType[prop] = _extapi._game.CardProperties[prop].Type.ToString()

# https://github.com/octgn/OCTGN/blob/master/octgnFX/Octgn.JodsEngine/Scripting/Versions/3.1.0.2.py#L263
def CardProperties_getitem(self, key):
   value = _api.CardProperty(self._id, key)
   if cardPropertiesType[key] == "Integer":
      if value == "":
         return 0
      value = int(value)
   return value

# Monkey patch. Might not work in Python 3.
CardProperties.__getitem__ = CardProperties_getitem
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
# DummyPlayer class
#---------------------------------------------------------------------------

class DummyPlayer(Octgn.Core.Play.IPlayPlayer):
   """
   Dummy player object, to format text messages.
   """
   id = 555  # A random ID high enough so it does not mess with the actual players
   
   def __init__(self, color = Colors.Black):
      # `color` is a System.Windows.Media.Color C# object, which is not available as a Python object
      self.color = Octgn.Core.Play.BuiltInPlayer.Notify.Color.FromRgb(*hexToRGB(color))
      self.name = u"\u200B"  # Zero-width space character
      DummyPlayer.id += 1
      self.id = DummyPlayer.id
      
   # Getters that IronPython calls when getting a property ("get_" + property name)
   def get_Color(self):
      return self.color
      
   def get_Name(self):
      return self.name
      
   def get_Id(self):
      return self.id
      
   def get_State(self):
      return Octgn.Core.Play.PlayerState.Connected
      
   def ToString(self):
      return self.name


#---------------------------------------------------------------------------
# Utilities
#---------------------------------------------------------------------------

def hexToRGB(hex):
   """
   Transform a color hex value (like "#FFCC000") into its RGB components as a list.
   """
   hex = hex.lstrip("#")
   return list(int(hex[i:i+2], 16) for i in (0, 2, 4))

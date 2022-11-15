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
# Player class
#---------------------------------------------------------------------------

class GamePlayer(object):
   def __init__(self):
      self.reset()
      # Values used in dialogs that can be overridden by the user to remember his last input
      self.dialogProphecyCount = 3
      self.dialogTrashCount    = 1
      self.dialogDrawCount     = self.handSize
      
   def reset(self):
      self.side           = None   # The side of the player (top: -1, bottom: 1)
      self.handSize       = HandSize
      self.cleanedUpRing  = False  # Tracks if the user has run the Clean-up phase
      self.turnsRemaining = 1      # The number of consecutive turns a player can play
      self.setupDone      = False  # Whether the player has done the game setup
      self.globals        = {}     # Replaces OCTGN player global variables

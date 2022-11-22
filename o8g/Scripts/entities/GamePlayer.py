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

def GamePlayer(player):
   """
   Wraps an OCTGN Player to add more methods and properties.
   """
   # Player is a C# class
   # Dynamically add a class method
   Player.reset = lambda _: GamePlayerReset(player)
   player.reset()
   # Values used in dialogs that can be overridden by the user to remember his last input
   player.dialogProphecyCount = 3
   player.dialogTrashCount    = 1
   player.dialogDrawCount     = player.handSize
   return player
      
def GamePlayerReset(player):
   debug(">>> GamePlayer::reset()")
   player.side           = None   # The side of the player (top: -1, bottom: 1)
   player.handSize       = HandSize
   player.cleanedUpRing  = False  # Tracks if the user has run the Clean-up phase
   player.turnsRemaining = 1      # The number of consecutive turns a player can play
   player.setupDone      = False  # Whether the player has done the game setup
   player.globals        = {}     # Replaces OCTGN player global variables


# Monkey patching the current player
me = GamePlayer(me)

# Python Scripts for the Card Fighters' Clash definition for OCTGN
# Based in the Python Scripts for the Doomtown CCG definition for OCTGN, by Konstantine Thoukydides
# Copyright (C) 2013  Raohmaru

# This python script is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this script.  If not, see <http://www.gnu.org/licenses/>.

#---------------------------------------------------------------------------
# Constants
#---------------------------------------------------------------------------
import re

Phases = [
   '{} is currently in the Pre-game Setup Phase'.format(me),
   "It is now {}'s ACTIVATE Phase",
   "It is now {}'s DRAW Phase",
   "It is now {}'s MAIN Phase",
   "It is now {}'s COUNTERATTACK Phase",
   "It is now {}'s END Phase"
]

# Highlight Colours
AttackColor = "#ff0000"
AttackNoFreezeColor = "#ff8000"
BlockColor = "#ffff00"
ActivatedColor = "#0000ff"
DoesntUnfreezeColor = "#000000"

# Dictionaries which hold all the hard coded markers and tokens (in the markers & tokens set)
MarkersDict = {
    'HP': ("HP", "b86fc644-d084-43d3-99d2-5b11457321cc"),
    'DoesntUnfreeze': ("Doesn't Unfreeze", "5231f83b-b78e-48b3-8bce-62031c022bf4"),
}
TokensDict = {
    'Empty Slot': "75771ec8-47a7-4be6-86dd-781a19755f75"
}

# A table holding tuples with the original location for various card types
CardsCoords = dict(
   #        x     y
   Slot0 = (-311, 198),
   Slot1 = (-134, 198),
   Slot2 = ( 44,  198),
   Slot3 = ( 221, 198)
)

# Misc
Xaxis = 'x'
Yaxis = 'y'
BackupRaiseBP = 3

#---------------------------------------------------------------------------
# Global variables
#---------------------------------------------------------------------------

playerside = None # Variable to keep track on which side each player is
playeraxis = None # Variable to keep track on which axis the player is
phaseIdx = 0
handsize = 5 # Used when automatically refilling your hand
slots = {}  # Dict holding tuples EmptySlot._id / slot number
debugVerbosity = 4 # At -1, means no debugging messages display

automations = {
   'Play'     : True, # Automatically trigger game effetcs and card effects when playing cards
   'Phase'    : True, # Automatically trigger phase related events, and effects from cards in play
   'WinForms' : True # Game will use the custom Windows Forms for displaying multiple-choice and info pop-ups
}
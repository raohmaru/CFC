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
UnitedAttackColor = "#ff42de"
BlockColor = "#ffff00"
ActivatedColor = "#0000ff"
DoesntUnfreezeColor = "#000000"

# Dictionaries which hold all the hard coded markers and tokens (in the markers & tokens set)
MarkersDict = {
   'HP': ("HP", "b86fc644-d084-43d3-99d2-5b11457321cc"),
   'JustEntered': ("Just entered", "9a52c42c-543f-48bb-9a48-d7599d6c8fae"),
   'Attack': ("Attack", "023406a3-417c-473d-bc23-481290755a4a"),
   'UnitedAttack': ("United Attack", "88036e2b-6a1f-40be-a941-988b27c405ba"),
   'CounterAttack': ("Counter-attack", "2fd7dc74-4149-469d-9bde-53e94b99b934"),
   'DoesntUnfreeze': ("Doesn't Unfreeze", "5231f83b-b78e-48b3-8bce-62031c022bf4")
}
TokensDict = {
    'Empty Slot': "75771ec8-47a7-4be6-86dd-781a19755f75"
}

# A table holding tuples with the location for the cards according its states
CardsCoords = dict(
   #        x     y
   Slot0 = (-311, 198),
   Slot1 = (-134, 198),
   Slot2 = ( 44,  198),
   Slot3 = ( 221, 198),
   Attack0 = (-311, 29),
   Attack1 = (-134, 29),
   Attack2 = ( 44,  29),
   Attack3 = ( 221, 29),
   BackupOffset = (0, 10)
)

# A dictionary which holds the regex used in other scripts
Regexps = dict(
   Ability = re.compile(r'(.)\s+([^\r]+)')
)

# Rules
CharsPerTurn = 1
BackupsPerTurn = 1
BackupRaiseBP = 3
MaxUnitedAttack = 2
UnitedAttackCost = 5

# Misc
Xaxis = 'x'
Yaxis = 'y'

#---------------------------------------------------------------------------
# Global variables
#---------------------------------------------------------------------------

playerside = None # Variable to keep track on which side each player is
playeraxis = None # Variable to keep track on which axis the player is
phaseIdx = 0
handsize = 5 # Used when automatically refilling your hand
slots = {}  # Dict holding tuples EmptySlot._id / slot number
charsPlayed = 0  # Num of chars played this turn
backupsPlayed = 0  # Num of chars backed-up this turn
debugVerbosity = 4 # At -1, means no debugging messages display

automations = {
   'Play'     : True, # Automatically trigger game effetcs and card effects when playing cards
   'Phase'    : True, # Automatically trigger phase related events, and effects from cards in play
   'WinForms' : True # Game will use the custom Windows Forms for displaying multiple-choice and info pop-ups
}
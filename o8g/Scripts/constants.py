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

phases = [
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

# A dictionary which holds all the hard coded markers (in the markers file)
mkdict = {
    'HP': ("HP", "b86fc644-d084-43d3-99d2-5b11457321cc")
}

# Misc
Xaxis = 'x'
Yaxis = 'y'

debugVerbosity = 4 # At -1, means no debugging messages display

Automations = {
   'Play'  : True, # Automatically trigger game effetcs and card effects when playing cards
   'Phase' : True  # Automatically trigger phase related events, and effects from cards they control.
}
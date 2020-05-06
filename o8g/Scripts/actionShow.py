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
# Functions to dynamically determines whether or not an action should appear or hide from the menu
#---------------------------------------------------------------------------

def acsh_Debug(args, x = 0, y = 0):
   return me.name == Author

      
def acsh_isChar(args, x = 0, y = 0):
   card = args[0]
   return isCharacter(card)

      
def acsh_gameStarted(args, x = 0, y = 0):
   return turnNumber() != 0

      
def acsh_gameNotStarted(args, x = 0, y = 0):
   return turnNumber() == 0


def acsh_isActivePlayerAttack(args, x = 0, y = 0):
   card = args[0]
   return isCharacter(card) and me.isActive and currentPhase()[1] == AttackPhase and not (hasMarker(card, 'Attack') or hasMarker(card, 'United Attack'))


def acsh_hasAbility(args, x = 0, y = 0):
   card = args[0]
   return bool(card.properties['Ability Type'])

      
def acsh_AutoPlayOff(args, x = 0, y = 0):
   return debugging or not settings['Play']

      
def acsh_isCharAndAutoPlayOff(args, x = 0, y = 0):
   return acsh_isChar(args) and acsh_AutoPlayOff(args)

      
def acsh_canBackup(args, x = 0, y = 0):
   card = args[0]
   return isCharacter(card) and me.isActive and currentPhase()[1] == MainPhase

      
def acsh_hidden(args, x = 0, y = 0):
   return False

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
   if me.name == Author:
      return True
   return False

      
def acsh_isChar(args, x = 0, y = 0):
   card = args[0]
   if card.Type == CharType:
      return True
   return False

      
def acsh_gameStarted(args, x = 0, y = 0):
   return turnNumber() != 0

      
def acsh_gameNotStarted(args, x = 0, y = 0):
   return turnNumber() == 0


def acsh_isActivePlayer(args, x = 0, y = 0):
   return me.isActive


def acsh_isNotActivePlayer(args, x = 0, y = 0):
   return not me.isActive

      
def acsh_isActivePlayerAndNotAttacking(args, x = 0, y = 0):
   card = args[0]
   if not me.isActive:
      return False
   if not MarkersDict['Attack'] in card.markers and not MarkersDict['United Attack'] in card.markers:
      return True
   return False

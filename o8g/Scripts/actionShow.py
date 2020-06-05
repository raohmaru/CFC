# Python Scripts for the Card Fighters' Clash definition for OCTGN
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
   return isCharacter(card) and me.isActive and currentPhase()[1] == AttackPhase and not isAttacking(card)


def acsh_hasAbility(args, x = 0, y = 0):
   card = args[0]
   return bool(card.properties['Ability Type'])

      
def acsh_AutoPlayOff(args, x = 0, y = 0):
   card = args[0] if args != table else None
   return (not card or not isButton(card)) and (debugging or not settings['Play'])

      
def acsh_isCharAndAutoPlayOff(args, x = 0, y = 0):
   return acsh_isChar(args) and acsh_AutoPlayOff(args)

      
def acsh_canBackup(args, x = 0, y = 0):
   card = args[0]
   return isCharacter(card) and me.isActive and currentPhase()[1] == MainPhase

      
def acsh_hidden(args, x = 0, y = 0):
   return False

      
def acsh_notUI(args, x = 0, y = 0):
   return not isUI(args[0])

      
def acsh_gameStartedAutoPlayOff(args, x = 0, y = 0):
   return acsh_gameStarted(args) and acsh_AutoPlayOff(args)

      
def acsh_gameStartedAutoPlay(args, x = 0, y = 0):
   return acsh_gameStarted(args) and not acsh_AutoPlayOff(args) and me.isActive
   
   
def acsh_isCharAndPlayRemoved(args, x = 0, y = 0):
   return getRule('play_removed') and acsh_isChar(args)
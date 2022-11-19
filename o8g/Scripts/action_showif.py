# Python Scripts for the Card Fighters' Clash definition for OCTGN
# Copyright (C) 2013 Raohmaru

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

#-------------------------------------------------------------------------------------------------
# Functions to dynamically determines whether or not an action should appear or hide from the menu
#-------------------------------------------------------------------------------------------------
      
def acsh_autoPlayOff(args, x = 0, y = 0):
   card = args[0] if isinstance(args, list) else None
   return (not card or not isUI(card)) and (debugging or not settings["PlayAuto"])

      
def acsh_canBackup(args, x = 0, y = 0):
   card = args[0]
   return isCharacter(card) and me.isActive and getCurrentPhase() == MainPhase and isCharInRing(card)

      
def acsh_charsInArena(args, x = 0, y = 0):
   return len(getRing()) > 0
   

def acsh_charIsInRing(args, x = 0, y = 0):
   card = args[0]
   return isCharacter(card) and isCharInRing(card)
   
   
def acsh_debug(args, x = 0, y = 0):
   return me.name == Author
      
      
def acsh_gameStarted(args, x = 0, y = 0):
   return turnNumber() != 0

      
def acsh_gameStartedAutoPlay(args, x = 0, y = 0):
   return acsh_gameStarted(args) and not acsh_autoPlayOff(args) and me.isActive

      
def acsh_gameStartedAutoPlayOff(args, x = 0, y = 0):
   return acsh_gameStarted(args) and acsh_autoPlayOff(args)

      
def acsh_gameNotStarted(args, x = 0, y = 0):
   return turnNumber() == 0


def acsh_hasAbility(args, x = 0, y = 0):
   card = args[0]
   return bool(card.properties["Ability Type"])

      
def acsh_hidden(args, x = 0, y = 0):
   return False


def acsh_isActivePlayerAttack(args, x = 0, y = 0):
   card = args[0]
   return isCharacter(card) and me.isActive and getCurrentPhase() == AttackPhase and not isAttacking(card) and isCharInRing(card)

      
def acsh_isChar(args, x = 0, y = 0):
   card = args[0]
   return isCharacter(card)

      
def acsh_isCharAndAutoPlayOff(args, x = 0, y = 0):
   return acsh_charIsInRing(args) and acsh_autoPlayOff(args)
   
   
def acsh_isCharAndPlayRemoved(args, x = 0, y = 0):
   return getRule("play_removed") and acsh_isChar(args)

      
def acsh_isNotCharBackup(args, x = 0, y = 0):
   card = args[0]
   return isCharacter(card) and not hasMarker(card, "Backup")

      
def acsh_isNotBackup(args, x = 0, y = 0):
   card = args[0]
   return not isCharacter(card) or isCharInRing(card)

      
def acsh_isNotTutorial(args, x = 0, y = 0):
   return tutorial is None

      
def acsh_notUI(args, x = 0, y = 0):
   return not isUI(args[0])
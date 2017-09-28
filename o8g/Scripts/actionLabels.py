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
# Functions that alter the label name of an action from the menu
#---------------------------------------------------------------------------

def aclb_Freeze(args, x = 0, y = 0):
   card = args[0]
   if isFrozen(card):
      return "Unfreeze"
   else:
      return "Freeze"

      
def aclb_Resolve(args, x = 0, y = 0):
   card = args[0]
   if isCharacter(card):
      return "Use ability"
   else:
      return "Resolve"

      
def aclb_Attack(args, x = 0, y = 0):
   card = args[0]
   if MarkersDict['Attack'] in card.markers or MarkersDict['United Attack'] in card.markers:
      return "Remove from attack"
   else:
      return

      
def aclb_Block(args, x = 0, y = 0):
   card = args[0]
   if MarkersDict['Counter-attack'] in card.markers:
      return "Don't counter-attack"
   else:
      return

      
def aclb_ChangeSlot(args, x = 0, y = 0):
   card = args[0]
   targets = getTargetedCards(card, True, card.controller == me)
   if len(targets) > 0:
      return "Swap slot"
   else:
      return "Change slot"

      
def aclb_Ability(args, x = 0, y = 0):
   card = args[0]
   if card.alternate == 'noability':
      return "Restore abilities"
   else:
      return "Lose abilities"

      
def aclb_Destroy(args, x = 0, y = 0):
   card = args[0]
   if isCharacter(card):
      return "KO"
   else:
      return "Discard"

      
def aclb_RevealTopDeck(group, x = 0, y = 0):
   if group[0].isFaceUp:
      return "Hide top card"
   else:
      return "Reveal top card"

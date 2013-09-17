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
# Event handlers
#---------------------------------------------------------------------------

# Event handler hooked to an OCTGN game events
def onMoveCardEventHandler(player, card, fromGroup, toGroup, oldIndex, index, oldX, oldY, x, y, isScriptMove):
   debugNotify(">>> onMoveCardEventHandler()") #Debug
   if fromGroup == table and toGroup != table and card.Type == 'Character':
      clearAttachLinks(card)
   debugNotify("<<< onMoveCardEventHandler()") #Debug

def onEndTurnEventHandler(player):
   mute()
   if player != me: return
   # Clears targets, colors and freeze (tap) characters in the player's ring
   myCards = (card for card in table
      if card.controller == me)
   for card in myCards:
      card.target(False)
      if card.highlight != None and card.highlight != DoesntUnfreezeColor:
         if card.highlight == AttackColor:
            card.orientation = Rot90
         card.highlight = None
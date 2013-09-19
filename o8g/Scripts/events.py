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

def checkTwoSidedTable():
   mute()
   if not table.isTwoSided():
      information(":::WARNING::: This game is designed to be played on a two-sided table. Playing could be uncomfortable otherwise! Please start a new game and make sure the appropriate button is checked.")

def OnLoadDeckEventHandler(player, groups):
   debugNotify(">>> OnLoadDeckEventHandler()") #Debug
   
   if player != me: return # We only want the owner of to run this script
   mute()
   decklen = len(me.Deck)
   if decklen != 50:
      notify (":::ERROR::: {}'s Deck must have exactly 50 cards (it has {} cards)".format(me,decklen))
   
   debugNotify("<<< OnLoadDeckEventHandler()") #Debug

def onMoveCardEventHandler(player, card, fromGroup, toGroup, oldIndex, index, oldX, oldY, x, y, isScriptMove):
   debugNotify(">>> onMoveCardEventHandler()") #Debug
   
   if card.owner == me and fromGroup == table and toGroup != table:
      if card.Type == 'Character':
         clearAttachLinks(card)
      
   debugNotify("<<< onMoveCardEventHandler()") #Debug
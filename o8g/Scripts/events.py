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
   if card.owner != me: return
   # Card is an Empty Slot token
   if card.model == Tokens['Empty Slot']:
      debugNotify(">>> Empty Slot moved") #Debug
      if toGroup != table:
         card.moveTo(table)
      elif oldIndex != index:
         card.setIndex(0)
      else:
         debugNotify("Slot number: {}".format(slots.get(card._id, 0)))
         slotNum = slots.get(card._id, 0)
         coords = CardsCoords['Slot'+`slotNum`]
         cx,cy = card.position
         if cx != coords[0] or cy != coords[1]:
            debugNotify("Moving slot to: {}".format(coords))
            card.moveToTable(coords[0], coords[1])
   # Other card which has been moved out the table
   elif fromGroup == table and toGroup != table:
      if card.Type == 'Character':
         clearAttachLinks(card)
         freeSlot(card)
   # Always in front of the Empty Slot tokens
   elif oldIndex != index and index == 0:
      if len(players) > 1:
         card.setIndex(8)
      else:
         card.setIndex(4)
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
      warning("This game is designed to be played on a two-sided table.\nPlease start a new game and make sure the appropriate option is checked.")


def onLoadDeck(player, groups):   
   if player != me: return # We only want the owner of to run this script
   mute()
   decksize = len(me.Deck)
   if decksize != DeckSize:
      notify(":::ERROR::: {}'s deck must have exactly {} cards (it has {} cards)".format(DeckSize, me,decksize))


def onMoveCard(player, card, fromGroup, toGroup, oldIndexs, indexs, oldX, oldY, x, y, faceup, highlights, markers):
   if card.controller != me: return
   if fromGroup == table and toGroup != table:
      if card.Type == 'Character':
         clearAttachLinks(card)
         freeSlot(card)
   elif fromGroup == table and toGroup == table:
      if card.Type == 'Character' and (oldX != x or oldY != y):
         alignBackups(card, x, y)
         

def onTurnChange(player, turnNumber):
   # Reset some player variables at the start of each turn
   debug(">>> OnTurn({}, {})".format(player, turnNumber)) #Debug
   if player == me:
      global charsPlayed, backupsPlayed
      charsPlayed = 0  # Num of chars played this turn
      backupsPlayed = 0  # Num of chars backed-up this turn
      setGlobalVar('PhaseIdx', 0, me)
   else:
      goToCleanup()
   debug("<<< OnTurn()") #Debug
   
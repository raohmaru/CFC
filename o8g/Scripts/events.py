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

def onTableLoad():
   checkTwoSidedTable()


def onGameStart():
   resetAll()


def onLoadDeck(player, groups):
   if player != me: return # We only want the owner of the deck to run this script
   debug(">>> onLoadDeck({})".format(player)) #Debug
   notify("{} has loaded a deck. Now his deck has {} cards.".format(player, len(me.Deck)))
   mute()
   cards = {}
   for card in me.Deck:
      if card.model in cards:
         cards[card.model] += 1
      else:
         cards[card.model] = 1
      if cards[card.model] > MaxCardCopies:
         msg = "INVALID DECK: {0}'s deck has more than {1} copies of a card (only {1} are allowed)".format(player, MaxCardCopies)
         notify(msg)
         # A more visible notification for all players
         for p in players:
            remoteCall(p, "notifyBar", ["#FF0000", msg])
         return
   if automations['Play']:
      setup(silent=True)


def onMoveCard(player, card, fromGroup, toGroup, oldIndex, index, oldX, oldY, x, y, faceup, highlights, markers):
   mute()
   if card.controller != me: return
   if fromGroup == table and toGroup != table:
      if card.Type == CharType:
         clearAttachLinks(card)
         freeSlot(card)
   elif fromGroup == table and toGroup == table:
      if card.Type == CharType and not MarkersDict['Backup'] in card.markers:
         alignBackups(card, x, y)
   # Restore transformed card if it goes to a pile
   if toGroup._name in me.piles:
      if card._id in transfCards:
         newCard = toGroup.create(transfCards[card._id], quantity = 1)
         newCard.moveTo(toGroup, index)
         whisper("Transformed card {} is restored into {}".format(card, newCard))
         del transfCards[card._id]
         card.delete()
         

def onTurnChange(player, turnNumber):
   # Reset some player variables at the start of each turn
   debug(">>> OnTurn({}, {})".format(player, turnNumber)) #Debug
   if player == me:
      global charsPlayed, backupsPlayed
      charsPlayed = 0  # Num of chars played this turn
      backupsPlayed = 0  # Num of chars backed-up this turn
      setGlobalVar('PhaseIdx', 0, me)
      clearGlobalVar('UnitedAttack')
      clearGlobalVar('Blockers')
   else:
      goToCleanup(silent = True)
   debug("<<< OnTurn()") #Debug
   
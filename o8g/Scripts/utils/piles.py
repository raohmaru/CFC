# Python Scripts for the Card Fighters' Clash definition for OCTGN
# Copyright (C) 2022 Raohmaru

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

#---------------------------------------------------------------------------
# Pile functions
#---------------------------------------------------------------------------

def swapPiles(pile1, pile2):
   """
   Swaps the cards of two piles.
   """
   mute()
   savedPile1 = [card for card in pile1]
   for card in pile2:
      card.moveTo(pile1)
   waitForAnimation()
   for card in savedPile1:
      card.moveTo(pile2)   
   if len(players) > 1:
      waitForAnimation()
   notify("{} swaps its {} with its {}.".format(me, pile1.name, pile2.name))


def reveal(group):
   """
   Reveals the cards of the group to the other players.
   """
   if isinstance(group, list):
      for card in group:
         isFaceUp = card.isFaceUp
         # If card is not faced up its name won't appear in the chat
         card.isFaceUp = True
         notify("{} reveals {} {}.".format(me, card, fromWhereStr(card.group)))
         card.isFaceUp = isFaceUp
   else:
      cards = [card for card in group]
      notify("{} shows his {}".format(group.controller, group.name))
      showCardDlg(cards, "Cards in {}'s {}".format(group.controller, group.name), 0, min = 0)
      # Allow opponent to peek at the revealed cards of your hand
      if group.name == "Hand":
         cardPeek(cards)
   
   
def getRing(player = None):
   """
   Gets the character cards in the ring of given player, or in the arena.
   """
   if player:
      ring = getGlobalVar("Ring", player)
   else: 
      ring = getGlobalVar("Ring", me)
      if len(players) > 1:
         ring += getGlobalVar("Ring", players[1])
   return [Card(c) for c in ring
      if Card(c) in table]  # Just in case there is a ghost card


def getRingSize(player = me):
   """
   Gets the number of characters in the ring of the given player.
   """
   ring = getGlobalVar("Ring", player)
   return NumSlots - ring.count(None)


def moveToGroup(toGroup, card, sourceGroup = None, pos = None, reveal = None, sourcePlayer = me, silent = False):
   mute()
   if not sourceGroup:
      sourceGroup = card.group
   posText = "to the top of"
   if pos is not None:
      if pos < 0:
         posText = "to the bottom of"
         # -2 is treated as "end of pile" (like -1), so we need to shift the index (bug?)
         if pos < -1:
            pos -= 1
      elif pos > 0:
         posText = "to position {} from the top of".format(pos)
   if toGroup.name == "Hand":
      posText = "into"
   name = "a card"
   # Cards in my hand are faced up for me
   isFaceUp = False if sourceGroup.name == "Hand" else card.isFaceUp
   if reveal != False:
      if isFaceUp:
         # If the group visibility is None, str(card) will output "Card", so we get the name
         if toGroup.name == "Deck" or toGroup.name == "Hand":
            name = card.Name
         else:
            name = card
      elif reveal:
         if toGroup.name == "Hand":
            remoteCall(getOpp(), "cardPeek", [card])
         # If the group visibility is None, card will output "Card", so we get the name
         if toGroup.name == "Deck" or toGroup.name == "Hand":
            card.isFaceUp = True
            name = card.Name
         else:
            name = card
      # Flip up card if the destination group is visible for all
      if toGroup.name == "Discard pile" or toGroup.name == "Removed pile":
         card.isFaceUp = True
         name = card
   # If card is not faced up its name won't appear in the chat
   if card.isFaceUp != isFaceUp:
      card.isFaceUp = isFaceUp
   fromText = fromWhereStr(sourceGroup, sourcePlayer)
   targetCtrl = "its" if me == sourcePlayer else "{}'s".format(me)
   msg = "{} moved {} {} {} {} {}.".format(sourcePlayer, name, fromText, posText, targetCtrl, toGroup.name)
   card.moveTo(toGroup, pos)
   if not silent:
      notify(msg)
   else:
      return msg
   
   
def cardPeek(cards):
   if isinstance(cards, Card):
      cards = [cards]
   for card in cards:
      card.peek()

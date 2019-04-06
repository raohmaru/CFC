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

# Happens when the table first loads, and never again
def onTableLoaded():
   checkTwoSidedTable()


def onGameStarted():
   resetAll()
   if debugging:
      debugScenario()


def onDeckLoaded(args):
   player = args.player
   groups = args.groups
   if player != me: return # We only want the owner of the deck to run this script
   debug(">>> onDeckLoaded({})".format(player)) #Debug
   notify("{} has loaded a deck. Now his deck has {} cards.".format(player, len(me.Deck)))
   mute()
   cards = {}
   for card in me.Deck:
      if card.Name in cards:
         cards[card.Name] += 1
      else:
         cards[card.Name] = 1
      if cards[card.Name] > MaxCardCopies:
         msg = "INVALID DECK: {0}'s deck has more than {1} copies of a card (only {1} are allowed)".format(player, MaxCardCopies)
         notify(msg)
         # A more visible notification for all players
         for p in players:
            remoteCall(p, "notifyBar", ["#FF0000", msg])
         return
   if automations['Play']:
      setup(silent=True)

      
def onCardsMoved(args):
   mute()
   cards = args.cards
   transfCards = getGlobalVar('Transformed')
   handChanged = False
   ringChanged = False
   for i in range(len(cards)):
      card      = args.cards[i]
      fromGroup = args.fromGroups[i]
      toGroup   = args.toGroups[i]
      index     = args.indexs[i]
      x         = args.xs[i]
      y         = args.ys[i]
      faceup    = args.faceups[i]
      highlight = args.highlights[i]
      markers   = eval(args.markers[i])  # markers it's a string equivalent of the Marker object
      
      if card.controller != me:
         return
      if fromGroup == table and toGroup != table:
         if isCharacter(card):
            clearAttachLinks(card)
            if charIsInRing(card):
               freeSlot(card)
               ringChanged = True
            if MarkersDict['Attack'] in markers or MarkersDict['United Attack'] in markers:
               rearrangeUAttack(card)
         removeParsedCard(card)
      elif fromGroup == table and toGroup == table:
         if isCharacter(card) and not MarkersDict['Backup'] in card.markers:
            alignBackups(card, *card.position)
      elif fromGroup != table and toGroup == table:
         if charIsInRing(card):
            ringChanged = True
      # Restore transformed card if it goes to a pile
      if toGroup._name in me.piles:
         if card._id in transfCards:
            newCard = toGroup.create(transfCards[card._id], quantity = 1)
            newCard.moveTo(toGroup, card.index)
            whisper("Transformed card {} is restored into {}".format(card, newCard))
            del transfCards[card._id]
            card.delete()
      if not handChanged and (fromGroup == me.hand and toGroup != me.hand or fromGroup != me.hand and toGroup == me.hand):
         handChanged = True
         
   setGlobalVar('Transformed', transfCards)
   # Trigger events
   if handChanged:
      triggerGameEvent(GameEvents.HandChanges, len(me.hand))
   if ringChanged:
      triggerGameEvent(GameEvents.RingChanges, getRingSize())

   
def onTurnPassed(args):
   # Reset some player variables at the start of each turn
   debug(">>> onTurnPassed({}, {})".format(args.player, turnNumber())) #Debug
   global charsPlayed, backupsPlayed, cleanedUpRing
   # That was my old turn
   if args.player == me:
      charsPlayed = 0  # Num of chars played this turn
      backupsPlayed = 0  # Num of chars backed-up this turn
      clearGlobalVar('UnitedAttack')
      clearGlobalVar('Blockers')
      if not cleanedUpRing:
         triggerPhaseEvent(CleanupPhase)  # Force cleanup
   # I start my turn
   elif args.player is not None:
      cleanedUpRing = False
   debug("<<< onTurnPassed()") #Debug


def onPhasePassed(args):
   name, idx = currentPhase()
   debug(">>> onPhasePassed: {} => {}".format(args.id, idx))
   if me.isActive:
      if idx == CleanupPhase:
         global cleanedUpRing
         cleanedUpRing = True
      gotoPhase(idx, args.id)

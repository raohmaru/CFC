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
# Global variables
#---------------------------------------------------------------------------

playerside = None # Variable to keep track on which side each player is
playeraxis = None # Variable to keep track on which axis the player is
phaseIdx = 0
handsize = 5 # Used when automatically refilling your hand
AttachingCard = None # Holds the card about to have other card attached. This needs to become a shared OCTGN variable when available.
AttachedCards = {} # A dictionary which holds a coutner for each card, numbering how many attached cards each card has.

#---------------------------------------------------------------------------
# Phases
#---------------------------------------------------------------------------

def showCurrentPhase():  # Just say a nice notification about which phase you're on.
   notify(phases[phaseIdx].format(me))

def nextPhase(group = table, x = 0, y = 0):  # Function to take you to the next phase.
   mute()
   if phaseIdx > len(phases): phaseIdx = 1
   else: phaseIdx += 1
   if phaseIdx == 1: goToActivate()
   elif phaseIdx == 2: goToDraw()
   elif phaseIdx == 3: goToMain()
   elif phaseIdx == 4: goToCounterattack()
   elif phaseIdx == 5: goToEnd()
   else: showCurrentPhase()

def goToActivate(group = table, x = 0, y = 0):
   mute()
   phaseIdx = 1
   showCurrentPhase()

def goToDraw(group = table, x = 0, y = 0):
   mute()
   phaseIdx = 2
   showCurrentPhase()

def goToMain(group = table, x = 0, y = 0):
   mute()
   phaseIdx = 3
   showCurrentPhase()

def goToCounterattack(group = table, x = 0, y = 0):
   mute()
   phaseIdx = 4
   showCurrentPhase()

def goToEnd(group = table, x = 0, y = 0):
   mute()
   phaseIdx = 5
   showCurrentPhase()

#---------------------------------------------------------------------------
# Table group actions
#---------------------------------------------------------------------------

def setup(group,x=0,y=0):  # This function is usually the first one the player does
   debugNotify(">>> setup()") #Debug
   mute()
   if table.isTwoSided():
      if not confirm("This game is NOT designed to be played on a two-sided table. Things will break!! Please start a new game and unckeck the appropriate button. Are you sure you want to continue?"): return
   resetAll()
   chooseSide() # The classic place where the players choose their side.
   me.Deck.shuffle()
   refill() # We fill the player's play hand to their hand size (usually 5)
   notify("Setup for player {} completed.".format(me,))
   debugNotify("<<< setup()") #Debug

def discard(card, x = 0, y = 0):  # Discard a card.
   debugNotify(">>> discard()") #Debug
   mute()
   card.moveTo(me.piles['Discard Pile'])
   notify("{} has discarded {}.".format(me, card))
   debugNotify("<<< discard()") #Debug

def doesNotUnboot(card, x = 0, y = 0):  # Mark a card as "Does not unboot" or unmark it. We use a card highlight to do this.
   if card.highlight == DoesntUnbootColor:  # If it's already marked, remove highlight from it and inform.
      card.highlight = None
      notify("{}'s {} can now unboot during Nightfall.".format(me, card))
   else:
      card.highlight = DoesntUnbootColor # Otherwise highlight it and inform.
      notify("{}'s {} will not unboot during Nightfall.".format(me, card))

#---------------------------------------------------------------------------
# Marker functions
#---------------------------------------------------------------------------

def plusBP(card, x = 0, y = 0, notification = 'loud', count = 1):
   mute()
   if notification == loud:
      notify("{} marks that {}'s BP has raised by {}".format(me, card, count))
   for i in range(0,count):
      card.markers[HPMarker] += 1

def minusBP(card, x = 0, y = 0, notification = 'loud', count = 1):
   mute()
   if notification == loud:
      notify("{} marks that {}'s BP has lowered by {}.".format(me, card, count))
   for i in range(0,count):
      if HPMarker in card.markers:
         card.markers[HPMarker] -= 1

def addMarker(cards, x = 0, y = 0):  # A simple function to manually add any of the available markers.
   mute()
   marker, quantity = askMarker() # Ask the player how many of the same type they want.
   if quantity == 0: return
   for card in cards:  # Then go through their cards and add those markers to each.
      card.markers[marker] += quantity
      notify("{} adds {} {} counter to {}.".format(me, quantity, marker[0], card))	

def changeMarker(cards, marker, question):
   n = 0
   for c in cards:
      if c.markers[marker] > n:
	     n = c.markers[marker]   
   count = askInteger(question, n)
   if count == None: return
   for c in cards:
      n = c.markers[marker]
      c.markers[marker] = count
      dif = count-n
      if dif >= 0: dif = "+" + str(dif)   
      notify("{} sets {}'s {} to {}({}).".format(me, c, marker[0], count, dif))

def changeBP(cards, x = 0, y = 0):
   mute()
   changeMarker(cards, HPMarker, "Set character BP to:")

#---------------------------------------------------------------------------
# Hand and Deck actions
#---------------------------------------------------------------------------

def playCard(card):  # This is the function to play cards from your hand. It's one of the core functions.
   mute()
   chooseSide()
   src = card.group
   card.moveToTable(0, 0)
   notify("{} plays {} from their {}.".format(me, card, src.name))

def shuffle(group):  # A simple function to shuffle piles
   group.shuffle()

def reshuffle(group = me.piles['Discard Pile']):  # This function reshuffles the player's discard pile into their deck.
   mute()
   Deck = me.Deck
   for card in group: card.moveTo(Deck) # Move the player's cards from the discard to their deck one-by-one.
   random = rnd(100, 10000) # Bug 105 workaround. This delays the next action until all animation is done.
                           # see https://octgn.16bugs.com/projects/3602/bugs/102681
   Deck.shuffle() # Then use the built-in shuffle action
   notify("{} reshuffled their {} into their Deck.".format(me, group.name)) # And inform everyone.

def draw(group = me.Deck):  # Draws one card from the deck into the player's hand.
   mute()
   if len(group) == 0:
      return
   group.top().moveTo(me.hand)
   notify("{} draws a card.".format(me))

def drawMany(group, count = None, notification = 'loud'):  # This function draws a variable number cards into the player's hand.
   mute()
   if count == None: count = askInteger("Draw how many cards?", 5) # Ask the player how many cards they want.
   for i in range(0, count):
      if len(group) > 0:  # If the deck is noy empty...
         group.top().moveTo(me.hand)  # ...then move them one by one into their play hand.
   if notification == loud : notify("{} draws {} cards.".format(me, count))


def trash(group = me.Deck, x = 0, y = 0, silent = False):  # Draws one card from the deck into the discard pile and announces its value.
   mute()
   if len(group) == 0:
      return
   count = askInteger("Trash how many cards?", 1)
   if count == None:
      return
   for card in group.top(count):
      card.moveTo(me.piles['Discard Pile'])
   rnd(1, 100) # Wait a bit more, as in multiplayer games, things are slower.
   if not silent: notify("{} trash top {} cards from {}.".format(me, count, group.name))
   
def setHandSize(group):  # A function to modify a player's hand size.
   global handsize
   handsize = askInteger("What is your current hand size?", handsize)
   if handsize == None: handsize = 5
   notify("{} sets their hand size to {}".format(me, handsize))

def refill(group = me.hand):  # Refill the player's hand to its hand size.
   global handsize
   playhand = len(me.hand) # count how many cards there are currently there.
   if playhand < handsize: drawMany(me.Deck, handsize - playhand, silent) # If there's less cards than the handsize, draw from the deck until it's full.

def discard(card, x = 0, y = 0):  # Discard a card from your hand.
   mute()
   card.moveTo(me.piles['Discard Pile'])
   notify("{} has discarded {}.".format(me, card))

def randomDiscard(group):  # Discard a card from your hand randomly.
   mute()
   card = group.random() # Select a random card
   if card == None: return # If hand is empty, do nothing.
   notify("{} randomly discards a card.".format(me)) # Inform that a random card was discarded
   card.moveTo(me.piles['Discard Pile']) # Move the card in the discard pile.

def moveIntoDeck(group):
   mute()
   Deck = me.Deck
   for card in group: card.moveTo(Deck)
   notify("{} moves their {} into their Deck.".format(me, group.name))
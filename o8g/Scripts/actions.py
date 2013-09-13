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
   
   # Unfreeze (untap) characters in the player's ring
   myCards = (card for card in table
      if card.controller == me
      and card.highlight != DoesntUnfreezeColor)
   for card in myCards:
      card.orientation &= ~Rot90
      card.highlight = None

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
   
   # Freeze (tap) characters in the player's ring
   myCards = (card for card in table
      if card.controller == me
      and card.highlight == AttackColor)
   for card in myCards:
      card.orientation = Rot90
      card.highlight = None

#---------------------------------------------------------------------------
# Table group actions
#---------------------------------------------------------------------------

def setup(group,x=0,y=0):  # This function is usually the first one the player does
   debugNotify(">>> setup()") #Debug
   mute()
   resetAll()
   chooseSide() # The classic place where the players choose their side.
   me.Deck.shuffle()
   refill() # We fill the player's play hand to their hand size
   notify("Setup for player {} completed.".format(me,))
   debugNotify("<<< setup()") #Debug

def scoop(group, x = 0, y = 0):
   mute()
   if not confirm("Are you sure you want to reset?"):
      return
   me.HP = 30
   me.SP = 0
   for card in me.Deck:
      card.moveTo(card.owner.Deck)
   myCards = (card for card in table
      if card.controller == me)
   for card in myCards:
      card.moveTo(card.owner.Deck)
   discards = me.piles['Discard Pile']
   for card in discards:
      card.moveTo(card.owner.Deck)
   for card in me.hand:
      card.moveTo(card.owner.Deck)
   notify("{} resets.".format(me))

def download_o8c(group,x=0,y=0):
   openUrl("http://raohmaru.com/pub/cfc/sets/cfc-sets-bundle.o8c")

def flipCoin(group, x = 0, y = 0):
   mute()
   n = rnd(1, 2)
   if n == 1:
      notify("{} flips heads.".format(me))
   else:
      notify("{} flips tails.".format(me))

def roll6(group, x = 0, y = 0):
   mute()
   rollDie(6)

def roll10(group, x = 0, y = 0):
   mute()
   rollDie(10)

def rollDie(num):
   n = rnd(1, num)
   notify("{} rolls {} on a {}-sided die.".format(me, n, num))
   
def randomPick(group, x = 0, y = 0):
    mute()
    card = group.random()
    if card == None:
        return
    card.select()
    card.target(True)
    if group == table:
        notify("{} randomly selects {}'s {} on the ring.".format(me, card.controller, card))
    else:
        notify("{} randomly selects {} from their {}.".format(me, card, group.name))
   
def clearAll(group, x = 0, y = 0):
   notify("{} clears all targets and highlights.".format(me))
   for card in group:
      card.target(False)
      if card.controller == me:
         card.highlight = None

#---------------------------------------------------------------------------
# Table card actions
#---------------------------------------------------------------------------

def tapUntap(card, x = 0, y = 0, count = None):
   mute()
   card.orientation ^= Rot90
   if card.orientation & Rot90 == Rot90:
      notify('{} taps {}'.format(me, card))
   else:
      notify('{} untaps {}'.format(me, card))

def faceUpDown(card, x = 0, y = 0):
   mute()
   if card.isFaceUp == True:
      card.isFaceUp = False
      notify("{} faces down {}.".format(me, card))
   else:
      card.isFaceUp = True
      notify("{} faces up {}.".format(me, card))

def flip(card, x = 0, y = 0):
   mute()
   if card.orientation & Rot180 == Rot180:
      notify("{} unflips {}.".format(me, card))
   else:
      notify("{} flips {}.".format(me, card))
   card.orientation ^= Rot180

def clone(cards, x = 0, y = 0):
   for card in cards:
      table.create(card.model, x, y, 1)
      x, y = table.offset(x, y)

def attack(card, x = 0, y = 0):
   mute()
   card.highlight = AttackColor
   notify('{} attacks with {}'.format(me, card))

def attackNoFreeze(card, x = 0, y = 0):
   mute()
   card.highlight = AttackNoFreezeColor
   notify('{} attacks with {}'.format(me, card))
	
def block(card, x = 0, y = 0):
    mute()
    card.highlight = BlockColor
    notify('{} counter-attacks with {}'.format(me, card))

def activate(card, x = 0, y = 0):
	mute()
	card.highlight = ActivatedColor
	notify("{} uses {}'s ability.".format(me, card))

def freeze(card, x = 0, y = 0, count = None):
   mute()
   card.orientation ^= Rot90
   if card.orientation & Rot90 == Rot90:
      notify('{} freezes {}'.format(me, card))
   else:
      notify('{} unfreezes {}'.format(me, card))
   if card.highlight == AttackColor or card.highlight == ActivatedColor:
      card.highlight = None
      
def clear(card, x = 0, y = 0):
   notify("{} clears {}.".format(me, card))
   card.highlight = None
   card.target(False)

#---------------------------------------------------------------------------
# Movement actions
#---------------------------------------------------------------------------
	
def destroy(card, x = 0, y = 0):
	mute()
	src = card.group
	fromText = " from the ring" if src == table else " from their " + src.name
	card.moveTo(me.piles['Discard Pile'])
	notify("{} KOs {}{}.".format(me, card, fromText))
	
def remove(card, x = 0, y = 0):
	mute()
	src = card.group
	fromText = " from the ring" if src == table else " from their " + src.name
	card.moveTo(me.piles['Removed Zone'])
	notify("{} kills {}{}.".format(me, card, fromText))

def toHand(card, x = 0, y = 0):
   mute()
   src = card.group
   fromText = " from the ring" if src == table else " from their " + src.name
   cardname = card.name
   if card.isFaceUp == False:
      if confirm("Reveal to all players?"):
         card.isFaceUp = True
         rnd(10,100)  # This delays the next action until all animation is done.
      else:
         cardname = "a card"
   card.moveTo(me.hand)
   notify("{} returns {} to their hand{}.".format(me, cardname, fromText))

def toDeckTop(card, x = 0, y = 0):
   mute()
   src = card.group
   fromText = " from the ring" if src == table else " from their " + src.name
   card.moveTo(me.Deck)
   notify("{} puts {}{} on the top of their Deck.".format(me, card, fromText))

def toDeckBottom(card, x = 0, y = 0):
   mute()
   src = card.group
   fromText = " from the ring" if src == table else " from their " + src.name
   card.moveToBottom(me.Deck)
   notify("{} puts {}{} on the bottom of their Deck.".format(me, card, fromText))

def toDeckTopAll(group, x = 0, y = 0):
   mute()
   for card in group:
      card.moveTo(me.Deck)
   notify("{} moves all cards from their {} to top of their Deck.".format(me, group.name))

def toDeckBottomAll(group, x = 0, y = 0):
   mute()
   for card in group:
      card.moveToBottom(me.Deck)
   notify("{} moves all cards from their {} to bottom of their Deck.".format(me, group.name))

def discardAll(group, x = 0, y = 0):
   mute()
   discards = me.piles['Discard Pile']
   for card in group:
      card.moveTo(discards)
   notify("{} moves all cards from their {} to their Discard Pile.".format(me, group.name))

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

def changeBP(cards, x = 0, y = 0):
   mute()
   changeMarker(cards, HPMarker, "Set character BP to:")

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

#---------------------------------------------------------------------------
# Hand actions
#---------------------------------------------------------------------------

def play(card):  # This is the function to play cards from your hand. It's one of the core functions.
   mute()
   chooseSide()
   card.moveToTable(0, 0)
   notify("{} plays {} from their {}.".format(me, card, card.group.name))

def backup(card, x = 0, y = 0):  # Play a card as backup attached to a character in the player's ring
   mute()
   target = [card for card in table if card.targetedBy]
   if len(targetcount) >= 1:
      attach(card, target[0])
      card.moveToTable(0, 0)
      notify("{} backups {} with {} from their {}.".format(me, target[0], card, card.group.name))

def discard(card, x = 0, y = 0):  # Discard a card from your hand.
   mute()
   card.moveTo(me.piles['Discard Pile'])
   notify("{} has discarded {}.".format(me, card))

def randomDiscard(group, x = 0, y = 0):
    mute()
    card = group.random()
    if card == None:
        return
    card.isFaceUp = True
    rnd(10,100)  # This delays the next action until all animation is done.
    card.moveTo(me.piles['Discard Pile'])
    notify("{} randomly discards {}.".format(me, card))

#---------------------------------------------------------------------------
# Piles actions
#---------------------------------------------------------------------------

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
      if len(group) > 0:  # If the deck is not empty...
         group.top().moveTo(me.hand)  # ...then move them one by one into their play hand.
   if notification == loud : notify("{} draws {} cards.".format(me, count))


def trash(group = me.Deck, x = 0, y = 0, silent = False):  # Draws one card from the deck into the discard pile and announces its value.
   mute()
   if len(group) == 0:
      return
   count = askInteger("Trash how many cards?", 1)
   if count == None:
      return
   discards = me.piles['Discard Pile']
   for card in group.top(count):
      card.moveTo(discards)
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
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
# Phases
#---------------------------------------------------------------------------

def showCurrentPhase():  # Just say a nice notification about which phase you're on.
   notify(Phases[phaseIdx].format(me))

def nextPhase(group = table, x = 0, y = 0):  # Function to take you to the next phase.
   global phaseIdx
   if phaseIdx >= len(Phases)-1:
      phaseIdx = 1
   else:
      phaseIdx += 1
   if phaseIdx == 1:   goToActivate()
   elif phaseIdx == 2: goToDraw()
   elif phaseIdx == 3: goToMain()
   elif phaseIdx == 4: goToCounterattack()
   elif phaseIdx == 5: goToEnd()
   else: showCurrentPhase()

def goToActivate(group = table, x = 0, y = 0):
   global phaseIdx
   phaseIdx = 1
   showCurrentPhase()
   triggerPhaseEvent('Activate')

def goToDraw(group = table, x = 0, y = 0):
   global phaseIdx
   phaseIdx = 2
   showCurrentPhase()
   triggerPhaseEvent('Draw')

def goToMain(group = table, x = 0, y = 0):
   global phaseIdx
   phaseIdx = 3
   showCurrentPhase()
   triggerPhaseEvent('Main')

def goToCounterattack(group = table, x = 0, y = 0):
   global phaseIdx
   phaseIdx = 4
   showCurrentPhase()
   triggerPhaseEvent('Counterattack')

def goToEnd(group = table, x = 0, y = 0):
   global phaseIdx
   phaseIdx = 5
   showCurrentPhase()
   triggerPhaseEvent('End')

#---------------------------------------------------------------------------
# Table group actions
#---------------------------------------------------------------------------

def setup(group,x=0,y=0):  # This function is usually the first one the player does
   debugNotify(">>> setup()") #Debug
   global slots
   mute()
   if not confirm("Are you sure you want to setup for a new game?\n(This action should only be done after a game reset)"):
      return
   chooseSide() # The classic place where the players choose their side.
   
   # Adds up to 4 empty slot tokens to the ring
   emptySlotsTokens = [card for card in table
      if card.controller == me
      and card.model == TokensDict['Empty Slot']]
   if len(emptySlotsTokens) == 0:
      for i in range(4):
         debugNotify("Creating Empty Slot {}".format(i))
         coords = CardsCoords['Slot'+`i`]
         card = table.create(TokensDict['Empty Slot'], coords[0], coords[1], 1, True)
         slots[card._id] = i
   # We ensure that player has loaded a deck
   if len(me.Deck) == 0:
      whisper("Please load a deck first")
      return
   me.Deck.shuffle()
   refill() # We fill the player's play hand to their hand size
   notify("Setup for player {} completed.".format(me,))
   debugNotify("<<< setup()") #Debug

def scoop(group, x = 0, y = 0):
   mute()
   if not confirm("Are you sure you want to reset?\n(All cards in your ring will return to their owner's hand and your stats will be restored)"):
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

def flipCoin(group, x = 0, y = 0):
   mute()
   n = rnd(1, 2)
   if n == 1:
      notify("{} flips Heads.".format(me))
   else:
      notify("{} flips Tails.".format(me))

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

def clearAll(allPlayers = False):
   notify("{} clears all targets and highlights.".format(me))
   for card in table:
      if allPlayers or card.controller == me:
         clear(card, silent = True)

def switchPlayAutomation(group, x = 0, y = 0):
   switchAutomation('Play')

def switchPhaseAutomation(group, x = 0, y = 0):
   switchAutomation('Phase')

def switchWinForms(group, x = 0, y = 0):
   switchAutomation('WinForms')

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

def freeze(card, x = 0, y = 0, unfreeze = None, silent = False):
   mute()
   if unfreeze != None:
      card.orientation = Rot0 if unfreeze else Rot90
   else:
      card.orientation ^= Rot90
   if card.orientation & Rot90 == Rot90:
      if not silent: notify('{} freezes {}'.format(me, card))
   else:
      if not silent: notify('{} unfreezes {}'.format(me, card))
   if card.highlight != DoesntUnfreezeColor:
      card.highlight = None

def doesNotUnfreeze(card, x = 0, y = 0):
   mute()
   if card.highlight != DoesntUnfreezeColor:
      card.highlight = DoesntUnfreezeColor
      notify("{0}'s {1} will not unfreeze during {0}'s next Activate phase.".format(me, card))
   else:
      card.highlight = None
      notify("{0}'s {1} will unfreeze as normal during {0}'s Activate phase.".format(me, card))

def clear(card, x = 0, y = 0, silent = False):
   if not silent: notify("{} clears {}.".format(me, card))
   card.target(False)
   if card.highlight != DoesntUnfreezeColor:
      card.highlight = None

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
   fromText = "from the ring" if src == table else "from their " + src.name
   cardname = card.Name
   if not card.isFaceUp:
      if confirm("Reveal card to all players?"):
         card.isFaceUp = True
         rnd(10,100)
         cardname = card.Name
      else:
         cardname = "a card"
   card.moveTo(me.hand)
   if src == table:
      notify("{} returns {} to their hand {}.".format(me, cardname, fromText))
   else:
      notify("{} puts {} in their hand {}.".format(me, cardname, fromText))

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
   Deck = me.Deck
   for card in group:
      card.moveTo(Deck)
   notify("{} moves all cards from their {} to top of their Deck.".format(me, group.name))

def toDeckBottomAll(group, x = 0, y = 0):
   mute()
   Deck = me.Deck
   for card in group:
      card.moveToBottom(Deck)
   notify("{} moves all cards from their {} to bottom of their Deck.".format(me, group.name))

def discardAll(group, x = 0, y = 0):
   mute()
   discards = me.piles['Discard Pile']
   for card in group:
      card.moveTo(discards)
   notify("{} moves all cards from their {} to their Discard Pile.".format(me, group.name))

#---------------------------------------------------------------------------
# Marker actions
#---------------------------------------------------------------------------

def plusBP(card, x = 0, y = 0, silent = False, count = 1):
   mute()
   if not silent:
      notify("{} raises {}'s BP by {}".format(me, card, count))
   for i in range(0,count):
      card.markers[MarkersDict['HP']] += 1

def minusBP(card, x = 0, y = 0, silent = False, count = 1):
   mute()
   if not silent:
      notify("{} lowers {}'s BP by {}.".format(me, card, count))
   for i in range(0,count):
      if MarkersDict['HP'] in card.markers:
         card.markers[MarkersDict['HP']] -= 1

def addMarker(cards, x = 0, y = 0):  # A simple function to manually add any of the available markers.
   mute()
   marker, quantity = askMarker() # Ask the player how many of the same type they want.
   if quantity == 0: return
   for card in cards:  # Then go through their cards and add those markers to each.
      card.markers[marker] += quantity
      notify("{} adds {} {} counter to {}.".format(me, quantity, marker[0], card))

def changeBP(cards, x = 0, y = 0):
   mute()
   changeMarker(cards, MarkersDict['HP'], "Set character BP to:")

#---------------------------------------------------------------------------
# Hand actions
#---------------------------------------------------------------------------

def play(card):  # This is the function to play cards from your hand.
   debugNotify(">>> playing card {}".format(card)) #Debug
   
   mute()
   chooseSide()  # Just in case...
   group = card.group
   if automations['Play']:
      if not playAuto(card): return
   else:
      placeCard(card, card.Type)
   notify("{} plays {} from their {}.".format(me, card, group.name))
   
   debugNotify("<<< playing card end") #Debug

def backup(card, x = 0, y = 0):  # Play a card as backup attached to a character in the player's ring
   debugNotify(">>> backup with card {}".format(card)) #Debug
   
   mute()
   group = card.group
   if automations['Play']:
      target = backupAuto(card)
      if target:
         notify("{} backups {} with {} from their {}.".format(me, target, card, group.name))
   else:
      placeCard(card, card.Type)
      notify("{} backups with {} from their {}.".format(me, card, group.name))
   
   debugNotify("<<< backup()") #Debug

def discard(card, x = 0, y = 0):
   mute()
   group = card.group
   card.moveTo(me.piles['Discard Pile'])
   notify("{} has discarded {} from their {}.".format(me, card, group.name))

def randomDiscard(group, x = 0, y = 0):
    mute()
    card = group.random()
    if card == None:
        return
    card.moveTo(me.piles['Discard Pile'])
    notify("{} randomly discards {}.".format(me, card))

def refill(group = me.hand):  # Refill the player's hand to its hand size.
   playhand = len(me.hand) # count how many cards there are currently there.
   if playhand < handsize: drawMany(me.Deck, handsize - playhand, True) # If there's less cards than the handsize, draw from the deck until it's full.

#---------------------------------------------------------------------------
# Piles actions
#---------------------------------------------------------------------------

def draw(group = me.Deck):  # Draws one card from the deck into the player's hand.
   mute()
   if len(group) == 0:
      return
   group.top().moveTo(me.hand)
   notify("{} draws a card.".format(me))

def drawMany(group, count = None, silent = False):  # This function draws a variable number cards into the player's hand.
   mute()
   if count == None: count = askInteger("Draw how many cards?", handsize) # Ask the player how many cards they want.
   for i in range(0, count):
      if len(group) > 0:  # If the deck is not empty...
         group.top().moveTo(me.hand)  # ...then move them one by one into their play hand.
   if not silent: notify("{} draws {} cards.".format(me, count))

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
   if len(players) > 1: rnd(1, 100)  # Wait a bit more, as in multiplayer games, things are slower.
   if not silent: notify("{} trash top {} cards from {}.".format(me, count, group.name))

def shuffle(group):  # A simple function to shuffle piles
   mute()
   for card in group:
      if card.isFaceUp:
         card.isFaceUp = False
   group.shuffle()
   notify("{} shuffled their {}".format(me, group.name))

def reshuffle(group = me.piles['Discard Pile']):  # This function reshuffles the player's discard pile into their deck.
   mute()
   Deck = me.Deck
   for card in group: card.moveTo(Deck) # Move the player's cards from the discard to their deck one-by-one.
   random = rnd(100, 10000) # Bug 105 workaround. This delays the next action until all animation is done.
                           # see https://octgn.16bugs.com/projects/3602/bugs/102681
   Deck.shuffle() # Then use the built-in shuffle action
   notify("{} reshuffled their {} into their Deck.".format(me, group.name)) # And inform everyone.

def revealTopDeck(group, x = 0, y = 0):
   mute()
   if group[0].isFaceUp:
      notify("{} hides {} from top of Library.".format(me, group[0]))
      group[0].isFaceUp = False
   else:
      group[0].isFaceUp = True
      notify("{} reveals {} from top of Library.".format(me, group[0]))

def swapWithDeck(group = me.piles['Discard Pile']):  # This function reshuffles the player's discard pile into their deck.
   mute()
   Deck = me.Deck
   savedDeck = (card for card in Deck)   
   for card in group:
      card.moveTo(Deck)   
   for card in savedDeck:
      card.moveTo(group)   
   if len(players) > 1: rnd(1, 100) # Wait a bit more, as in multiplayer games, things are slower.
   notify("{} swaps their {} with their Deck.".format(me, group.name)) # And inform everyone.

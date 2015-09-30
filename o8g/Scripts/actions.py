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

import re

#---------------------------------------------------------------------------
# Phases
#---------------------------------------------------------------------------

def showCurrentPhase():  # Just say a nice notification about which phase you're on.
   notify(Phases[getGlobalVar('PhaseIdx', me)].format(me))


def nextPhase(group = table, x = 0, y = 0):  # Function to take you to the next phase.
   idx = oldIdx = getGlobalVar('PhaseIdx', me)
   if idx >= len(Phases) - 1:
      idx = ActivatePhase
   else:
      idx += 1
   if idx == ActivatePhase:
      if oldIdx != CleanupPhase:  # Force cleanup
         triggerPhaseEvent(CleanupPhase)
      goToActivate()
   elif idx == DrawPhase:    goToDraw()
   elif idx == MainPhase:    goToMain()
   elif idx == AttackPhase:  goToAttack()
   elif idx == BlockPhase:   goToCounterattack()
   elif idx == EndPhase:     goToEnd()
   elif idx == CleanupPhase: goToCleanup()


def goToActivate(group = table, x = 0, y = 0):
   setGlobalVar('PhaseIdx', ActivatePhase, me)
   showCurrentPhase()
   triggerPhaseEvent(ActivatePhase)


def goToDraw(group = table, x = 0, y = 0):
   setGlobalVar('PhaseIdx', DrawPhase, me)
   showCurrentPhase()
   triggerPhaseEvent(DrawPhase)


def goToMain(group = table, x = 0, y = 0):
   setGlobalVar('PhaseIdx', MainPhase, me)
   showCurrentPhase()
   triggerPhaseEvent(MainPhase)


def goToAttack(group = table, x = 0, y = 0):
   setGlobalVar('PhaseIdx', AttackPhase, me)
   showCurrentPhase()
   triggerPhaseEvent(AttackPhase)


def goToCounterattack(group = table, x = 0, y = 0):
   setGlobalVar('PhaseIdx', BlockPhase, me)
   showCurrentPhase()
   triggerPhaseEvent(BlockPhase)


def goToEnd(group = table, x = 0, y = 0):
   setGlobalVar('PhaseIdx', EndPhase, me)
   showCurrentPhase()
   triggerPhaseEvent(EndPhase)


def goToCleanup(group = table, x = 0, y = 0, silent = False):
   setGlobalVar('PhaseIdx', CleanupPhase, me)
   if not silent:
      showCurrentPhase()
   triggerPhaseEvent(CleanupPhase)


#---------------------------------------------------------------------------
# Table group actions
#---------------------------------------------------------------------------

def setup(group, x=0, y=0):
# This function is usually the first one the player does
   debug(">>> setup()") #Debug
   mute()
   if not confirm("Are you sure you want to setup for a new game?\n(This action should only be done after a game reset.)"):
      return
   chooseSide() # The classic place where the players choose their side
   # We ensure that player has loaded a deck
   if len(me.Deck) == 0:
      warning("Please load a deck first.")
      return
   notify(Phases[SetupPhase].format(me))
   me.Deck.shuffle()
   refill() # We fill the player's play hand to their hand size
   notify("Setup for player {} completed.".format(me))

   
def scoop(group, x=0, y=0):
# Reset the game
   debug(">>> reset()") #Debug
   mute()
   if not confirm("Are you sure you want to reset the game?"):
      return
      
   resetAll()   
   myCards = (card for card in table
      if card.controller == me)        
   toOwnerDeck(myCards)
   toOwnerDeck(me.Deck)
   toOwnerDeck(me.hand)
   toOwnerDeck(me.piles['Discard Pile'])
   toOwnerDeck(me.piles['Kill Pile'])
   notify("{} resets the game.".format(me,))


def flipCoin(group, x = 0, y = 0):
   mute()
   n = rnd(1, 2)
   if n == 1:
      notify("{} flips Heads.".format(me))
   else:
      notify("{} flips Tails.".format(me))


def randomPick(group, x = 0, y = 0, fromPlayer = None):
   mute()
   card = None
   player = fromPlayer if fromPlayer != None else me
   if group == table:
      ring = getGlobalVar('Ring', player)
      if fromPlayer == None and len(players) > 1:
         ring += getGlobalVar('Ring', players[1])
      ring = filter(None, ring)
      if(len(ring)) > 0:
         card = Card(ring[rnd(0, len(ring)-1)])
   else:
      card = group.random()
   if card == None:
      return
   card.select()
   card.target(True)
   revealDrawnCard(card)
   if group == table:
      notify("{} randomly selects {}'s {} on the ring.".format(me, card.controller, card))
   else:
      notify("{} randomly selects {} from their {}.".format(me, card, group.name))
      

def randomPickMine(group, x = 0, y = 0):
   randomPick(group, x, y, me)
      

def randomPickEnemy(group, x = 0, y = 0):
   if len(players) > 1:
      randomPick(group, x, y, players[1])

      
def clearAll(group = table, x = 0, y = 0, allPlayers = False):
   notify("{} clears all targets and highlights.".format(me))
   for card in table:
      if allPlayers or card.controller == me:
         clear(card, silent = True)


def alignCards(group, x = 0, y = 0):
   myCards = (card for card in table
      if card.controller == me
      and (card.Type == 'Character'))
   for card in myCards:
      alignCard(card)


def switchPlayAutomation(group, x = 0, y = 0):
   switchAutomation('Play')


def switchPhaseAutomation(group, x = 0, y = 0):
   switchAutomation('Phase')


def switchWinForms(group, x = 0, y = 0):
   switchAutomation('WinForms')


def switchAttackDamage(group, x = 0, y = 0):
   switchAutomation('AttackDmg')


#---------------------------------------------------------------------------
# Table card actions
#---------------------------------------------------------------------------

def attack(card, x = 0, y = 0):
   mute()
   if automations['Play']:
      if not attackAuto(card): return
   card.highlight = AttackColor
   notify('{} attacks with {}'.format(me, card))


def attackNoFreeze(card, x = 0, y = 0):
   mute()
   if automations['Play']:
      if not attackAuto(card): return
   card.highlight = AttackNoFreezeColor
   setMarker(card, 'NoFreeze')
   notify('{} attacks without freeze with {}.'.format(me, card))


def unitedAttack(card, x = 0, y = 0):
   debug(">>> unitedAttack()") #Debug
   mute()
   cardsnames = card
   if automations['Play']:
      target = unitedAttackAuto(card)
      if target:
         cardsnames = '{} and {}'.format(card, target)
      else:
         return
   card.highlight = UnitedAttackColor
   notify('{} does an United Attack with {}.'.format(me, cardsnames))


def block(card, x = 0, y = 0):
   mute()
   text = 'with {}'.format(card)
   if automations['Play']:
      target = blockAuto(card)
      if target:
         text = '{} '.format(target) + text
      else:
         return
   card.highlight = BlockColor
   notify('{} counter-attacks {}'.format(me, text))


def activate(card, x = 0, y = 0):
   debug(">>> activate()") #Debug
   mute()
   if automations['Play']:
      if not activateAuto(card): return
   if card.Type == 'Character':
      pcard = getParsedCard(card)
      if pcard.hasEffect():
         if pcard.ability_type == ActivatedAbility:
            freeze(card, silent = True)
         ability = "ability {}".format(pcard.ability)
      else:
         whisper("{} has no ability.".format(card))
         return
   else:
      ability = "effect"
   card.highlight = ActivatedColor
   notify("{} activates {}'s {}.".format(me, card, ability))


def freeze(card, x = 0, y = 0, unfreeze = None, silent = False):
   mute()
   if unfreeze != None:
      card.orientation = Rot0 if unfreeze else Rot90
   else:
      card.orientation ^= Rot90
   if isFrozen(card):
      if not silent: notify('{} freezes {}'.format(me, card))
   else:
      if not silent: notify('{} unfreezes {}'.format(me, card))
   if card.highlight == ActivatedColor:
      card.highlight = None


def doesNotUnfreeze(card, x = 0, y = 0):
   mute()
   msg = "not unfreeze"
   if not MarkersDict['DoesntUnfreeze'] in card.markers:
      card.highlight = DoesntUnfreezeColor
      setMarker(card, 'DoesntUnfreeze')
   else:
      card.highlight = None
      removeMarker(card, 'DoesntUnfreeze')
      msg = "unfreeze as normal"
   
   notify("{0}'s {1} will {2} during {0}'s Activate phase.".format(card.controller, card, {2}))


def clear(card, x = 0, y = 0, silent = False):
   if not silent: notify("{} clears {}.".format(me, card))
   card.target(False)
   card.arrow(card, False)
   if not card.highlight in [ActivatedColor]:
      card.highlight = None


def alignCardAction(card, x = 0, y = 0):
   if card.Type == 'Character':
      slotIdx = getSlotIdx(card)
      if slotIdx != -1:
         alignCard(card, slotIdx=slotIdx)
      else:
         backups = getGlobalVar('Backups')
         if backups.get(card._id):
            c = Card(backups[card._id])
            alignBackups(c, *c.position)


def askCardBackups(card, x = 0, y = 0):
   if card.Type == 'Character':
      acceptedBackups = (card.properties['Backup 1'], card.properties['Backup 2'], card.properties['Backup 3'])
      msg = "{} can be backed-up with the following character types:\n- {}".format(card.Name, '\n- '.join(filter(None, acceptedBackups)))
      information(msg)
      whisper(msg)
   else:
      information("Only character cards can be backed-up.")


#---------------------------------------------------------------------------
# Movement actions
#---------------------------------------------------------------------------
   
def destroy(card, x = 0, y = 0):
   mute()
   fromText = fromWhereStr(card.group)
   action = "discards"
   card.moveTo(me.piles['Discard Pile'])
   if card.Type == 'Character':
      action = "KOs"
   notify("{} {} {} {}.".format(me, action, card, fromText))
   

def remove(card, x = 0, y = 0):
   mute()
   fromText = fromWhereStr(card.group)
   card.moveTo(me.piles['Kill Pile'])
   notify("{} kills {} {}.".format(me, card, fromText))


def toHand(card, x = 0, y = 0):
   mute()
   src = card.group
   fromText = fromWhereStr(card.group)
   cardname = revealDrawnCard(card)
   card.moveTo(me.hand)
   if src == table:
      notify("{} returns {} to its hand {}.".format(me, cardname, fromText))
   else:
      notify("{} puts {} in its hand {}.".format(me, cardname, fromText))


def toDeckTop(card, x = 0, y = 0):
   mute()
   fromText = fromWhereStr(card.group)
   cardname = revealDrawnCard(card, faceUp = False)
   card.moveTo(me.Deck)
   notify("{} puts {} {} on the top of its Deck.".format(me, cardname, fromText))


def toDeckBottom(card, x = 0, y = 0):
   mute()
   fromText = fromWhereStr(card.group)
   card.moveToBottom(me.Deck)
   notify("{} puts {} {} on the bottom of its Deck.".format(me, card, fromText))


def toDeckTopAll(group, x = 0, y = 0):
   mute()
   Deck = me.Deck
   for card in group:
      card.moveTo(Deck)
   if len(players) > 1: rnd(1, 100) # Wait a bit more, as in multiplayer games, things are slower.
   notify("{} moves all cards from their {} to the top of its Deck.".format(me, group.name))


def toDeckBottomAll(group, x = 0, y = 0):
   mute()
   Deck = me.Deck
   for card in group:
      card.moveToBottom(Deck)
   if len(players) > 1: rnd(1, 100) # Wait a bit more, as in multiplayer games, things are slower.
   notify("{} moves all cards from their {} to the bottom of its Deck.".format(me, group.name))

   
def toOwnerDeck(cards):
   for card in cards:
      card.moveTo(card.owner.Deck)


def discardAll(group, x = 0, y = 0):
   mute()
   discards = me.piles['Discard Pile']
   for card in group:
      card.moveTo(discards)
   if len(players) > 1: rnd(1, 100) # Wait a bit more, as in multiplayer games, things are slower.
   notify("{} moves all cards from their {} to its Discard Pile.".format(me, group.name))

   
def toTableFaceDown(card, x = 0, y = 0):
   debug(">>> toTableFaceDown {}".format(card)) #Debug
   mute()
   fromText = fromWhereStr(card.group)
   placeCard(card, card.Type, faceDown=True)
   notify("{} puts a card face down in the Arena {}.".format(me, fromText))


#---------------------------------------------------------------------------
# Marker actions
#---------------------------------------------------------------------------

# --------------
# Characters' BP
# --------------
def plusBP(card, x = 0, y = 0, silent = False, count = 1):
   mute()
   addMarker(card, 'BP', count)
   if not silent:
      notify("{} raises {}'s BP by {} (new BP is {})".format(me, card, count, getMarker(card, 'BP')))

def minusBP(card, x = 0, y = 0, silent = False, count = 1):
   mute()
   c = count
   if c > getMarker(card, 'BP'):
      c = getMarker(card, 'BP')
   addMarker(card, 'BP', -c)
   if not silent:
      notify("{} lowers {}'s BP by {} (new BP is {}).".format(me, card, count, getMarker(card, 'BP')))
      
def plusBP2(card, x = 0, y = 0): plusBP(card, count = 2)
def plusBP3(card, x = 0, y = 0): plusBP(card, count = 3)
def plusBP4(card, x = 0, y = 0): plusBP(card, count = 4)
def plusBP5(card, x = 0, y = 0): plusBP(card, count = 5)
def plusBP6(card, x = 0, y = 0): plusBP(card, count = 6)
def plusBP7(card, x = 0, y = 0): plusBP(card, count = 7)
def plusBP8(card, x = 0, y = 0): plusBP(card, count = 8)
def plusBP9(card, x = 0, y = 0): plusBP(card, count = 9)

def plusBPX(card, x = 0, y = 0):
   n = askInteger("Raise BP by...", 1)
   if n == None: return
   plusBP(card, count = n)
   
def minusBP2(card, x = 0, y = 0): minusBP(card, count = 2)
def minusBP3(card, x = 0, y = 0): minusBP(card, count = 3)
def minusBP4(card, x = 0, y = 0): minusBP(card, count = 4)
def minusBP5(card, x = 0, y = 0): minusBP(card, count = 5)
def minusBP6(card, x = 0, y = 0): minusBP(card, count = 6)
def minusBP7(card, x = 0, y = 0): minusBP(card, count = 7)
def minusBP8(card, x = 0, y = 0): minusBP(card, count = 8)
def minusBP9(card, x = 0, y = 0): minusBP(card, count = 9)

def minusBPX(card, x = 0, y = 0):
   n = askInteger("Lower BP by...", 1)
   if n == None: return
   minusBP(card, count = n)

def changeBP(cards, x = 0, y = 0):
   mute()
   changeMarker(cards, MarkersDict['BP'], "Set character BP to:")

def addMarkerAction(cards, x = 0, y = 0):  # A simple function to manually add any of the available markers.
   mute()
   marker, quantity = askMarker() # Ask the player how many of the same type they want.
   if quantity == 0: return
   for card in cards:  # Then go through their cards and add those markers to each.
      card.markers[marker] += quantity
      notify("{} adds {} {} counter to {}.".format(me, quantity, marker[0], card))

# -----------
# Players' SP
# -----------
def plusSP (group, x = 0, y = 0): modSP(1)
def plusSP2(group, x = 0, y = 0): modSP(2)
def plusSP3(group, x = 0, y = 0): modSP(3)
def plusSP4(group, x = 0, y = 0): modSP(4)
def plusSP5(group, x = 0, y = 0): modSP(5)
def plusSP6(group, x = 0, y = 0): modSP(6)
def plusSP7(group, x = 0, y = 0): modSP(7)
def plusSP8(group, x = 0, y = 0): modSP(8)
def plusSP9(group, x = 0, y = 0): modSP(9)

def plusSPX(group, x = 0, y = 0):
   n = askInteger("Gain SP by...", 1)
   if n == None: return
   modSP(n)
   
def minusSP (group, x = 0, y = 0): modSP(-1)
def minusSP2(group, x = 0, y = 0): modSP(-2)
def minusSP3(group, x = 0, y = 0): modSP(-3)
def minusSP4(group, x = 0, y = 0): modSP(-4)
def minusSP5(group, x = 0, y = 0): modSP(-5)
def minusSP6(group, x = 0, y = 0): modSP(-6)
def minusSP7(group, x = 0, y = 0): modSP(-7)
def minusSP8(group, x = 0, y = 0): modSP(-8)
def minusSP9(group, x = 0, y = 0): modSP(-9)

def minusSPX(group, x = 0, y = 0):
   n = askInteger("Lose SP by...", 1)
   if n == None: return
   modSP(-n)


def toggleNoAbility(cards, x = 0, y = 0):
   for card in cards:
      toggleMarker(card, 'NoAbility')

#---------------------------------------------------------------------------
# Hand actions
#---------------------------------------------------------------------------

def play(card):  # This is the function to play cards from your hand.
   debug(">>> playing card {}".format(card)) #Debug
   
   mute()
   chooseSide()  # Just in case...
   slot = ""
   if automations['Play']:
      if not playAuto(card): return
      slot = " in slot {}".format(getSlotIdx(card))
   else:
      placeCard(card, card.Type)
   notify("{} plays {} from its {}{}.".format(me, card, card.group.name, slot))
   
   debug("<<< playing card end") #Debug


def backup(card, x = 0, y = 0):  # Play a card as backup attached to a character in the player's ring
   debug(">>> backup with card {}".format(card)) #Debug
   
   mute()
   group = card.group
   if automations['Play']:
      target = backupAuto(card)
      if target:
         notify("{} backups {} with {} from its {} (new BP is {}).".format(me, target, card, group.name, getMarker(target, 'BP')))
   else:
      placeCard(card, card.Type)
      notify("{} backups with {} from its {}.".format(me, card, group.name))
   
   debug("<<< backup()") #Debug


def discard(card, x = 0, y = 0):
   mute()
   card.moveTo(me.piles['Discard Pile'])
   notify("{} has discarded {} from its {}.".format(me, card, card.group.name))


def randomDiscard(group, x = 0, y = 0):
    mute()
    card = group.random()
    if card == None:
        return
    card.moveTo(me.piles['Discard Pile'])
    notify("{} randomly discards {} from its {}.".format(me, card, group.name))


def refill(group = me.hand):  # Refill the player's hand to its hand size.
   playhand = len(me.hand) # count how many cards there are currently there.
   if playhand < handSize:
      drawMany(me.Deck, handSize - playhand, True) # If there's less cards than the handSize, draw from the deck until it's full.


#---------------------------------------------------------------------------
# Piles actions
#---------------------------------------------------------------------------

def draw(group = me.Deck):  # Draws one card from the deck into the player's hand.
   mute()
   if len(group) == 0:
      whisper("Can't draw from an empty {}.".format(group.name))
      return
   group.top().moveTo(me.hand)
   notify("{} draws a card.".format(me))


def drawMany(group, count = None, silent = False):  # This function draws a variable number cards into the player's hand.
   mute()
   if count == None:
      count = askInteger("Draw how many cards?", handSize) # Ask the player how many cards they want.
   for i in range(0, count):
      if len(group) > 0:  # If the deck is not empty...
         group.top().moveTo(me.hand)  # ...then move them one by one into their play hand.
   if not silent:
      notify("{} draws {} cards.".format(me, count))


def randomDraw(group = me.Deck, type = None):
   mute()
   if len(group) == 0:
      whisper("Can't draw from an empty {}.".format(group.name))
      return
   if type == None:
      card = group.random()
   else:
      cards = [card for card in group
         if card.Type == type]
      if len(cards) == 0:
         whisper("There is no cards of type {} in the {}.".format(type, group.name))
         return
      card = cards[rnd(0, len(cards)-1)]
   cardname = revealDrawnCard(card, type)
   card.moveTo(me.hand)
   notify("{} draws {} at random {}.".format(me, cardname, fromWhereStr(group)))
   
   
def randomDrawCHA(group = me.Deck):
   randomDraw(group, 'Character')
   
   
def randomDrawAC(group = me.Deck):
   randomDraw(group, 'Action')
   
   
def randomDrawRE(group = me.Deck):
   randomDraw(group, 'Reaction')


def trash(group = me.Deck, x = 0, y = 0, silent = False):
# Draws one card from the deck into the discard pile
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
   if not silent:
      notify("{} trash top {} cards from {}.".format(me, count, group.name))


def shuffle(group):
# A simple function to shuffle piles
   mute()
   for card in group:
      if card.isFaceUp:
         card.isFaceUp = False
   group.shuffle()
   notify("{} shuffled its {}".format(me, group.name))


def reshuffle(group = me.piles['Discard Pile']):
# This function reshuffles the player's discard pile into its deck.
   mute()
   Deck = me.Deck
   for card in group:
      card.moveTo(Deck) # Move the player's cards from the discard to its deck one-by-one.
   rnd(1, 100) # Bug 105 workaround. This delays the next action until all animation is done.
               # see https://octgn.16bugs.com/projects/3602/bugs/102681
   Deck.shuffle() # Then use the built-in shuffle action
   notify("{} reshuffled its {} into its Deck.".format(me, group.name)) # And inform everyone.


def revealTopDeck(group, x = 0, y = 0):
   mute()
   if group[0].isFaceUp:
      notify("{} hides {} from top of Library.".format(me, group[0]))
      group[0].isFaceUp = False
   else:
      group[0].isFaceUp = True
      notify("{} reveals {} from top of Library.".format(me, group[0]))


def swapWithDeck(group = me.piles['Discard Pile']):
# This function swap the deck with the discard pile.
   mute()
   Deck = me.Deck
   savedDeck = [card for card in Deck]
   for card in group:
      card.moveTo(Deck)
   rnd(1, 100)  # Delay the next action until all animation is done
   for card in savedDeck:
      card.moveTo(group)   
   if len(players) > 1: rnd(1, 100) # Wait a bit more, as in multiplayer games, things are slower.
   notify("{} swaps its {} with its Deck.".format(me, group.name)) # And inform everyone.

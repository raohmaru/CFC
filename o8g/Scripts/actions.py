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

def nextPhase(group = table, x = 0, y = 0):  # Function to take you to the next phase.
   idx = currentPhase()[1]
   if idx >= len(Phases) - 1:
      idx = ActivatePhase
   else:
      idx += 1
   setPhase(idx)

   
def gotoPhase(idx, oldIdx = 0):
   # if idx == ActivatePhase:
   if idx == DrawPhase:
      if turnNumber() == 1:
         notify("(The player who goes first should skip his Draw phase during their first turn.)")
   # elif idx == MainPhase:  
   # elif idx == AttackPhase:
   elif idx == BlockPhase: 
      if len(players) > 1:
         notify("(Now defending player {} may choose if block attackers)".format(players[1]))
   # elif idx == EndPhase:   
   elif idx == CleanupPhase:
      whisper("(This is the last phase of your turn)")
   triggerPhaseEvent(idx)

   
def gotoActivate(group = table, x = 0, y = 0):
   setPhase(ActivatePhase)


def gotoDraw(group = table, x = 0, y = 0):
   setPhase(DrawPhase)


def gotoMain(group = table, x = 0, y = 0):
   setPhase(MainPhase)


def gotoAttack(group = table, x = 0, y = 0):
   setPhase(AttackPhase)


def gotoCounterattack(group = table, x = 0, y = 0):
   setPhase(BlockPhase)


def gotoEnd(group = table, x = 0, y = 0):
   setPhase(EndPhase)


def gotoCleanup(group = table, x = 0, y = 0, silent = False):
   setPhase(CleanupPhase)


#---------------------------------------------------------------------------
# Table group actions
#---------------------------------------------------------------------------

def setup(group=table, x=0, y=0, silent=False):
# This function is usually the first one the player does
   debug(">>> setup()") #Debug
   mute()
   # if not silent:
      # if not confirm("Are you sure you want to setup for a new game?"):
         # return
   chooseSide() # The classic place where the players choose their side
   # We ensure that player has loaded a deck
   if len(me.Deck) == 0:
      warning("Please load a deck first.")
      return
   notify(Phases[SetupPhase].format(me))
   me.Deck.shuffle()
   refill() # We fill the player's play hand to their hand size
   notify("Setup for player {} completed.".format(me))
   # Start the turn of the first player to setup
   if automations['Play']:
      me.setActive()

   
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
   toOwnerDeck(me.piles['Removed Pile'])
   notify("{} resets the game.".format(me))


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
      and (card.Type == CharType))
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
   setMarker(card, 'No Freeze')
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
   if card.highlight == ActivatedColor:
      card.highlight = None
      notify("{} deactivates {}.".format(me, card))
      return
   ability = "effect"
   pcard = getParsedCard(card)
   if card.Type == CharType and pcard.hasEffect():
      ability = "ability {}".format(pcard.ability)
   notify("{} tries to activate {}'s {}.".format(me, card, ability))
   if automations['Play']:
      if not activateAuto(card):
         return
   elif card.Type == CharType and pcard.hasEffect() and pcard.ability.type == ActivatedAbility:
      freeze(card, silent = True)
   card.highlight = ActivatedColor
   notify("{} has activated {}'s {}.".format(me, card, ability))


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
   if not MarkersDict["Does Not Unfreeze"] in card.markers:
      card.highlight = DoesntUnfreezeColor
      setMarker(card, "Does Not Unfreeze")
   else:
      card.highlight = None
      removeMarker(card, "Does Not Unfreeze")
      msg = "unfreeze as normal"
   
   notify("{0}'s {1} will {2} during {0}'s Activate phase.".format(card.controller, card, {2}))


def clear(card, x = 0, y = 0, silent = False):
   if not silent: notify("{} clears {}.".format(me, card))
   card.target(False)
   card.arrow(card, False)
   if not card.highlight in [ActivatedColor]:
      card.highlight = None


def alignCardAction(card, x = 0, y = 0):
   if card.Type == CharType:
      slotIdx = getSlotIdx(card)
      if slotIdx != -1:
         alignCard(card, slotIdx=slotIdx)
      else:
         backups = getGlobalVar('Backups')
         if backups.get(card._id):
            c = Card(backups[card._id])
            alignBackups(c, *c.position)


def askCardBackups(card, x = 0, y = 0):
   if card.Type == CharType:
      acceptedBackups = getAcceptedBackups(card)
      for c in me.hand:
         if c.Type == CharType:
            if c != card and c.Subtype in acceptedBackups:
               c.highlight = InfoColor
            elif c.highlight == InfoColor:
               c.highlight = None
      whisper("Highlighting compatible back-ups cards in your hand")
      msg = "{} can be backed-up with the following character types:\n- {}".format(card.Name, '\n- '.join(filter(None, acceptedBackups)))
      information(msg)
      whisper(msg)
   else:
      information("Only character cards can be backed-up.")
      

def toggleAbility(card, x = 0, y = 0):
   mute()
   # Removes card from parsed list to parse it again with the new abilities
   if card.Type != CharType or (card.alternate == '' and card.Rules == ''):
      return
   removeParsedCard(card)
   if card.alternate == 'noability':
      card.alternate = ''
      if card.Rules != '':
         notify("{} restores {}'s abilities".format(me, card))
         parseCard(card)
      else:
         notify("{} tried to restore {}'s abilities, but it doesn't have any core ability".format(me, card))
   else:
      # Updates proxy image of other players
      for p in players:
         remoteCall(p, "addAlternateRules", [card, '', '', 'noability'])
      notify("{} removes {}'s abilities".format(me, card))
   

def transformCards(cards, x = 0, y = 0):
   mute()
   cardModel = None
   targets =  [c for c in table   if c.targetedBy == me]
   targets += [c for c in me.hand if c.targetedBy == me]
   targets += [c for c in me.piles['Discard Pile'] if c.targetedBy == me]
   if len(targets) > 0:
      cardModel = targets[0].model
   else:
      cardtype = cards[0].Type
      card, quantity = askCard({"Type":cardtype}, "and", "Choose a card")
      if quantity > 0:
         cardModel = card
   if cardModel:
      for card in cards:
         transformCard(card, cardModel)
      for target in targets:
         target.target(False)
      

def copyAbility(card, x = 0, y = 0, target = None):
   debug(">>> copyAbility()") #Debug
   mute()
   if card.Type != CharType:
      whisper("Abilities can only be copied to character cards.")
      return
   if target == None:
      targets =  [c for c in table   if c.targetedBy == me]
      targets += [c for c in me.hand if c.targetedBy == me]
      targets += [c for c in me.piles['Discard Pile'] if c.targetedBy == me]
      if len(targets) > 0 and targets[0].Type == CharType and targets[0] != card:
         target = targets[0]
      else:
         model, quantity = askCard({"Type":CharType}, "and", "Choose a character with an ability")
         if quantity > 0:
            target = model
         else:
            return
   if target:
      result = copyAlternateRules(card, target)
      if result:
         removeParsedCard(card)
         parseCard(card, target.model)
         # Updates proxy image for the other players
         for p in players:
            if p != me:
               remoteCall(p, "copyAlternateRules", [card, target])
         update()  # Trying this method to delay next actions until networked tasks are complete
         notify("{} copies ability {} to {}.".format(me, getParsedCard(card).ability.name, card))
      else:
         warning("Target character card doesn't have an ability to copy.")
   else:
      warning("Please select a valid character card.")
   debug("<<< copyAbility()") #Debug

         
def swapAbilities(card, x = 0, y = 0):
   debug(">>> swapAbilities()") #Debug
   mute()
   if card.Type != CharType or not charIsInRing(card, card.controller):
      whisper("Abilities can only be swapped between character cards in the ring.")
      return
   target = None
   targets =  [c for c in table   if c.targetedBy == me]
   if len(targets) > 0 and targets[0].Type == CharType and targets[0] != card and charIsInRing(targets[0], targets[0].controller):
      target = targets[0]
      if card.Rules and target.Rules:
         card_copy = Struct(**{
            'Rules'  : card.Rules,
            'Ability': card.Ability,
            'model'  : card.model
         })
         copyAbility(card,   target = target)
         copyAbility(target, target = card_copy)
      else:
         warning("Please select two character cards with abilities.")
      target.target(False)
   else:
      warning("Please select a valid character card in the ring.")

#---------------------------------------------------------------------------
# Movement actions
#---------------------------------------------------------------------------
   
def destroy(card, x = 0, y = 0, controller=me):
   mute()
   fromText = fromWhereStr(card.group)
   action = "discards"
   card.moveTo(me.piles['Discard Pile'])
   if card.Type == CharType:
      action = "KOs"
   notify("{} {} {} {}.".format(controller, action, card, fromText))
   

def remove(card, x = 0, y = 0):
   mute()
   fromText = fromWhereStr(card.group)
   card.moveTo(me.piles['Removed Pile'])
   notify("{} removes {} {}.".format(me, card, fromText))


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


def toHandAll(group, x = 0, y = 0):
   mute()
   for card in group:
      card.moveTo(me.hand)
   if len(players) > 1: rnd(1, 100) # Wait a bit more, as in multiplayer games, things are slower.
   notify("{} moves all cards from their {} to its hand.".format(me, group.name))


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


def shuffleIntoDeck(cards, x = 0, y = 0):
   mute()   
   for card in cards:
      toDeckTop(card)
   rnd(100, 10000) # Bug 105 workaround. This delays the next action until all animation is done.
   shuffle(me.Deck)


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

   
def changeSlot(card, x = 0, y = 0):
   debug(">>> changeSlot {}".format(card)) #Debug
   mute()
   cardSlot = getSlotIdx(card, card.controller)
   if cardSlot == -1:
      warning(MSG_SEL_CHAR_RING)
      return
   targets = getTargetedCards(card, True, card.controller == me)
   if len(targets) > 0:
      target = targets[0]
      targetSlot = getSlotIdx(target, target.controller)
      if targetSlot == -1:
         warning(MSG_SEL_CHAR_RING)
         return
      putAtSlot(card, targetSlot, card.controller)
      putAtSlot(target, cardSlot, target.controller)
      alignCard(card)
      alignCard(target)
      target.target(False)
      notify("{} swapped positions of {} and {}.".format(me, card, target))
   else:
      slotIdx = askForSlot(card.controller)
      if slotIdx > -1:
         putAtSlot(card, slotIdx, card.controller, True)
         alignCard(card)
         notify("{} moved {} to slot {}.".format(me, card, slotIdx+1))
      

#---------------------------------------------------------------------------
# Marker actions
#---------------------------------------------------------------------------

# --------------
# Characters' BP
# --------------
def plusBP(cards, x = 0, y = 0, silent = False, count = 1):
   mute()
   for card in cards:
      addMarker(card, 'BP', count)
      if not silent:
         notify("{} raises {}'s BP by {} (new BP is {})".format(me, card, count, getMarker(card, 'BP')))

def minusBP(cards, x = 0, y = 0, silent = False, count = 1):
   mute()
   for card in cards:
      c = count
      bp = getMarker(card, 'BP')
      if c > bp:
         c = bp
      addMarker(card, 'BP', -c)
      if not silent:
         notify("{} lowers {}'s BP by {} (new BP is {}).".format(me, card, count, getMarker(card, 'BP')))
      
def plusBP2(cards, x = 0, y = 0): plusBP(cards, count = 2)
def plusBP3(cards, x = 0, y = 0): plusBP(cards, count = 3)
def plusBP4(cards, x = 0, y = 0): plusBP(cards, count = 4)
def plusBP5(cards, x = 0, y = 0): plusBP(cards, count = 5)
def plusBP6(cards, x = 0, y = 0): plusBP(cards, count = 6)
def plusBP7(cards, x = 0, y = 0): plusBP(cards, count = 7)
def plusBP8(cards, x = 0, y = 0): plusBP(cards, count = 8)
def plusBP9(cards, x = 0, y = 0): plusBP(cards, count = 9)

def plusBPX(cards, x = 0, y = 0):
   n = askInteger("Raise BP by...", 1)
   if n == None: return
   plusBP(cards, count = n)
   
def minusBP2(cards, x = 0, y = 0): minusBP(cards, count = 2)
def minusBP3(cards, x = 0, y = 0): minusBP(cards, count = 3)
def minusBP4(cards, x = 0, y = 0): minusBP(cards, count = 4)
def minusBP5(cards, x = 0, y = 0): minusBP(cards, count = 5)
def minusBP6(cards, x = 0, y = 0): minusBP(cards, count = 6)
def minusBP7(cards, x = 0, y = 0): minusBP(cards, count = 7)
def minusBP8(cards, x = 0, y = 0): minusBP(cards, count = 8)
def minusBP9(cards, x = 0, y = 0): minusBP(cards, count = 9)

def minusBPX(cards, x = 0, y = 0):
   n = askInteger("Lower BP by...", 1)
   if n == None: return
   minusBP(cards, count = n)

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
      slot = " in slot {}".format(getSlotIdx(card)+1)
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
   group = card.group
   card.moveTo(me.piles['Discard Pile'])
   notify("{} has discarded {} from its {}.".format(me, card, group.name))


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
      count = askInteger("How many cards do you want to draw?", handSize) # Ask the player how many cards they want.
   if count == None:
      return
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
   randomDraw(group, CharType)
   
   
def randomDrawAC(group = me.Deck):
   randomDraw(group, ActionType)
   
   
def randomDrawRE(group = me.Deck):
   randomDraw(group, ReactionType)


def trash(group = me.Deck, x = 0, y = 0, silent = False):
# Draws one or more cards from the deck into the discard pile
   mute()
   if len(group) == 0:
      return
   global defTrashCount
   count = askInteger("How many cards do you want to trash?", defTrashCount)
   if count == None:
      return
   defTrashCount = count
   discards = me.piles['Discard Pile']
   for card in group.top(count):
      card.moveTo(discards)
   if len(players) > 1: rnd(1, 100)  # Wait a bit more, as in multiplayer games, things are slower.
   if not silent:
      notify("{} trash top {} cards {}.".format(me, count, fromWhereStr(group)))


def prophecy(group = me.Deck, x = 0, y = 0):
   mute()
   if len(group) == 0:
      return
   global defProphecyCount
   count = askInteger("How many cards do you want to see?", defProphecyCount)
   if count == None:
      return
   defProphecyCount = count
   cards = [c for c in group[:count]]
   cardsPos = []
   while len(cards) > 0:
      card = showCardDlg(cards, "Select a card to put on top or bottom of the deck")
      if card == None:
         return
      card = card[0]
      choice = askChoice("Put {} on top or bottom of the deck?".format(card.Name), ['Top', 'Bottom'])
      if choice == 0:
         return
      cards.remove(card)
      cardsPos.append((card, choice))
   fromText = fromWhereStr(group)
   for item in cardsPos:
      card = item[0]
      choice = item[1]
      cardname = card.Name if card.isFaceUp else "a card"
      if choice == 1:         
         card.moveTo(me.Deck)
         notify("{} puts {} {} on the top of its Deck.".format(me, cardname, fromText))
      else:      
         card.moveToBottom(me.Deck)
         notify("{} puts {} {} on the bottom of its Deck.".format(me, cardname, fromText))


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
   rnd(100, 10000) # Bug 105 workaround. This delays the next action until all animation is done.
               # see https://octgn.16bugs.com/projects/3602/bugs/102681
   Deck.shuffle() # Then use the built-in shuffle action
   notify("{} reshuffled its {} into its Deck.".format(me, group.name)) # And inform everyone.
   

def reshuffleCards(group, cardType):
# Reshuffles all the cards of the given type into the player's deck
   Deck = me.Deck
   for card in group:
      if card.Type == cardType:
         card.moveTo(Deck) # Move the player's cards from the discard to its deck one-by-one.
   update()  # Trying this method to delay next actions until networked tasks are complete
   Deck.shuffle()
   notify("{} shuffles all {} cards from his {} into its Deck.".format(me, cardType, group.name)) # And inform everyone.
   

def reshuffleCHA(group = me.piles['Discard Pile']):
   mute()
   reshuffleCards(group, CharType)

def reshuffleAC(group = me.piles['Discard Pile']):
   mute()
   reshuffleCards(group, ActionType)

def reshuffleRE(group = me.piles['Discard Pile']):
   mute()
   reshuffleCards(group, ReactionType)
   

def revealTopDeck(group, x = 0, y = 0):
   mute()
   if group[0].isFaceUp:
      notify("{} hides {} from top of Library.".format(me, group[0]))
      group[0].isFaceUp = False
   else:
      group[0].isFaceUp = True
      notify("{} reveals {} from top of Library.".format(me, group[0]))


def swapWithDeck(group = me.piles['Discard Pile']):
   swapPiles(me.Deck, group)

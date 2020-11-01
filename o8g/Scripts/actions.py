# Python Scripts for the Card Fighters' Clash definition for OCTGN
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

def nextPhase(fromKeyStroke = True, x = 0, y = 0):
   global phaseOngoing
   if fromKeyStroke and phaseOngoing and settings['Play'] and me.isActive:
      return
      
   phaseIdx = currentPhase()[1]
      
   if tutorial and tutorial.validate == phaseIdx and fromKeyStroke:
      tutorial.goNext()
      return
   
   # if me.isActive:
   if getState(None, 'activePlayer') == me._id:
      if phaseIdx == BlockPhase and getState(None, 'priority') != me._id:
         whisper('You cannot go to the next phase until {} is done.'.format(getOpp()))
         playSnd('win-warning', True)
         return
      # Priority back to me
      if getState(None, 'priority') != me._id:
         setState(None, 'priority', me._id)
      
      global turns
      if phaseIdx >= CleanupPhase:
         turns -= 1
         if turns <= 0:
            setState(None, 'activePlayer', getOpp()._id)
            nextTurn(getOpp())
         else:
            notify("{} takes another turn".format(me))
            setState(None, 'activePlayer', me._id)
            nextTurn(me)
         return
      else:
         phaseIdx += 1
      setPhase(phaseIdx)
      phaseOngoing = True
   elif phaseIdx == BlockPhase and getState(None, 'priority') == me._id:
      setStop(BlockPhase, False)
      # Pass priority to opponent
      setState(None, 'priority', getOpp()._id)
      notify(MSG_PHASE_DONE.format(me, Phases[phaseIdx], getOpp()))
      notification(MSG_PHASE_DONE.format(me, Phases[phaseIdx], 'you'), player = getOpp())
      removeButton('NextButton')
      # remoteCall(players[1], 'addButton', ['NextButton'])
      remoteCall(players[1], 'nextPhase', [False])
      playSnd('notification')
      
      
def prevPhase(group = table, x = 0, y = 0):
   if me.isActive:
      phaseIdx = currentPhase()[1]
      if phaseIdx > 1:
         setPhase(phaseIdx-1)


def gotoPhase(idx, oldIdx = 0):
   triggerPhaseEvent(idx, oldIdx)


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

def setup(group = table, x = 0, y = 0, silent = False):
# This function is usually the first one the player does
   debug(">>> setup()")
   mute()
   # if not silent:
      # if not confirm("Are you sure you want to setup for a new game?"):
         # return
   chooseSide()
   # We ensure that player has loaded a deck
   if len(me.Deck) == 0:
      warning("Please load a deck first.")
      return
   _extapi.notify(MSG_PHASES[SetupPhase].format(me), Colors.LightBlue, True)
   me.Deck.shuffle()
   notify("{} shuffles their deck.".format(me))
   refill() # We fill the player's play hand to their hand size
   notify("Setup for player {} completed.".format(me))
   # Start the turn of the first player to do the setup
   # if settings['Play'] and not getActivePlayer():
      # me.setActive()


def scoop(group=None, x=0, y=0):
# Reset the game
   debug(">>> reset()")
   mute()
   if group != None and not confirm("Are you sure you want to reset the game?"):
      return
   resetAll()
   myCards = (card for card in table
      if card.controller == me
      and not isUI(card))
   toOwnerDeck(myCards)
   toOwnerDeck(me.Deck)
   toOwnerDeck(me.hand)
   toOwnerDeck(me.piles['Discard pile'])
   toOwnerDeck(me.piles['Removed pile'])
   rnd(100, 10000) # Delays the next action until all animation is done
   setup()
   notify("{} resets the game.".format(me))
   if group != None and len(players) > 1:
      remoteCall(players[1], 'scoop', [])


def flipCoin(group = None, x = 0, y = 0):
   mute()
   sides = ['Heads','Tails']
   notify("{} flips a coin...".format(me))
   choice = askChoice("Call heads or tails", sides)
   if choice == 0:
      choice = 1
   notify("{} has choosen {}".format(me, sides[choice-1]))
   n = rnd(1, 2)
   wins = n == choice
   notify(u" \u2192 flips {} ({}).".format(sides[n-1], ('loses', 'wins')[wins]))
   return wins


def randomPick(group, x = 0, y = 0, fromPlayer = None):
   mute()
   card = None
   player = fromPlayer if fromPlayer != None else me
   if group == table:
      if fromPlayer:
         ring = getRing(player)
      else:
         ring = getRing()
      if(len(ring)) > 0:
         card = ring[rnd(0, len(ring)-1)]
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
   randomPick(group, fromPlayer = me)


def randomPickEnemy(group, x = 0, y = 0):
   if len(players) > 1:
      randomPick(group, fromPlayer = players[1])


def clearAll(group = None, x = 0, y = 0):
   notify("{} clears all targets and highlights.".format(me))
   for card in table:
      if card.controller == me:
         clear(card, group)
   clearSelection()


def alignCards(group = None, x = 0, y = 0):
   for card in getRing():
      alignCard(card)


def switchPlayAuto(group, x = 0, y = 0):
   switchSetting('Play')


def switchPhaseAuto(group, x = 0, y = 0):
   switchSetting('Phase')


def switchActivateAuto(group, x = 0, y = 0):
   switchSetting('Activate')


def switchWinForms(group, x = 0, y = 0):
   switchSetting('WinForms')
   
   
def switchSounds(group, x = 0, y = 0):
   switchSetting('Sounds')
   # Udpate OCTGN preferences
   Octgn.Core.Prefs.EnableGameSound = settings['Sounds']
   
   
def switchWelcomeScreen(group, x = 0, y = 0):
   switchSetting('WelcomeScreen')


#---------------------------------------------------------------------------
# Table card actions
#---------------------------------------------------------------------------

def defaultAction(card, x = 0, y = 0):
   phaseIdx = currentPhase()[1]
   # Button
   if isButton(card):
      buttonAction(card)
   # Avatar
   elif isAvatar(card):
      avatarAction(card)
   # Char Attack
   elif me.isActive and phaseIdx == AttackPhase and isCharacter(card):
      attack(card)
   # Char block
   elif (not me.isActive or tutorial) and phaseIdx == BlockPhase and isCharacter(card):
      block(card)
   # Activate ability/effect
   elif (
         (me.isActive and (isCharacter(card) or isAction(card)))
         or (isReaction(card) and ((not me.isActive and phaseIdx == BlockPhase) or debugging or tutorial))
      ):
      activate(card)


def attack(card, x = 0, y = 0):
   mute()
   if settings['Play']:
      if not attackAuto(card): return
   card.highlight = AttackColor
   playSnd('attack-1')
   notify('{} attacks with {}'.format(me, card))


def attackNoFreeze(card, x = 0, y = 0):
   mute()
   if settings['Play']:
      if not attackAuto(card): return
   card.highlight = AttackNoFreezeColor
   setMarker(card, 'Unfreezable')
   playSnd('attack-1')
   notify('{} attacks with {} (character will not freeze).'.format(me, card))


def unitedAttack(card, x = 0, y = 0, targets = None):
   debug(">>> unitedAttack()")
   mute()
   cardsnames = card
   if settings['Play']:
      target = unitedAttackAuto(card, targets)
      if target:
         cardsnames = '{} and {}'.format(card, target)
      else:
         return
   card.highlight = UnitedAttackColor
   playSnd('attack-2')
   notify('{} does an United Attack with {}.'.format(me, cardsnames))


def block(card, x = 0, y = 0, targets = None):
   mute()
   text = 'with {}'.format(card)
   if settings['Play']:
      target = blockAuto(card, targets)
      if target:
         text = '{} '.format(target) + text
      else:
         return
   card.highlight = BlockColor
   playSnd('block')
   notify('{} counter-attacks {}'.format(me, text))


def activate(card, x = 0, y = 0):
   debug(">>> activate()")
   mute()
   if card.highlight == ActivatedColor and not settings['Play']:
      card.highlight = None
      card.target(None)
      notify("{} deactivates {}.".format(me, card))
      return
   ability = "effect"
   pcard = getParsedCard(card)
   if not pcard.hasEffect():
      whisper("{} has no ability to activate".format(card))
      return
   if isCharacter(card):
      ability = "ability {}".format(pcard.ability)
   notify("{} tries to activate {}'s {}.".format(me, card, ability))
   if settings['Play']:
      res = activateAuto(card)
      if not res or res != True:
         if res == ERR_NO_EFFECT:
            notify("{}'s {} has no effect.".format(card, ability))
            playSnd('cancel-2')
         if (isCharacter(card) and pcard.ability.type == TriggerAbility) or res != ERR_NO_EFFECT:
            return
   elif isCharacter(card) and pcard.ability.type == TriggerAbility:
      freeze(card, silent = True)
   if card.group == table:
      willHighlight = pcard.getState('highlight')
      if willHighlight != False:
         card.highlight = ActivatedColor
      if willHighlight != None:
         pcard.setState('highlight', None)
   if isCharacter(card):
      playSnd('activate-1')
   else:
      playSnd('activate-2')
   notify("{} has activated {}'s {}.".format(me, card, ability))


def freeze(card, x = 0, y = 0, unfreeze = None, silent = False):
   mute()
   if card.group != table:
      return
   initialRot = card.orientation
   if unfreeze != None:
      card.orientation = Rot0 if unfreeze else Rot90
   else:
      card.orientation ^= Rot90
   if card.orientation != initialRot:
      if not silent:
         notify('{} {}freezes {}'.format(me, ('un', '')[isFrozen(card)], card))
      playSnd(('untap','tap')[isFrozen(card)])
   if not isFrozen(card) and card.highlight == ActivatedColor:
      card.highlight = None
      card.target(None)


def doesNotUnfreeze(card, x = 0, y = 0, restr = None):
   debug("doesNotUnfreeze({}, {}, {}, {})".format(card, x, y, restr))
   mute()
   msg = "not unfreeze"
   when = ''
   if not hasMarker(card, 'Cannot Unfreeze'):
      setMarker(card, "Cannot Unfreeze")
      if restr:
         when = 'next '
   else:
      removeMarker(card, "Cannot Unfreeze")
      msg = "unfreeze as normal"

   notify("{0}'s {1} will {2} in {0}'s {3}Activate phase.".format(card.controller, card, msg, when))


def clear(card, x = 0, y = 0):
   card.target(False)
   if settings['Play']:
      # Triggered from the menu
      if x != 0 or y != 0:
         if card.highlight in [InfoColor]:
            card.highlight = None
      else:
         card.highlight = None
   else:
      card.highlight = None


def alignCardAction(card, x = 0, y = 0):
   if isCharacter(card):
      slotIdx = getSlotIdx(card)
      if slotIdx != -1:
         alignCard(card, slotIdx=slotIdx)
      else:
         backups = getGlobalVar('Backups')
         if backups.get(card._id):
            c = Card(backups[card._id])
            alignBackups(c, *c.position)


def askCardBackups(card, x = 0, y = 0):
   if isCharacter(card):
      acceptedBackups = getAcceptedBackups(card)
      inRing = charIsInRing(card)
      charsBackup = []
      msg1 = ''
      msg2 = "{} can be backed-up with the following character types:\n  - {}".format(card.Name, '\n  - '.join(filter(None, acceptedBackups)))
      # Check remaining backups
      avlBackups = list(acceptedBackups) # Copy array
      backups = getGlobalVar('Backups')
      for id in backups:
         if backups[id] == card._id:
            avlBackups.remove(Card(id).Subtype)
      if inRing and len(avlBackups) < len(acceptedBackups):
         msg2 += "\n\nRemaining backups: {}.".format(", ".join(avlBackups))
      # Candidates to back-up in the hand
      for c in me.hand:
         if isCharacter(c):
            if c != card and c.Subtype in avlBackups:
               c.highlight = InfoColor
               charsBackup.append(c)
            elif c.highlight == InfoColor:
               c.highlight = None
      if len(charsBackup) > 0:
         if inRing:
            targets = showCardDlg(charsBackup, 'Select a character card from your hand to back-up {}'.format(card.Name))
            if targets:
               backup(targets[0], target=card)
         whisper("Highlighting compatible back-ups cards in your hand: {}.".format(cardsNamesStr(charsBackup)))
      else:
         if inRing:
            msg1 = "You don't have compatible character cards in your hand to backup {}.\n\n".format(card.Name)
      whisper(msg2)
      if not inRing or len(charsBackup) == 0:
         information(msg1 + msg2)
   else:
      information("Only character cards can be backed-up.")


def transformCards(cards, x = 0, y = 0):
   mute()
   cardModel = None
   targets =  [c for c in table   if c.targetedBy == me]
   targets += [c for c in me.hand if c.targetedBy == me]
   targets += [c for c in me.piles['Discard pile'] if c.targetedBy == me]
   if len(players) > 1:
      targets += [c for c in players[1].piles['Discard pile'] if c.targetedBy == me]
   if len(targets) > 0:
      cardModel = targets[0].model
   else:
      cardtype = cards[0].Type
      card, quantity = askCard({"Type":cardtype}, "and", "Target character will be transformed into choosen card.")
      if quantity > 0:
         cardModel = card
   if cardModel:
      for card in cards:
         transformCard(card, cardModel)
      for target in targets:
         target.target(False)

         
def toggleAbility(card, x = 0, y = 0, remove = False):
   mute()
   if not isCharacter(card) or (card.alternate == '' and card.Rules == ''):
      return
   # Restores ability
   if card.alternate == 'noability' and not remove:
      card.alternate = ''
      # Removes card from parsed list to parse it again with the new abilities
      for p in players:
         funcCall(p, removeParsedCard, [card])
      funcCall(card.controller, parseCard, [card])
      if card.Rules != '':
         notify("{} restores {}'s abilities".format(me, card))
      else:
         notify("{} tried to restore {}'s abilities, but it doesn't have any original ability".format(me, card))
   # Removes ability
   else:
      triggerGameEvent([GameEvents.Powerless, card._id])
      for p in players:
         funcCall(p, removeParsedCard, [card])
      CharsAbilities = getGlobalVar('CharsAbilities')
      if card._id in CharsAbilities:
         del CharsAbilities[card._id]
      setGlobalVar('CharsAbilities', CharsAbilities)
      if 'Model' in card.properties:
         card.properties['Model'] = None
      if 'noability' in card.alternates:
         card.alternate = 'noability'
      else:
         # Updates proxy image for all players
         for p in players:
            funcCall(p, addAlternateRules, [card, '', '', 'noability'])
      notify("{} removes {}'s abilities".format(me, card))


def copyAbility(card, x = 0, y = 0, target = None):
   debug(">>> copyAbility({}, {})".format(card, target))
   mute()
   if not isCharacter(card):
      warning('Abilities can only be copied to character cards.')
      return
   if target == None:
      targets =  [c for c in table   if c.targetedBy == me]
      targets += [c for c in me.hand if c.targetedBy == me]
      targets += [c for c in me.piles['Discard pile'] if c.targetedBy == me]
      if len(targets) > 0 and isCharacter(targets[0]) and targets[0] != card:
         target = targets[0]
      else:
         choice = askChoice('From where do you want to copy an ability?', ['Arena', 'Hand', 'My discard pile'])
         if choice == 0:
            return
         if choice == 1:
            pile = getRing()
         elif choice == 2:
            pile = me.hand
         else:
            pile = me.piles['Discard pile']
         cards = [c for c in pile
                  if c.Rules != ""
                  and isCharacter(c)
                  and c != card]
         choosenCards = showCardDlg(cards, 'Choose a character with an ability to copy')
         if choosenCards:
            target = choosenCards[0]
         else:
            return
   if target:
      result = copyAlternateRules(card, target)
      if result:
         CharsAbilities = getGlobalVar('CharsAbilities')
         model = target.model
         if isinstance(target, Card):
            if target._id in CharsAbilities:
               model = CharsAbilities[target._id]
         CharsAbilities[card._id] = model
         setGlobalVar('CharsAbilities', CharsAbilities)
         triggerGameEvent([GameEvents.Powerless, card._id])
         # Updates proxy image for the other players
         if len(players) > 1:
            for p in players:
               if p != me:
                  remoteCall(p, "copyAlternateRules", [card, target])
         update()  # Trying this method to delay next actions until networked tasks are complete
         for p in players:
            funcCall(p, removeParsedCard, [card])
         funcCall(card.controller, parseCard, [card, model])
         if target.Ability.split(' ')[0] != InstantAbility:
            if card.highlight == ActivatedColor:
               card.highlight = None
         notify("{} copies ability {} to {}.".format(me, target.Ability, card))
         return target
      else:
         warning("Target card doesn't have an ability to copy.")
   else:
      warning("Please select a valid character card.")
   debug("<<< copyAbility()")


def swapAbilities(card, x = 0, y = 0, target = None):
   debug(">>> swapAbilities({}, {})".format(card, target))
   mute()
   if not isCharacter(card) or not charIsInRing(card, card.controller) or not card.Rules:
      whisper("Abilities can only be swapped between character cards with abilities in the arena.")
      return
   if not target:
      targets = [c for c in table if c.targetedBy == me]
      if len(targets) == 0:
         cards = [c for c in getRing() if c.Rules != "" and c != card]
         targets = showCardDlg(cards, "Choose a character with an ability")
         if targets == None:
            return
      target = targets[0]
   model = card.model
   CharsAbilities = getGlobalVar('CharsAbilities')
   card_copy = Struct(**{
      'Rules'  : card.Rules,
      'Ability': card.Ability,
      'model'  : CharsAbilities[card._id] if card._id in CharsAbilities else card.model
   })
   copyAbility(card,   target = target)
   copyAbility(target, target = card_copy)
   target.target(False)
   notify("{} has swapped abilities between {} and {}".format(me, card, target))
      
      
def stealAbility(card, x = 0, y = 0, target = None):
   target = copyAbility(card, target = target)
   if target:
      ability = getParsedCard(target).ability.name
      toggleAbility(target, remove=True)
      notify("{} steals ability {} from {} and gives it to {}.".format(me, ability, target, card))

   
#---------------------------------------------------------------------------
# Movement actions
#---------------------------------------------------------------------------

def destroy(card, x = 0, y = 0, controller=me):
   mute()
   if isUI(card) and not debugging:
      return
   fromText = fromWhereStr(card.group)
   action = "discards"
   card.moveTo(me.piles['Discard pile'])
   if isCharacter(card):
      action = "KOs"
      playSnd('ko-1')
   else:
      playSnd('ko-2')
   if card.orientation != Rot0:
      card.orientation = Rot0
   notify("{} {} {} {}.".format(controller, action, card, fromText))


def remove(card, x = 0, y = 0):
   mute()
   fromText = fromWhereStr(card.group)
   card.moveTo(me.piles['Removed pile'])
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
   discards = me.piles['Discard pile']
   for card in group:
      card.moveTo(discards)
   if len(players) > 1: rnd(1, 100) # Wait a bit more, as in multiplayer games, things are slower.
   notify("{} moved all cards from their {} to its discard pile.".format(me, group.name))


def removeAll(group, x = 0, y = 0):
   mute()
   pile = me.piles['Removed pile']
   for card in group:
      card.moveTo(pile)
   if len(players) > 1: rnd(1, 100) # Wait a bit more, as in multiplayer games, things are slower.
   notify("{} moved all cards from their {} to its removed pile.".format(me, group.name))


def toTableFaceDown(card, x = 0, y = 0):
   debug(">>> toTableFaceDown {}".format(card))
   mute()
   fromText = fromWhereStr(card.group)
   placeCard(card, card.Type, faceDown=True)
   notify("{} puts a card face down in the Arena {}.".format(me, fromText))


def changeSlot(card, x = 0, y = 0, targets = None):
   debug(">>> changeSlot {}".format(card))
   mute()
   cardSlot = getSlotIdx(card, card.controller)
   if cardSlot == -1:
      warning(MSG_SEL_CHAR_RING)
      return
   if not targets:
      targets = getTargetedCards(card, True, card.controller == me)
   if len(targets) > 0:
      target = targets[0]
      targetSlot = getSlotIdx(target, target.controller)
      if targetSlot == -1:
         warning(MSG_SEL_CHAR_RING)
         return
      if target.controller != target.controller:
         whisper("You can only swap exactly two characters in the same ring.")
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
def plusBP(cards, x = 0, y = 0, silent = False, count = 100):
   mute()
   for card in cards:
      addMarker(card, 'BP', count)
      if not silent:
         notify("{} raises {}'s BP by {} (new BP is {})".format(me, card, count, getMarker(card, 'BP')))

def minusBP(cards, x = 0, y = 0, silent = False, count = 100):
   mute()
   for card in cards:
      c = count
      bp = getMarker(card, 'BP')
      if c > bp:
         c = bp
      addMarker(card, 'BP', -c)
      if not silent:
         notify("{} lowers {}'s BP by {} (new BP is {}).".format(me, card, count, getMarker(card, 'BP')))

def plusBP2(cards, x = 0, y = 0): plusBP(cards, count = 200)
def plusBP3(cards, x = 0, y = 0): plusBP(cards, count = 300)
def plusBP4(cards, x = 0, y = 0): plusBP(cards, count = 400)
def plusBP5(cards, x = 0, y = 0): plusBP(cards, count = 500)
def plusBP6(cards, x = 0, y = 0): plusBP(cards, count = 600)
def plusBP7(cards, x = 0, y = 0): plusBP(cards, count = 700)
def plusBP8(cards, x = 0, y = 0): plusBP(cards, count = 800)
def plusBP9(cards, x = 0, y = 0): plusBP(cards, count = 900)

def plusBPX(cards, x = 0, y = 0):
   n = askInteger("Raise BP by...", 100)
   if n == None: return
   plusBP(cards, count = fixBP(n))

def minusBP2(cards, x = 0, y = 0): minusBP(cards, count = 200)
def minusBP3(cards, x = 0, y = 0): minusBP(cards, count = 300)
def minusBP4(cards, x = 0, y = 0): minusBP(cards, count = 400)
def minusBP5(cards, x = 0, y = 0): minusBP(cards, count = 500)
def minusBP6(cards, x = 0, y = 0): minusBP(cards, count = 600)
def minusBP7(cards, x = 0, y = 0): minusBP(cards, count = 700)
def minusBP8(cards, x = 0, y = 0): minusBP(cards, count = 800)
def minusBP9(cards, x = 0, y = 0): minusBP(cards, count = 900)

def minusBPX(cards, x = 0, y = 0):
   n = askInteger("Lower BP by...", 100)
   if n == None: return
   minusBP(cards, count = fixBP(n))

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

def play(card, x = 0, y = 0, slotIdx=None):  # This is the function to play cards from your hand.
   debug(">>> playing card {} at {}".format(card, slotIdx))

   mute()
   chooseSide()
   slot = ""
   group = card.group
   if settings['Play']:
      if not playAuto(card, slotIdx):
         return False
      slot = " in slot {}".format(getSlotIdx(card)+1)
   else:
      placeCard(card, card.Type)
   isChar = isCharacter(card)
   if isChar:
      notify("{} plays {} from their {}{}.".format(me, card, group.name, slot))
      charsPlayed = getState(me, 'charsPlayed')
      playSnd('card-play-1')
      notify("({} has played {} character{} this turn.)".format(me, charsPlayed, plural(charsPlayed)))
   else:
      playSnd('card-play-2')
      notify("{} plays {} from their {}.".format(me, card, group.name))
      
   if settings['Play']:
      pcard = getParsedCard(card)
      if isChar and pcard.hasEffect() and pcard.ability.type == InstantAbility or not isChar:
         if settings['Activate']:
            # Trying to delay activation {
            rnd(10, 1000)
            update()
            rnd(10, 1000)
            update()
            # }
            activate(card)
         else:
            whisper(MSG_HINT_ACTIVATE)

   debug("<<< playing card end")


def backup(card, x = 0, y = 0, target = None):  # Play a card as backup attached to a character in the player's ring
   debug(">>> backup with card {}".format(card))
   mute()
   group = card.group
   if settings['Play']:
      target = backupAuto(card, target)
      if target:
         target, oldBP = target
         newBP = getMarker(target, 'BP')
         notify("{0} backups {1} with {2} from their {3}. New BP of {1} is {4} (before was {5}).".format(me, target, card, group.name, newBP, oldBP))
         playSnd('backup')
         return True
   else:
      placeCard(card, card.Type)
      notify("{} backups with {} from their {}.".format(me, card, group.name))
      playSnd('backup')


def discard(card, x = 0, y = 0, isRandom = False):
   if isUI(card):
      return
   mute()
   group = card.group
   card.moveTo(me.piles['Discard pile'])
   msg = "{} has discarded {} from their {}."
   if group != me.hand:
      msg = "{} puts {} into his discard pile."
   if isRandom:
      msg = MSG_DISCARD_RANDOM
   playSnd('discard')
   notify(msg.format(me, card, group.name))


def randomDiscard(group = me.hand, x = 0, y = 0):
    mute()
    card = group.random()
    if card == None:
        return
    card.moveTo(me.piles['Discard pile'])
    notify(MSG_DISCARD_RANDOM.format(me, card, group.name))


def refill(group = me.hand):  # Refill the player's hand to its hand size.
   playhand = len(me.hand) # count how many cards there are currently there.
   if playhand < handSize:
      drawMany(me.Deck, handSize - playhand) # If there's less cards than the handSize, draw from the deck until it's full.


#---------------------------------------------------------------------------
# Piles actions
#---------------------------------------------------------------------------

def draw(group = me.Deck):  # Draws one card from the deck into the player's hand.
   mute()
   if len(group) == 0:
      whisper("You can't draw cards from an empty {}.".format(group.name))
      return
   group.top().moveTo(me.hand)
   playSnd('draw')
   notify("{} draws a card.".format(me))


def drawMany(group, count = None, silent = False):  # This function draws a variable number cards into the player's hand.
   mute()
   if len(group) == 0:
      whisper("Can't draw cards from an empty {}.".format(group.name))
      return
   if count == None:
      count = askInteger("How many cards do you want to draw?", handSize) # Ask the player how many cards they want.
   if count == None:
      return
   drawn = 0
   for i in range(0, count):
      if len(group) > 0:  # If the deck is not empty...
         group.top().moveTo(me.hand)  # ...then move them one by one into their play hand.
         drawn += 1
   if not silent:
      notify("{} draws {} card{}.".format(me, drawn, plural(drawn)))
   playSnd('draw')


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


def trash(group, x = 0, y = 0, silent = False, count = None):
# Draws one or more cards from the deck into the discard pile
   mute()
   if group is None:
      group = me.Deck
   global defTrashCount
   if count == None:
      count = askInteger("How many cards do you want to trash?", defTrashCount)
   if count == None:
      return
   defTrashCount = count
   discards = me.piles['Discard pile']
   cards = []
   for card in group.top(count):
      card.moveTo(discards)
      cards.append(card)
   # Add trashed card to action local variables
   addTempVar('trashed', cards)
   if len(players) > 1: rnd(1, 100)  # Wait a bit more, as in multiplayer games, things are slower.
   if not silent:
      notify("{} trashes top {} cards {}.".format(me, count, fromWhereStr(group)))


def prophecy(group = me.Deck, x = 0, y = 0, count = None, deckPos = 0):
   mute()
   if len(group) == 0:
      return
   global defProphecyCount
   if not count:
      count = askInteger("How many cards do you want to see?", defProphecyCount)
      if count == None:
         return
   defProphecyCount = count
   cards = [c for c in group[:count]]
   cardsPos = []
   owner = 'his' if group.controller == me else "{}'s".format(group.controller)
   notify(MSG_PLAYER_LOOKS.format(me, owner, group.name))
   while len(cards) > 0:
      card = showCardDlg(cards, "Select a card to put on {} of the deck".format(["top or bottom", "top", "bottom"][deckPos]))
      if card == None:
         return
      card = card[0]
      # Allow the player to first see the cards, and then choose where to put them
      if not deckPos:
         deckPos = askChoice("Where to put the card?", ['Top of deck', 'Bottom of deck'])
         if deckPos == 0:
            return
      cards.remove(card)
      cardsPos.append((card, deckPos))
   for item in cardsPos:
      card = item[0]
      pos = (item[1] - 1) * -1
      if group.controller == me:
         moveToGroup(group, card, pos = pos, reveal = False)
      else:
         remoteCall(group.controller, "moveToGroup", [group, card, group, pos, False, me])


def shuffle(group):
# A simple function to shuffle piles
   mute()
   for card in group:
      if card.isFaceUp:
         card.isFaceUp = False
   group.shuffle()
   playSnd('shuffle')
   notify("{} shuffled its {}".format(me, group.name))


def reshuffle(group = me.piles['Discard pile']):
# This function reshuffles the player's discard pile into its deck.
   mute()
   Deck = me.Deck
   for card in group:
      card.moveTo(Deck) # Move the player's cards from the discard to its deck one-by-one.
   rnd(100, 10000) # Bug 105 workaround. This delays the next action until all animation is done.
               # see https://octgn.16bugs.com/projects/3602/bugs/102681
   Deck.shuffle() # Then use the built-in shuffle action
   playSnd('shuffle')
   notify("{} reshuffled its {} into its Deck.".format(me, group.name)) # And inform everyone.


def reshuffleCards(group, cardType):
# Reshuffles all the cards of the given type into the player's deck
   Deck = me.Deck
   for card in group:
      if card.Type == cardType:
         card.moveTo(Deck) # Move the player's cards from the discard to its deck one-by-one.
   update()  # Trying this method to delay next actions until networked tasks are complete
   Deck.shuffle()
   playSnd('shuffle')
   notify("{} shuffles all {} cards from his {} into its Deck.".format(me, cardType, group.name)) # And inform everyone.


def reshuffleCHA(group = me.piles['Discard pile']):
   mute()
   reshuffleCards(group, CharType)

def reshuffleAC(group = me.piles['Discard pile']):
   mute()
   reshuffleCards(group, ActionType)

def reshuffleRE(group = me.piles['Discard pile']):
   mute()
   reshuffleCards(group, ReactionType)


def revealTopDeck(group, x = 0, y = 0):
   mute()
   if group[0].isFaceUp:
      notify("{} hides {} from the top of their Deck.".format(me, group[0]))
      group[0].isFaceUp = False
   else:
      group[0].isFaceUp = True
      notify("{} reveals {} from the top of their Deck.".format(me, group[0]))


def swapWithDeck(group = me.piles['Discard pile']):
   swapPiles(me.Deck, group)


def removedDefaultAction(card, x = 0, y = 0):
   if me.isActive and currentPhase()[1] == MainPhase and getRule('play_removed'):
      play(card)
   else:
      toHand(card)
      

#---------------------------------------------------------------------------
# Debug actions
#---------------------------------------------------------------------------

def setupDebug(group, x=0, y=0):
   mute()
   global debugging
   debugging = True
   resetGame()


def setDebugVerbosity(group=None, x=0, y=0):
   global debugVerbosity
   mute()
   levels = DebugLevel.keys()
   choice = askChoice("Set debug verbosity to: (current is {})".format(levels[debugVerbosity]), levels)
   if choice == 0:
      return
   debugVerbosity = choice - 1
   whisper("Debug verbosity is now: {} ({})".format(levels[debugVerbosity], debugVerbosity))


def createCard(group, x=0, y=0):
   id, quantity = askCard(title = 'Choose a card to add to the game')
   if quantity > 0:
      card = table.create(id, 0, 0, quantity=quantity, persist=True)
      notify("{} has created the card {}".format(me, card))

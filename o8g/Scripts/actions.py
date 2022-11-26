# Python Scripts for the Card Fighters' Clash definition for OCTGN
# Copyright (C) 2013 Raohmaru

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

# Functions in this file correspond to the actions the player can execute, defined in definition.xml.

import re

#---------------------------------------------------------------------------
# Phase actions
#---------------------------------------------------------------------------

def nextPhase(fromKeyStroke = True, x = 0, y = 0):
   global isPhaseOngoing
   if fromKeyStroke and isPhaseOngoing and settings["PlayAuto"] and me.isActive:
      return
      
   phaseIdx = getCurrentPhase()
      
   # If playing the tutorial we go to the next tutorial phase instead
   if tutorial and tutorial.validatePhase == phaseIdx and fromKeyStroke:
      tutorial.goNextStep()
      return
   
   # If I am the active player
   if getState(None, "activePlayer") == me._id:
      # Opp has the priority, we cannot advance
      if phaseIdx == BlockPhase and getState(None, "priority") != me._id:
         whisper(MSG_PHASE_LOCK.format(getOpp()))
         playSnd("win-warning", True)
         return
      # We reached the last phase
      if phaseIdx >= CleanupPhase:
         me.turnsRemaining -= 1
         if me.turnsRemaining <= 0:
            setState(None, "activePlayer", getOpp()._id)
            nextTurn(getOpp())
         else:
            notify("{} takes another turn", me)
            setState(None, "activePlayer", me._id)
            nextTurn(me)
         return
      else:
         phaseIdx += 1
      
      setPhase(phaseIdx)
      isPhaseOngoing = True
   # If I am not the active player but it is the Block phase
   elif phaseIdx == BlockPhase and getState(None, "priority") == me._id:
      # Pass priority to opponent
      setState(None, "priority", getOpp()._id)
      notify(MSG_PHASE_DONE, me, PhaseNames[phaseIdx], getOpp())
      notification(MSG_PHASE_DONE.format(me, PhaseNames[phaseIdx], "you"), playerList = [getOpp()])
      removeButton(NextButton)
      remoteCall(players[1], "nextPhase", [False])
      playSnd("notification")
      
      
def prevPhase(group = table, x = 0, y = 0):
   if me.isActive:
      phaseIdx = getCurrentPhase()
      if phaseIdx > 1:
         setPhase(phaseIdx - 1)


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

def setup(group = table, x = 0, y = 0):
   """
   Game setup. It should be the first function to invoke to start a game.
   """
   debug(">>> setup()")
   # We ensure that player has loaded a deck
   if len(me.Deck) == 0:
      warning(MSG_ACTION_LOAD_DECK)
      return
   if not me.setupDone:
      _extapi.notify(MSG_PHASES[SetupPhase].format(me), Colors.LightBlue, True)
      shuffle(me.Deck)
      refillHand() # We fill the player's hand to their hand size
      notify("Setup for player {} completed.", me)
      me.setupDone = True
   else:
      me.setActive()


def restart(isRemote = False, x = 0, y = 0):
   debug(">>> restart()")
   if not isRemote and not confirm("Are you sure you want to restart the game?"):
      return
   resetAll()
   # Get all my cards in the table
   myCards = (card for card in table
      if card.controller == me and not isUI(card))
   toOwnerDeck(myCards)
   toOwnerDeck(me.Deck)
   toOwnerDeck(me.hand)
   toOwnerDeck(me.piles["Discard pile"])
   toOwnerDeck(me.piles["Removed pile"])
   waitForAnimation()
   setup()
   notify("{} restarts the game.", me)
   if not isRemote and len(players) > 1:
      remoteCall(players[1], "restart", [])


def flipCoin(group = None, x = 0, y = 0):
   sides = ["Heads", "Tails"]
   notify("{} flips a coin...", me)
   choice = askChoice("Call heads or tails", sides)
   # askChoice() returns 0 if the window is closed
   choice = choice - 1
   if choice == -1:
      choice = 0
   notify("{} has choosen {}", me, sides[choice])
   n = rnd(0, 1)
   wins = n == choice
   notify(u"\u2192 flips {} ({}).".format(sides[n], ("loses", "wins")[wins]))
   return wins


def randomPick(group, x = 0, y = 0, fromPlayer = None):
   """
   Randomly picks a card from the given group.
   """
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
   revealCard(card)
   if group == table:
      notify("{} randomly selects {}'s {} on the ring.", me, card.controller, card)
   else:
      notify("{} randomly selects {} from their {}.", me, card, group.name)


def randomPickMine(group, x = 0, y = 0):
   randomPick(group, fromPlayer = me)


def randomPickEnemy(group, x = 0, y = 0):
   if len(players) > 1:
      randomPick(group, fromPlayer = players[1])


def clearAll(group = None, x = 0, y = 0):
   """
   Clear selections on all cards
   """
   notify("{} clears all selections, targets and highlights.", me)
   for card in getCards(group):
      clear(card)
   clearSelection()


def alignCards(group = None, x = 0, y = 0):
   """
   Arranges cards in the table according to the grid.
   """
   for card in getRing():
      alignCard(card)


#---------------------------------------------------------------------------
# Settings
#---------------------------------------------------------------------------

def switchPlayAuto(group, x = 0, y = 0):
   switchSetting("PlayAuto")


def switchPhaseAuto(group, x = 0, y = 0):
   switchSetting("PhaseAuto")


def switchActivateAuto(group, x = 0, y = 0):
   switchSetting("Activate")


def switchWinForms(group, x = 0, y = 0):
   switchSetting("WinForms")
   
   
def switchSounds(group, x = 0, y = 0):
   switchSetting("Sounds")
   # Updates OCTGN preferences
   Octgn.Core.Prefs.EnableGameSound = settings["Sounds"]
   
   
def switchWelcomeScreen(group, x = 0, y = 0):
   switchSetting("WelcomeScreen")


def resetDoNotShowAgain(group, x = 0, y = 0):
   doNotShow = settings["DoNotShow"].copy()
   doNotShow.clear()
   switchSetting("DoNotShow", doNotShow)
   whisper("Restored \"Do not show again\" dialogs. Hidden notifications will appear again.")


#---------------------------------------------------------------------------
# Table card actions
#---------------------------------------------------------------------------

def defaultAction(card, x = 0, y = 0):
   """
   Changes the action of the first item of the contextual menu (which is also activated with double click)
   depending on the context.
   """
   phaseIdx = getCurrentPhase()
   # Button
   if isButton(card):
      buttonAction(card)
   # Avatar
   elif isAvatar(card):
      avatarAction(card)
   # Char attack
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
   if settings["PlayAuto"]:
      if not attackAuto(card):
         return
   card.highlight = AttackColor
   playSnd("attack-1")
   notify(MSG_ACTION_ATTACK, me, card)


def attackNoFreeze(card, x = 0, y = 0):
   if settings["PlayAuto"]:
      if not attackAuto(card):
         return
   card.highlight = AttackNoFreezeColor
   setMarker(card, "Unfreezable")
   playSnd("attack-1")
   notify(MSG_ACTION_ATTACK_NOFREEZE, me, card)


def unitedAttack(card, x = 0, y = 0, targets = None):
   debug(">>> unitedAttack()")
   cardsnames = card
   if settings["PlayAuto"]:
      target = unitedAttackAuto(card, targets)
      if target:
         cardsnames = "{} and {}".format(card, target)
      else:
         return
   card.highlight = UnitedAttackColor
   playSnd("attack-2")
   notify("{} does an United Attack with {}.", me, cardsnames)


def block(card, x = 0, y = 0, targets = None):
   withChar = "with {}".format(card)
   if settings["PlayAuto"]:
      target = blockAuto(card, targets)
      if target:
         withChar = "{} ".format(target) + withChar
      else:
         notify("{} cannot counter-attack due to an ability or effect.", card)
         return
   card.highlight = BlockColor
   playSnd("block")
   notify("{} counter-attacks {}.", me, withChar)


def activate(card, x = 0, y = 0):
   debug(">>> activate()")
   mute()
   # Action can toggle the activated state when play automations are off
   if card.highlight == ActivatedColor and not settings["PlayAuto"]:
      card.highlight = None
      card.target(None)
      notify("{} deactivates {}.", me, card)
      return
   pcard = getGameCard(card)
   if not pcard.hasEffect():
      whisper("{} has no ability to activate.".format(card))
      return
   ability = "effect"
   if isCharacter(card):
      ability = "ability {}".format(pcard.ability)
   notify("{} tries to activate {}'s {}.", me, card, ability)
   if settings["PlayAuto"]:
      res = activateAuto(card)
      # Nothing happened
      if not res or res != True:
         if res == ERR_NO_EFFECT:
            notify("{}'s {} has no effect.", card, ability)
            playSnd("cancel-2")
         if (isCharacter(card) and pcard.ability.type == TriggerAbility) or res != ERR_NO_EFFECT:
            return
   # Freeze char if it's a triggered ability
   elif isCharacter(card) and pcard.ability.type == TriggerAbility:
      freeze(card, silent = True)
   # Apply highlight
   if card.group == table:
      # Get again the parsed card in case its rules changed
      pcard = getGameCard(card)
      if pcard.getState("willHighlight") == True:
         card.highlight = ActivatedColor
      else:
         pcard.setState("willHighlight", True)
   if isCharacter(card):
      playSnd("activate-1")
   else:
      playSnd("activate-2")
   notify("{} has activated {}'s {}.", me, card, ability)


def freeze(card, x = 0, y = 0, unfreeze = None, silent = False):
   """
   Rotates (taps or untaps) a card.
   """
   mute()
   if card.group != table:
      return
   initialRot = card.orientation
   if unfreeze != None:
      card.orientation = Rot0 if unfreeze else Rot90
   else:
      # Toggle rotation
      card.orientation ^= Rot90
   if card.orientation != initialRot:
      if not silent:
         notify("{} {}freezes {}".format(me, ("un", "")[isFrozen(card)], card))
      playSnd(("untap", "tap")[isFrozen(card)])
   if not isFrozen(card) and card.highlight == ActivatedColor:
      clear(card)


def doesNotUnfreeze(card, restr = None):
   """
   Card does not unfreeze (untap) normally.
   """
   mute()
   debug("doesNotUnfreeze({}, {})", card, restr)
   msg = "not unfreeze"
   when = ""
   if not hasMarker(card, "Cannot Unfreeze"):
      setMarker(card, "Cannot Unfreeze")
      if restr:  # Time restrictions
         when = "next "
   else:
      removeMarker(card, "Cannot Unfreeze")
      msg = "unfreeze as normal"
   notify("{0}'s {1} will {2} in {0}'s {3}Activate phase.", card.controller, card, msg, when)


def clear(card, x = 0, y = 0):
   card.target(False)
   card.highlight = None
   card.select(False)
   card.arrow(card, False)


def alignCardAction(card, x = 0, y = 0):
   if isCharacter(card):
      slotIdx = getSlotIdx(card)
      if slotIdx != -1:
         alignCard(card, slotIdx = slotIdx)
      else:
         backups = getGlobalVar("Backups")
         if backups.get(card._id):
            c = Card(backups[card._id])
            alignBackups(c, *c.position)


def askCardBackups(card, x = 0, y = 0):
   if not isCharacter(card):
      information("Only character cards can be backed-up.")
      return
   acceptedBackups = getAcceptedBackups(card)
   inRing = isCharInRing(card)
   avlCharsForBackup = []
   msg = "{} can be backed-up with the following character types:\n  - {}".format(card.Name, "\n  - ".join(filter(None, acceptedBackups)))
   # Check remaining backups
   avlBackups = list(acceptedBackups) # Copy array
   backups = getGlobalVar("Backups")
   for id in backups:
      # Remove the backups the card already has
      if backups[id] == card._id:
         avlBackups.remove(Card(id).Subtype)
   # Candidates to back-up from the hand
   for c in me.hand:
      if isCharacter(c):
         if c != card and c.Subtype in avlBackups:
            avlCharsForBackup.append(c)
   # Backup char if it is in the ring
   if inRing:
      if len(avlBackups) > 0:
         msg += "\n\nRemaining backups: {}/{} ({}).".format(len(avlBackups), len(acceptedBackups), ", ".join(avlBackups))
         if len(avlCharsForBackup) > 0:
            if not canBackup(card):
               return
            targets = showCardDlg(avlCharsForBackup, "Select a character card from your hand to back-up {}".format(card.Name))
            if targets:
               if backup(targets[0], target = card):
                  return
         else:
            msg = "You don't have compatible character cards in your hand to back-up {}.".format(card.Name) + "\n\n" + msg
            whisper(msg)
            information(msg)
            return
      else:
         warning("{} cannot be backed-up, maximum number of back-ups ({}) reached for this character.".format(card.Name, len(acceptedBackups)))
         return
   # Asked for back-up info
   if len(avlBackups) > 0 and len(avlCharsForBackup) > 0:
      msg += "\n\nCompatible cards in your hand: {}.".format(cardsAsNamesListStr(avlCharsForBackup))
   whisper(msg)
   if not inRing or len(avlCharsForBackup) == 0:
      information(msg)


def transformCards(cards, x = 0, y = 0):
   """
   Transform a card into another card.
   """
   cardModel = None
   targets = getAllTargetedCards()
   if len(targets) > 0:
      cardModel = targets[0].model
   else:
      cardtype = cards[0].Type
      card, quantity = askCard({"Type": cardtype}, "and", "Target character will be transformed into chosen card.")
      if quantity > 0:
         cardModel = card
   if cardModel:
      for card in cards:
         transformCard(card, cardModel)
      for target in targets:
         target.target(False)


def toggleAbility(card, x = 0, y = 0, remove = False):
   """
   Removes or restores the ability of a character.
   """
   if not isCharacter(card) or (card.alternate == "" and card.Rules == ""):
      return
   # Restores ability
   if card.alternate == "noability" and not remove:
      card.alternate = ""  # Revert to default form
      # Removes card from parsed list to parse it again with the new abilities
      for p in players:
         funcCall(p, deleteGameCard, [card])
      funcCall(card.controller, createGameCard, [card, None, True, False, True])
      if card.Rules != "":
         notify("{} restores {}'s abilities.", me, card)
      else:
         notify("{} tried to restore {}'s abilities, but it doesn't have any original ability.", me, card)
   # Removes ability
   else:
      dispatchEvent(GameEvents.Powerless, card._id)
      for p in players:
         funcCall(p, deleteGameCard, [card])
       # Remove the ability from the dict that holds the state of the modified abilities
      CharsAbilities = getGlobalVar("CharsAbilities")
      if card._id in CharsAbilities:
         del CharsAbilities[card._id]
      setGlobalVar("CharsAbilities", CharsAbilities)
      if "Model" in card.properties:
         card.properties["Model"] = None
      # Ability was already removed
      if "noability" in card.alternates:
         card.alternate = "noability"
      else:
         # Updates proxy image for all players
         for p in players:
            funcCall(p, addAlternateRules, [card, "", "", "noability"])
      notify("{} removes {}'s abilities", me, card)


def copyAbility(card, x = 0, y = 0, target = None):
   """
   Copies an ability from one target card to another card.
   """
   debug(">>> copyAbility({}, {})", card, target)
   if not isCharacter(card):
      warning("Abilities can only be copied to character cards.")
      return
   if target == None:
      targets = getAllTargetedCards()
      if len(targets) > 0 and isCharacter(targets[0]) and targets[0] != card:
         target = targets[0]
      else:
         choice = askChoice("From where do you want to copy an ability?", ["Arena", "Hand", "My Discard pile"])
         if choice == 0:
            return
         if choice == 1:
            pile = getRing()
         elif choice == 2:
            pile = me.hand
         else:
            pile = me.piles["Discard pile"]
         cards = [c for c in pile
                  if c.Rules != ""
                  and isCharacter(c)
                  and c != card]
         choosenCards = showCardDlg(cards, "Choose a character with an ability to copy")
         if choosenCards:
            target = choosenCards[0]
         else:
            return
   if target:
      # Copy the card in case its abilities changes
      target_copy = copyCard(target)
      result = copyAlternateRules(card, target)
      if result:
         CharsAbilities = getGlobalVar("CharsAbilities")
         model = target.model
         # target can be a Struct
         if isinstance(target, Card):
            if target._id in CharsAbilities:
               model = CharsAbilities[target._id]
         # Updates the dict that holds the state of the modified abilities
         CharsAbilities[card._id] = model
         setGlobalVar("CharsAbilities", CharsAbilities)
         dispatchEvent(GameEvents.Powerless, card._id)
         # Updates proxy image for the other players
         if len(players) > 1:
            for p in players:
               if p != me:
                  remoteCall(p, "copyAlternateRules", [card, target_copy])
         update()
         for p in players:
            funcCall(p, deleteGameCard, [card])
         funcCall(card.controller, createGameCard, [card, model, True, False, True])
         if target.Ability.split(" ")[0] != InstantAbility:
            if card.highlight == ActivatedColor:
               card.highlight = None
         notify("{} copies ability {} to {}.", me, target.Ability, card)
         return target
      else:
         warning("Target card doesn't have an ability to copy.")
   else:
      warning("Please select a valid character card.")
   debug("<<< copyAbility()")


def swapAbilities(card, x = 0, y = 0, target = None):
   """
   Swap the abilities between two characters.
   """
   debug(">>> swapAbilities({}, {})", card, target)
   if not isCharacter(card) or not isCharInRing(card, card.controller) or not card.Rules:
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
   card_copy = copyCard(card)  # Shallow copy of the card
   copyAbility(card,   target = target)
   copyAbility(target, target = card_copy)
   target.target(False)
   notify("{} has swapped abilities between {} and {}", me, card, target)
      
      
def stealAbility(card, x = 0, y = 0, target = None):
   """
   Copies the ability from one card to another and removes the ability of the first.
   """
   target = copyAbility(card, target = target)
   if target:
      ability = getGameCard(target).ability.name
      toggleAbility(target, remove = True)
      notify("{} steals ability {} from {} and gives it to {}.", me, ability, target, card)


def flip(card, x = 0, y = 0):
   """
   Flips a card so it is face down or face up.
   """
   mute()
   faceUp = card.isFaceUp
   card.isFaceUp = True
   notify("{} flips {} face {}.".format(me, card, ("up", "down")[faceUp]))
   card.isFaceUp = not faceUp


#---------------------------------------------------------------------------
# Card movement actions
#---------------------------------------------------------------------------

def destroy(card, controller = me):
   """
   Puts a card in the discards pile.
   """
   mute()
   # Do not delete UI elements (they are cards after all)
   if isUI(card) and not debugging:
      return
   fromText = fromWhereStr(card.group)
   action = "discards"
   card.moveTo(me.piles["Discard pile"])
   if isCharacter(card):
      action = "KOs"
      playSnd("ko-1")
   else:
      playSnd("ko-2")
   # Restore rotation or it will go to the pile rotated
   if card.orientation != Rot0:
      card.orientation = Rot0
   notify("{} {} {} {}.", controller, action, card, fromText)


def batchDestroy(cards, x = 0, y = 0):
   if len(cards) == 1:
      action = "KO" if isCharacter(cards[0]) and isCharInRing(cards[0]) else "discard"
      msg = "Do you want to {} {}?".format(action, cards[0].Name)
   else:
      msg = "Do you want to discard these {} cards?".format(len(cards))
   # Ask for confirmation if user uses a keyboard shortcut
   if not settings["WinForms"] or confirm(msg, "Destroy"):
      for card in cards:
         destroy(card)
      

def remove(card, x = 0, y = 0):
   mute()
   """
   Puts a card in the Removed pile.
   """
   fromText = fromWhereStr(card.group)
   card.moveTo(me.piles["Removed pile"])
   notify("{} removes {} {}.", me, card, fromText)


def toHand(card, x = 0, y = 0):
   mute()
   src = card.group
   fromText = fromWhereStr(card.group)
   cardname = revealCard(card)
   card.moveTo(me.hand)
   if src == table:
      notify("{} returns {} to its Hand {}.", me, cardname, fromText)
   else:
      notify("{} puts {} in its Hand {}.", me, cardname, fromText)


def toDeckTop(card, x = 0, y = 0):
   mute()
   fromText = fromWhereStr(card.group)
   cardname = revealCard(card)
   card.isFaceUp = False
   card.moveTo(me.Deck)
   notify("{} puts {} {} on the top of its Deck.", me, cardname, fromText)


def toDeckBottom(card, x = 0, y = 0):
   mute()
   fromText = fromWhereStr(card.group)
   card.moveToBottom(me.Deck)
   notify("{} puts {} {} on the bottom of its Deck.", me, card, fromText)


def toHandAll(group, x = 0, y = 0):
   mute()
   for card in group:
      card.moveTo(me.hand)
   if len(players) > 1:
      waitForAnimation()
   notify(MSG_ACTION_MOVE_ALL_CARDS, me, group.name, "its Hand")


def toDeckTopAll(group, x = 0, y = 0):
   mute()
   Deck = me.Deck
   for card in group:
      card.moveTo(Deck)
   if len(players) > 1:
      waitForAnimation()
   notify(MSG_ACTION_MOVE_ALL_CARDS, me, group.name, "the top of its Deck")


def toDeckBottomAll(group, x = 0, y = 0):
   mute()
   Deck = me.Deck
   for card in group:
      card.moveToBottom(Deck)
   if len(players) > 1:
      waitForAnimation()
   notify(MSG_ACTION_MOVE_ALL_CARDS, me, group.name, "the bottom of its Deck")


def toOwnerDeck(cards):
   for card in cards:
      card.moveTo(card.owner.Deck)


def shuffleIntoDeck(group, x = 0, y = 0):
   mute()
   for card in group:
      toDeckTop(card)
   waitForAnimation()
   shuffle(me.Deck)


def discardAll(group, x = 0, y = 0):
   mute()
   discards = me.piles["Discard pile"]
   for card in group:
      card.moveTo(discards)
   if len(players) > 1:
      waitForAnimation()
   notify(MSG_ACTION_MOVE_ALL_CARDS, me, group.name, "the bottom of its Discard pile")


def removeAll(group, x = 0, y = 0):
   """
   Puts the cards in the group into the Removed pile
   """
   mute()
   pile = me.piles["Removed pile"]
   for card in group:
      card.moveTo(pile)
   if len(players) > 1:
      waitForAnimation()
   notify(MSG_ACTION_MOVE_ALL_CARDS, me, group.name, "the bottom of its Removed pile")


def toTableFaceDown(card, x = 0, y = 0):
   debug(">>> toTableFaceDown {}", card)
   mute()
   fromText = fromWhereStr(card.group)
   placeCard(card, card.Type, faceDown = True)
   notify(MSG_ACTION_FACE_DOWN, me, fromText)


def changeSlot(card, x = 0, y = 0, targets = None):
   debug(">>> changeSlot {}", card)
   mute()
   cardSlot = getSlotIdx(card, card.controller)
   if cardSlot == -1:
      warning(MSG_SEL_CHAR_RING)
      return
   if not targets:
      targets = getTargetedCardsFrom(card, True, card.controller == me)
   # Swap the position of two characters
   if len(targets) > 0:
      target = targets[0]
      targetSlot = getSlotIdx(target, target.controller)
      if targetSlot == -1:
         warning(MSG_SEL_CHAR_RING)
         return
      if target.controller != target.controller:
         whisper("You can only swap two characters in the same ring.")
         return
      putAtSlot(card, targetSlot, card.controller)
      putAtSlot(target, cardSlot, target.controller)
      alignCard(card)
      alignCard(target)
      target.target(False)
      notify("{} swapped positions of {} and {}.", me, card, target)
   # Move a character to another slot
   else:
      slotIdx = askForEmptySlot(card.controller)
      if slotIdx > -1:
         putAtSlot(card, slotIdx, card.controller, True)
         alignCard(card)
         notify("{} moved {} to slot {}.", me, card, slotIdx+1)


#---------------------------------------------------------------------------
# Marker actions
#---------------------------------------------------------------------------

def addMarkerAction(cards, x = 0, y = 0):
   """
   Manually adds any of the available markers.
   """
   mute()
   # Ask the player how many of the same type they want.
   marker, quantity = askMarker()
   if quantity == 0:
      return
   # Then go through their cards and add those markers to each.
   for card in cards:
      card.markers[marker] += quantity
      notify("{} adds {} {} counter to {}.", me, quantity, marker[0], card)

# --------------
# Character BP
# --------------

def plusBP(cards, x = 0, y = 0, silent = False, amount = 100):
   mute()
   for card in cards:
      addMarker(card, "BP", amount)
      if not silent:
         notify("{} raises {}'s BP by {} (new BP is {})", me, card, amount, getMarker(card, "BP"))
         playSnd("power-up")

def minusBP(cards, x = 0, y = 0, silent = False, amount = 100):
   mute()
   for card in cards:
      c = amount
      bp = getMarker(card, "BP")
      if c > bp:
         c = bp
      addMarker(card, "BP", -c)
      if not silent:
         notify("{} lowers {}'s BP by {} (new BP is {}).", me, card, amount, getMarker(card, "BP"))
         playSnd("power-down")

def plusBP2(cards, x = 0, y = 0): plusBP(cards, amount = 200)
def plusBP3(cards, x = 0, y = 0): plusBP(cards, amount = 300)
def plusBP4(cards, x = 0, y = 0): plusBP(cards, amount = 400)
def plusBP5(cards, x = 0, y = 0): plusBP(cards, amount = 500)
def plusBP6(cards, x = 0, y = 0): plusBP(cards, amount = 600)
def plusBP7(cards, x = 0, y = 0): plusBP(cards, amount = 700)
def plusBP8(cards, x = 0, y = 0): plusBP(cards, amount = 800)
def plusBP9(cards, x = 0, y = 0): plusBP(cards, amount = 900)

def plusBPX(cards, x = 0, y = 0):
   n = askInteger("Raise BP by...", 100)
   if n == None:
      return
   plusBP(cards, amount = roundBP(n))

def minusBP2(cards, x = 0, y = 0): minusBP(cards, amount = 200)
def minusBP3(cards, x = 0, y = 0): minusBP(cards, amount = 300)
def minusBP4(cards, x = 0, y = 0): minusBP(cards, amount = 400)
def minusBP5(cards, x = 0, y = 0): minusBP(cards, amount = 500)
def minusBP6(cards, x = 0, y = 0): minusBP(cards, amount = 600)
def minusBP7(cards, x = 0, y = 0): minusBP(cards, amount = 700)
def minusBP8(cards, x = 0, y = 0): minusBP(cards, amount = 800)
def minusBP9(cards, x = 0, y = 0): minusBP(cards, amount = 900)

def minusBPX(cards, x = 0, y = 0):
   n = askInteger("Lower BP by...", 100)
   if n == None:
      return
   minusBP(cards, amount = roundBP(n))

def changeBP(cards, x = 0, y = 0):
   mute()
   changeMarker(cards, MarkersDict["BP"], "Set character BP to:\n(a value of 0 will KO the character)")

# -----------
# Player SP
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
   if n == None:
      return
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
   if n == None:
      return
   modSP(-n)


#---------------------------------------------------------------------------
# Hand actions
#---------------------------------------------------------------------------

def play(card, x = 0, y = 0, slotIdx = None):
   """
   Play cards from (usually) the player's hand.
   """
   debug(">>> playing card {} at slot {}", card, slotIdx)

   mute()
   slot = ""
   group = card.group
   if settings["PlayAuto"]:
      if not playAuto(card, slotIdx):
         # Something happened and couldn't play the card
         return False
      slot = " in slot {}".format(getSlotIdx(card) + 1)
   else:
      placeCard(card, card.Type)
   isChar = isCharacter(card)
   if isChar:
      notify("{} plays {} from their {}{}.", me, card, group.name, slot)
      charsPlayed = getState(me, "charsPlayed")
      playSnd("card-play-1")
      notify("({} has played {} character{} this turn.)", me, charsPlayed, pluralize(charsPlayed))
   else:
      playSnd("card-play-2")
      notify("{} plays {} from their {}.", me, card, group.name)
      
   if settings["PlayAuto"]:
      pcard = getGameCard(card)
      if not isChar or pcard.hasEffect() and pcard.ability.type == InstantAbility:
         if settings["Activate"]:
            # Trying to delay activation {
            waitForAnimation()
            update()
            waitForAnimation()
            update()
            # }
            activate(card)
         else:
            whisper(MSG_HINT_ACTIVATE)

   debug("<<< playing card end")


def backup(card, x = 0, y = 0, target = None):
   """
   Play a card as backup attached to a character in the player's ring.
   """
   debug(">>> back-up with card {}", card)
   mute()
   group = card.group
   if settings["PlayAuto"]:
      target = backupAuto(card, target)
      if target:
         lastBP = getGameCard(target).getState("lastBP")
         newBP = getMarker(target, "BP")
         notify("{0} back-ups {1} with {2} from their {3}. New BP of {1} is {4} (before was {5}).", me, target, card, group.name, newBP, lastBP)
         playSnd("backup")
         return True
   else:
      placeCard(card, card.Type)
      notify("{} back-ups with {} from their {}.", me, card, group.name)
      playSnd("backup")
   debug("<<< back-up end")


def discard(card, x = 0, y = 0, isRandom = False):
   mute()
   group = card.group
   card.moveTo(me.piles["Discard pile"])
   msg = "{} has discarded {} from their {}."
   if group != me.hand:
      msg = "{} puts {} into his Discard pile."
   if isRandom:
      msg = MSG_DISCARD_RANDOM
   playSnd("discard")
   notify(msg, me, card, group.name)


def randomDiscard(group = me.hand, x = 0, y = 0):
    mute()
    card = group.random()
    if card == None:
        return
    card.moveTo(me.piles["Discard pile"])
    notify(MSG_DISCARD_RANDOM, me, card, group.name)


def refillHand(group = me.hand):
   """
   Refill the player's hand to its hand size.
   """
   playHand = len(me.hand)
   # If there's less cards than the handSize, draw from the deck until it's full
   if playHand < me.handSize:
      drawMany(me.Deck, me.handSize - playHand)


#---------------------------------------------------------------------------
# Piles actions
#---------------------------------------------------------------------------

def draw(group = me.Deck):
   """
   Draws one card from the deck into the player's hand.
   """
   mute()
   if len(group) == 0:
      whisper(MSG_ERR_DRAW_EMPTY_PILE.format(group.name))
      return
   group.top().moveTo(me.hand)
   playSnd("draw")
   notify("{} draws a card.", me)


def drawMany(group, count = None):
   """
   Draws a variable number cards into the player's hand.
   """
   mute()
   if len(group) == 0:
      whisper(MSG_ERR_DRAW_EMPTY_PILE.format(group.name))
      return
   if count == None:
      count = askInteger("How many cards do you want to draw?", me.dialogDrawCount) # Ask the player how many cards they want.
   if count == None:
      return
   # Remember amount for next time dialog is opened
   me.dialogDrawCount = count
   drawn = 0
   for i in range(0, count):
      # If the deck is not empty...
      if len(group) > 0:
         # ...then move them one by one into their play hand.
         group.top().moveTo(me.hand)
         drawn += 1
   notify("{} draws {} card{}.", me, drawn, pluralize(drawn))
   playSnd("draw")


def randomDraw(group = me.Deck, type = None):
   mute()
   if len(group) == 0:
      whisper(MSG_ERR_DRAW_EMPTY_PILE.format(group.name))
      return
   if type == None:
      card = group.random()
   else:
      cards = [card for card in group
         if card.Type == type]
      if len(cards) == 0:
         whisper("There is no cards of the type {} in the {}.".format(type, group.name))
         return
      card = cards[rnd(0, len(cards)-1)]
   cardname = revealCard(card, type)
   card.moveTo(me.hand)
   notify("{} draws {} at random {}.", me, cardname, fromWhereStr(group))


def randomDrawCHA(group = me.Deck):
   randomDraw(group, CharType)


def randomDrawAC(group = me.Deck):
   randomDraw(group, ActionType)


def randomDrawRE(group = me.Deck):
   randomDraw(group, ReactionType)


def trash(group, x = 0, y = 0, count = None):
   """
   Puts one or more cards from the given pile into the Discard pile.
   """
   mute()
   if group is None:
      group = me.Deck
   # Last input by the user
   if count == None:
      count = askInteger("How many cards do you want to trash?", me.dialogTrashCount)
   if count == None:
      return
   # Remember amount for next time dialog is opened
   me.dialogTrashCount = count
   discards = me.piles["Discard pile"]
   cards = []
   for card in group.top(count):
      card.moveTo(discards)
      cards.append(card)
   # Add trashed card to action local variables
   addTempVar("trashed", cards)
   if len(players) > 1:
      waitForAnimation()
   notify("{} trashes top {} cards {}.", me, count, fromWhereStr(group))


def prophecy(group = me.Deck, x = 0, y = 0, count = None, deckPos = False):
   """
   Rearranges the top cards of the deck according to the given argument.
   """
   mute()
   if len(group) == 0:
      return
   # Last input by the user
   if not count:
      count = askInteger("How many cards do you want to see?", me.dialogProphecyCount)
      if count == None:
         return
   # Remember amount for next time dialog is opened
   me.dialogProphecyCount = count
   # Convert generator object to list
   cards = list(group[:count])
   cardsPos = []
   owner = "his" if group.controller == me else "{}'s".format(group.controller)
   notify(MSG_PLAYER_LOOKS, me, owner, group.name)
   where = "top or bottom"
   if deckPos is not False:
      where = "top" if deckPos >= 0 else "bottom"
   question = "Select a card to put on {} of the deck".format(where)
   while len(cards) > 0:
      # Allow the player to first see the cards...
      card = showCardDlg(cards, question)
      if card == None:
         return
      card = card[0]
      # ... and then choose where to put them (once)
      if deckPos is False:
         deckPos = askChoice("Where to put the card?", ["Top of the deck", "Bottom of the deck"])
         if deckPos == 0:
            return
         # Reverse the choice  1,2 => 0,-1
         deckPos = (deckPos - 1) * -1
      cards.remove(card)
      cardsPos.append((card, deckPos))
   for item in cardsPos:
      card, pos = item
      if group.controller == me:
         moveToGroup(group, card, pos = pos, reveal = False)
      else:
         remoteCall(group.controller, "moveToGroup", [group, card, group, pos, False, me])
   waitForAnimation()


def shuffle(group):
   """
   A simple function to shuffle piles.
   """
   mute()
   group.shuffle()
   playSnd("shuffle")
   notify("{} shuffled its {}", me, group.name)


def reshuffle(group = me.piles["Discard pile"]):
   """
   This function reshuffles a pile into player's deck.
   """
   mute()
   Deck = me.Deck
   for card in group:
      # Move the player's cards from the group to its deck one-by-one.
      card.moveTo(Deck)
   waitForAnimation()
   Deck.shuffle()
   playSnd("shuffle")
   notify("{} reshuffled its {} into its Deck.", me, group.name)


def reshuffleCardsOfType(group, cardType):
   """
   Reshuffles all the cards of the given type into the player's deck.
   """
   Deck = me.Deck
   for card in group:
      if card.Type == cardType:
         # Move the player's cards from the group to its deck one-by-one.
         card.moveTo(Deck)
   update()  # Trying this method to delay next actions until networked tasks are complete
   Deck.shuffle()
   playSnd("shuffle")
   notify("{} shuffles all {} cards from his {} into its Deck.", me, cardType, group.name)


def reshuffleCHA(group = me.piles["Discard pile"]):
   mute()
   reshuffleCardsOfType(group, CharType)


def reshuffleAC(group = me.piles["Discard pile"]):
   mute()
   reshuffleCardsOfType(group, ActionType)


def reshuffleRE(group = me.piles["Discard pile"]):
   mute()
   reshuffleCardsOfType(group, ReactionType)


def revealTopDeck(group, x = 0, y = 0):
   mute()
   if len(group) == 0:
      return
   card = group[0]
   if card.isFaceUp:
      notify("{} hides {} from the top of their {}.", me, card, group.name)
      card.isFaceUp = False
   else:
      card.isFaceUp = True
      notify("{} reveals {} from the top of their {}.", me, card, group.name)


def swapWithDeck(group = me.piles["Discard pile"]):
   swapPiles(me.Deck, group)


def removedDefaultAction(card, x = 0, y = 0):
   if me.isActive and getCurrentPhase() == MainPhase and getRule("play_removed"):
      play(card)
   else:
      toHand(card)
      

#---------------------------------------------------------------------------
# Debug actions
#---------------------------------------------------------------------------

def startDebug(group, x = 0, y = 0):
   mute()
   global debugging
   debugging = True
   resetGame()
   

def stopDebug(group, x = 0, y = 0):
   mute()
   global debugging
   debugging = False
   global debugVerbosity
   debugVerbosity = DebugLevel["Off"]
   resetGame()


def setDebugVerbosity(group = None, x = 0, y = 0):
   global debugVerbosity
   mute()
   levels = DebugLevel.keys()
   choice = askChoice("Set debug verbosity to:\n(currently is \"{}\")".format(levels[debugVerbosity]), levels)
   if choice == 0:
      return
   debugVerbosity = choice - 1
   whisper("Debug verbosity is now \"{}\" ({})".format(levels[debugVerbosity], debugVerbosity))


def createCard(group, x = 0, y = 0):
   id, quantity = askCard(title = "Choose a card to add to the game")
   if quantity > 0:
      card = table.create(id, 0, 0, quantity = quantity, persist = True)
      notify("{} has created the card {}", me, card)
      
      
def createRandomDeck(group = table, x = 0, y = 0):
   mute()
   nonCharQty = random.randInt(17, 21)
   nonChar = random.sample(queryCard({"Type": ["Action", "Reaction"]}), nonCharQty)
   whisper("Deck contains {} non-char cards".format(len(nonChar)))
   allChar = queryCard({"Type": "Character"})
   charNoRules = queryCard({"Type": "Character", "Rules": ""}, True)
   charsRules = [c for c in allChar if c not in charNoRules]
   chars = random.sample(charsRules, DeckSize - nonCharQty)
   whisper("Deck contains {} char cards with rules".format(len(chars)))
   deck = nonChar + chars
   for id in deck:
      me.deck.create(id, 1)
   playSnd("load-deck")
   waitForAnimation()
   shuffle(me.Deck)
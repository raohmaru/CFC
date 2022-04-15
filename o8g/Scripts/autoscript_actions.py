# Python Scripts for the Card Fighters" Clash definition for OCTGN
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

#------------------------------------------------------------------------------
# Automated actions
#------------------------------------------------------------------------------

def playAuto(card, slotIdx = None, force = False):
   debug(">>> playAuto({}, {}, {})", card, slotIdx, force)
   syncGlobalVars()
   phaseIdx = getCurrentPhase()

   # Player plays a Character card
   if isCharacter(card):
      # Check if the card can be legally played
      if (not me.isActive or phaseIdx != MainPhase) and not force:
         information("Character cards can only be played in your Main Phase.")
         return
      # Limit of chars that can be played per turn
      charsPlayed = getState(me, "charsPlayed")
      charsPerTurn = getState(me, "charsPerTurn")
      if charsPlayed >= charsPerTurn:
         warning("Only {} character card{} per turn can be played.\n(You have played {} character{} this turn.)".format(charsPerTurn, pluralize(charsPerTurn), charsPlayed, pluralize(charsPlayed)))
         return
      # BP limit?
      bplimit = getRule("play_char_bp_limit")
      if bplimit:
         # Get the max value allowed
         bplimit = reduce(lambda a, b: min(a, b), bplimit)
         if card.BP >= bplimit:
            warning(MSG_RULES["play_char_bp_limit"][True].format(bplimit))
            return
      # Player has any empty slot in his ring?
      myRing = getGlobalVar("Ring", me)
      if myRing.count(None) == 0:
         warning(MSG_ERR_NO_EMPTY_SLOTS)
         return
      # Prompt the player to select an empty slot
      if slotIdx == None:
         slotIdx = askForEmptySlot()
         if slotIdx == -1:
            return
         debug("Selected slot: {} ({})", slotIdx, myRing[slotIdx])
      # Sanity check: Is it really empty that slot?
      # (It's also really needed this check?)
      if myRing[slotIdx] != None:
         warning("Character card can't be played, slot {} is not empty (it's taken up by {}).\nIf you want to do a backup, please first target a character in your ring.".format(slotIdx, Card(myRing[slotIdx]).Name))
         return
      # Pay SP cost
      if not payCostSP(card.SP, card, type = CharType):
         return
      # Finally, the card is played
      placeCard(card, card.Type, "play", slotIdx)
      # Parse the card to enable the card autoscript
      deleteGameCard(card)
      pcard = createGameCard(card)
      setMarker(card, "BP", card.BP)
      # Triggers a hook whether the character can have the "just entered" marker
      if triggerHook(Hooks.PlayAsFresh, args = [card._id]) != False:
         setMarker(card, "Just Entered")
      putAtSlot(card, slotIdx)
      setState(me, "charsPlayed", charsPlayed + 1)

   # Player plays an Action card
   elif isAction(card):
      # Triggers a hook to check if the player can play action cards
      if triggerHook(Hooks.BeforePlayAC, args = [me._id]) == False:
         return
      # Check if the card can be legally played
      if not me.isActive or phaseIdx != MainPhase:
         information("Action cards can only be played in your Main Phase.")
         return
      # Pay SP cost
      if not payCostSP(card.SP, card, type = ActionType):
         return
      placeCard(card, card.Type, "play")
      # Parse the card to enable card autoscript
      deleteGameCard(card)
      createGameCard(card)
      # Remove "until next action card" events
      cleanupGameEvents(RS_KW_RESTR_UNAC)

   # Player plays a Reaction card
   elif isReaction(card):
      # Check if the card can be legally played
      if (me.isActive or phaseIdx != BlockPhase) and not debugging and not tutorial:
         information("Reaction cards can only be played in enemy's Counter-attack Phase.")
         return
      # Triggers a hook to check if the player can play reaction cards
      if triggerHook(Hooks.BeforePlayRE, args = [me._id]) == False:
         return
      # Pay SP cost
      if not payCostSP(card.SP, card, type = ReactionType):
         return
      placeCard(card, card.Type, "play")
      # Parse the card to enable card autoscript
      deleteGameCard(card)
      createGameCard(card)

   return True


def backupAuto(card, target = None):
   debug(">>> backupAuto({}, {})", card, target)

   # Check if the card can be legally played
   if not me.isActive or getCurrentPhase() != MainPhase:
      information("Characters can only be backed-up in your Main Phase.")
      return
   # Only for character cards
   if not isCharacter(card):
      warning("You can only back-up with Character cards.")
      return
   # Check if a valid char has been targeted
   if not target:
      myRing = getGlobalVar("Ring", me)
      targets = getTargetedCards(card)
      if len(targets) == 0 or not targets[0]._id in myRing:
         targets = []
         # Get a compatible character in the ring
         for c in getRing(me):
            acceptedBackups = getAcceptedBackups(c)
            if card.Subtype in acceptedBackups:
               targets.append(c)
         if targets:
            targets = showCardDlg(targets, "Select a character in your ring to back-up")
            if targets == None:
               return
         else:
            warning("There are no compatible characters to back-up in your ring with {} (subtype is \"{}\").".format(card, card.Subtype))
            return
      target = targets[0]
   # Target is frozen?
   if isFrozen(target):
      warning("Frozen characters can't be backed-up.")
      return
   # Check some constrains
   if not canBackup(target):
      return
   # Check compatible backups
   acceptedBackups = getAcceptedBackups(target)
   if not card.Subtype in acceptedBackups:
      warning("Incompatible back-up type.\n{} accepts these character subtypes: {}.".format(target.Name, cardsAsNamesListStr(acceptedBackups)))
      return
   # Check remaining backups
   avlbckps = acceptedBackups.count(card.Subtype)
   backups = getGlobalVar("Backups")
   for id in backups:
      # id is the card attached to backups[id]
      if backups[id] == target._id:
         if Card(id).Subtype == card.Subtype:
            avlbckps -= 1
   if avlbckps <= 0:
      qty = acceptedBackups.count(card.Subtype)
      warning("{} can't be backed-up with more than {} {} card{}.".format(target.Name, qty, card.Subtype, pluralize(qty)))
      return
   # It's a legal backup
   attach(card, target)
   placeCard(card, card.Type, "backup", target)
   card.sendToBack()
   setMarker(card, "Backup")
   pcard = getGameCard(target)
   # Backed-up character's BP is raised
   addMarker(target, "BP", BackupRaiseBP)
   setState(me, "backupsPlayed", getState(me, "backupsPlayed") + 1)
   dispatchEvent(GameEvents.BackedUp, args = [target._id])
   return target


def attackAuto(card, force = False):
   debug(">>> attackAuto({}, {})", card, force)

   # Check if player can attack
   if not force and (not me.isActive or getCurrentPhase() != AttackPhase):
      information("You can only attack in your Attack Phase.")
      return
   # Only for character cards...
   if not isCharacter(card):
      information("You can only attack with Character cards.")
      return
   # ... in player's ring
   slotIdx = getSlotIdx(card)
   if slotIdx == -1:
      warning(MSG_ERR_ATTACK_CHAR_RING)
      return
   # Check if attack is allowed
   if not getRule("attack"):
      warning(MSG_ERR_CANNOT_ATTACK.format(card.Name))
      return
   # Triggers a hook to check if the character can attack
   if triggerHook(Hooks.BeforeAttack, card._id, [card._id]) == False:
      return
   # Cancels the character's attack if it's already attacking
   if isAttacking(card):
      cancelAttack(card)
      return
   # Char just entered the ring?
   if hasMarker(card, "Just Entered"):
      warning(MSG_ERR_ATTACK_FRESH)
      return
   # Frozen char?
   if isFrozen(card):
      warning("Frozen characters cannot attack the turn they enter the ring.")
      return
   # Wants to join a United attack?
   targets = getTargetedCards(card)
   if len(targets) > 0:
      unitedAttack(card)
      return

   # Perform the attack
   setMarker(card, "Attack")
   alignCard(card, slotIdx)

   return True


def unitedAttackAuto(card, targets = None, force = False):
   debug(">>> attackAuto({}, {}, {})", card, targets, force)

   # Is char in player's ring?
   if not charIsInRing(card):
      warning(MSG_ERR_ATTACK_CHAR_RING)
      return 
   # If is the only attacker, do a regular attack
   if len(getAttackingCards()) == 0:
      attack(card)
      return
   # Check if attack is allowed
   if not getRule("attack"):
      warning(MSG_ERR_CANNOT_ATTACK.format(card.Name))
      return
   # Char just entered the ring?
   if hasMarker(card, "Just Entered"):
      warning(MSG_ERR_ATTACK_FRESH)
      return
   # Triggers a hook to check if the character can attack
   if triggerHook(Hooks.BeforeAttack, card._id, [card._id]) == False:
      return
   # Cancels the character's attack if it's already attacking
   if not force and isAttacking(card):
      cancelAttack(card)
      return
   # Check if an attacking char has been selected
   myRing = getGlobalVar("Ring", me)
   if not targets:
      targets = getTargetedCards(card)
   if len(targets) == 0 or not targets[0]._id in myRing or not isAttacking(targets[0]):
      if not force:
         targets = getAttackingCards()
         if len(targets) > 1:
            targets = showCardDlg(targets, "Select an attacking character to join an United Attack.")
         if not targets:
            warning("Please select an attacking character in your ring.\n({}).".format(MSG_SEL_HOW_TO))
            return
   target = targets[0]
   # Allowed united attacks
   uattack = getGlobalVar("UnitedAttack")
   if len(uattack) > 0:
      if uattack[0] != target._id:
         # If targeting other char in the UA, change target to lead char
         if target._id in uattack:
            target.target(False)
            target = Card(uattack[0])
         else:
            warning("Only one United Attack is allowed.")
            return
   # Current chars in the United Attack
   united = [c for c in table
      if c.controller == me
      and hasMarker(c, "United Attack")]
   # Max chars per United Attack
   if len(united) >= MaxCharsUAttack:
      if not force:
         warning(MSG_UA_MAX.format(MaxCharsUAttack + 1))
      else:
         notify(MSG_UA_MAX.format(MaxCharsUAttack + 1))
      return
   totalUnited = len(united) + 1 # Current chars in UA + current char that will wants to join
   # Cost
   if not force:
      cost = totalUnited * UAttackCost
      cost = getCostMod(cost, "ua" + str(totalUnited + 1))
      if me.SP + cost < 0:
         type = ["", "Double", "Triple"][totalUnited]
         warning("You do not have enough SP to do a {} United Attack (it costs {} SP).".format(type, cost))
         return

   # Update UnitedAttack list
   if len(uattack) == 0:
      uattack.extend([target._id, card._id])
   else:
      uattack.append(card._id)
   setGlobalVar("UnitedAttack", uattack)
   debug("UnitedAttack: {}", uattack)

   setMarker(card, "United Attack")
   removeMarker(card, "Attack")
   target.target(False)
   alignCard(card)

   return target


def blockAuto(card, targets = None):
   debug(">>> blockAuto()")

   # Check if the card can legally block
   if (me.isActive or getCurrentPhase() != BlockPhase) and not tutorial:
      information("You can only counter-attack in enemy's Counter-attack Phase.")
      return
   # Only for character cards...
   if not isCharacter(card):
      information("You can only counter-attack with character cards.")
      return
   # ... in player's ring
   if not charIsInRing(card):
      warning("Please counter-attack with a character in your ring.")
      return
   # Frozen char?
   if isFrozen(card):
      warning("Frozen characters cannot counter-attack.")
      return
   # Triggers a hook to check if the character can counter-attack
   if triggerHook(Hooks.BeforeBlock, card._id, [card._id]) == False:
      return
   # Cancels the character's counter-attack if it's already blocking
   if hasMarker(card, "Counter-attack"):
      cancelBlock(card)
      return
   # Check if an attacking enemy char has been selected
   blockers = getGlobalVar("Blockers")
   enemyRing = getGlobalVar("Ring", players[1])
   targeted = False
   if not targets:
      targets = getTargetedCards(card, True, False)
      targeted = True
   if len(targets) > 0:
      if not targets[0]._id in enemyRing or not isAttacking(targets[0], False):
         if targeted:
            warning("Please select an attacking character ({}).\nIf blocking an United Attack, then select the leading character.".format(MSG_SEL_HOW_TO))
         return
   if len(targets) == 0:
      # Automatically select an attacking character if there is only one...
      atkCards = [c for c in getAttackingCards(getOpp())
         if c._id not in blockers]
      if len(atkCards) == 1:
         targets = atkCards
      elif len(atkCards) > 1:
         # ...or show card dialog to choose
         targets = showCardDlg(atkCards, "Select an attacking character to counter-attack with {}.".format(card.Name))
      else:
         whisper("There are not available attacking characters to block.")
         whisper("({})".format(MSG_ERR_BLOCK_ONE))
      if not targets:
         return
   target = targets[0]
   # An attacker can only be blocked by exactly 1 char
   if target._id in blockers:
      warning(MSG_ERR_BLOCK_ONE)
      return

   # Triggers a hook to check if block is possible
   addTempVar("attacker", [target])
   addTempVar("blocker", [card])
   if triggerHook(Hooks.CanBeBlocked, target._id, [target._id]) == False:
      return

   setMarker(card, "Counter-attack")
   # Save attacker => blocker
   blockers[target._id] = card._id
   setGlobalVar("Blockers", blockers)
   target.target(False)
   alignCard(card)

   return target


def activateAuto(card):
   debug(">>> activateAuto({})", card)
   
   syncGlobalVars()

   if card.highlight == ActivatedColor:
      kind = "ability" if isCharacter(card) else "effect"
      notify("{}'s {} has already been activated.".format(card, kind))
      return
   # Character ability
   if isCharacter(card):
      pcard = getGameCard(card)
      if not pcard.hasEffect():
         notify("{} has no ability to activate.".format(card))
         return
      debug("Trying to activate {}'s ability {} {}", card.Name, pcard.ability.type, pcard.ability.name)
      # Activate [] and /\ only in player's Main Phase
      if pcard.ability.type in [InstantAbility, TriggerAbility] and (not me.isActive or getCurrentPhase() != MainPhase):
         information("You can only activate {} or {} abilities in your Main Phase.".format(TriggerUniChar, InstantUniChar))
         return
      # /\ abilities
      if pcard.ability.type == InstantAbility:
         # Check if /\ abilities can be activated
         if not getRule("ab_instant_act"):
            if not settings["Activate"]:
               warning(MSG_RULES["ab_instant_act"][False])
            else:
               playSnd("cancel-2")
            notify(MSG_RULES["ab_instant_act"][False])
            return
         # Activate only once
         if not hasMarker(card, "Just Entered"):
            warning("{} abilities can only be activated once when the character just enters the ring.".format(InstantUniChar))
            return
      # [] abilities
      if pcard.ability.type == TriggerAbility:
         # Check if [] abilities can be activated
         if not getRule("ab_trigger_act"):
            warning(MSG_RULES["ab_trigger_act"][False])
            return
         # Just entered?
         if not getRule("ab_trigger_fresh") and hasMarker(card, "Just Entered"):
            warning("Can't activate {} abilities of characters that just entered the ring.".format(TriggerUniChar))
            return
         # Frozen or attacking?
         if isFrozen(card) or isAttacking(card):
            warning("Can't activate {} abilities of frozen or attacking characters.".format(TriggerUniChar))
            return
      # () abilities
      if pcard.ability.type == AutoAbility:
         whisper("{} abilities are activated automatically, you don't need to manually activate them.".format(AutoUniChar))
         return

      # Activate [] ability?
      if pcard.ability.type == TriggerAbility:
         if not confirm("Activate {}'s ability {} {}?\n\n\n{}".format(card.Name, pcard.ability.unicodeChar, pcard.ability.name, pcard.ability.rules)):
            return
      # Activate the ability
      return pcard.activateEffect()
   # Rest of cards
   else:
      pcard = getGameCard(card)
      return pcard.activateEffect()


#---------------------------------------------------------------------------
# Related functions
#---------------------------------------------------------------------------

def rearrangeUAttack(card):
   """
   Rearrange or cancels a UA if the card was part of it.
   """
   debug(">>> rearrangeUAttack({})", card)
   uattack = getGlobalVar("UnitedAttack")
   if card._id in uattack:
      notify("{} was part of an United Attack. Now it will be rearranged.".format(card))
      uatttackIdx = uattack.index(card._id)
      uattack.remove(card._id)
      uattack = filter(None, uattack)
      setGlobalVar("UnitedAttack", uattack)
      # If it was the lead card, or there is only 1 char left, cancel UA
      if uatttackIdx == 0 or len(uattack) == 1:
         notify("{} cancels the United Attack.".format(me))
         for cid in uattack:
            c = Card(cid)
            removeMarker(c, "United Attack")
            setMarker(c, "Attack")
            c.highlight = AttackColor
            alignCard(c)
         clearGlobalVar("UnitedAttack")
      # Reorder remaining chars in the UA
      else:
         for cid in uattack[1:]:
            alignCard(Card(cid))
      debug("UnitedAttack: {}", uattack)
      

def cancelAttack(card, silent = False):
   removeMarker(card, "Attack")
   removeMarker(card, "United Attack")
   removeMarker(card, "Unfreezable")
   clear(card)
   alignCard(card)
   rearrangeUAttack(card)
   if not silent:
      notify("{} cancels the attack with {}.".format(me, card))
      playSnd("cancel-1")
   

def cancelBlock(card, silent = False):
   removeMarker(card, "Counter-attack")
   clear(card)
   alignCard(card)
   blockers = getGlobalVar("Blockers")
   for i in blockers:
      if blockers[i] == card._id:
         del blockers[i]
         debug("Removed blocker {}", blockers)
         setGlobalVar("Blockers", blockers)
         break
   if not silent:
      notify("{} cancels the counter-attack with {}.".format(me, card))
      playSnd("cancel-1")

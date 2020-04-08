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

#------------------------------------------------------------------------------
# Start/End of Turn/Phase triggers
#------------------------------------------------------------------------------

def triggerPhaseEvent(phase):
   # Function which triggers effects at the start or end of the phase
   debug(">>> triggerPhaseEvent({})".format(phase)) #Debug
   mute()
   if not automations['Phase']: return
   
   skipPhases = getState(me, 'skip')
   if phase in skipPhases:
      notify("{} skips his {} phase due to an ability.".format(me, Phases[phase]))
      skipPhases.remove(phase)  # remove by value
      setState(me, 'skip', skipPhases)
      nextPhase()
      return

   if   phase == ActivatePhase: activatePhaseStart()
   elif phase == DrawPhase:     drawPhaseStart()
   elif phase == AttackPhase:   attackPhaseStart()
   elif phase == BlockPhase:    blockPhaseStart()
   elif phase == EndPhase:      endPhaseStart()
   elif phase == CleanupPhase:  cleanupPhaseStart()


def activatePhaseStart():
   # Unfreeze characters in the player's ring, clear colors and remove script markers
   myCards = (card for card in table
      if card.controller == me)
   frosted = []
   for card in myCards:
      if isCharacter(card):
         if not MarkersDict["Cannot Unfreeze"] in card.markers:
            freeze(card, unfreeze = True, silent = True)
         else:
            frosted.append(card)
         removeMarker(card, 'Just Entered')
         clear(card, silent = True)
      # Discard any Action or Reaction card left in the table (just in case player forgot to remove them)
      elif isAction(card) or isReaction(card):
         discard(card)
   frostedChars = ''
   if frosted:
      frostedChars = " but {}".format(' and '.join(["{}".format(c) for c in frosted]))
   notify("{} unfreezes all characters in their ring{}.".format(me, frostedChars))
   # Trigger event
   triggerGameEvent(GameEvents.ActivatePhase)
   cleanupGameEvents(RS_KW_RESTR_UYNT)


def drawPhaseStart():
   if automations['Play']:
      if len(me.Deck) == 0 and len(players) > 1:
         notify("{} has no cards in their deck and therefore can't draw.".format(me))
         _extapi.notify(MSG_HINT_WIN.format(players[1]), Colors.Black, True)
      else:
         draw()
   # Trigger event
   triggerGameEvent(GameEvents.DrawPhase)


def attackPhaseStart():
   clearKOedChars()
   clearGlobalVar('Stack')
   # Discard action cards I have played
   myActionCards = (card for card in table
      if card.controller == me
      and isAction(card))
   for card in myActionCards:
      discard(card)


def blockPhaseStart():
   if automations['Play']:
      uattack = getGlobalVar('UnitedAttack')
      if len(uattack) > 0:
         chars = len(uattack) - 1
         uatype = "Double" if chars == 1 else "Triple"
         payCostSP(-chars*UAttackCost, msg = "does a {} United Attack".format(uatype))
         notify("{} has paid the cost of the {} United Attack".format(me, uatype))
   # Trigger event
   triggerGameEvent(GameEvents.BlockPhase)
   # Attacking chars event not in UA
   atkCards = getAttackingCards()
   uattack = getGlobalVar('UnitedAttack')
   for card in atkCards:
      if len(uattack) == 0 or uattack[0] != card._id:
         triggerGameEvent([GameEvents.Attacks, card._id], card._id)


def endPhaseStart():
   clearKOedChars()
   clearGlobalVar('Stack')

   # Freeze attacking characters
   myCards = (card for card in table
      if card.controller == me)
   for card in myCards:
      if isCharacter(card):
         if (hasMarker(card, 'Attack') or hasMarker(card, 'United Attack')) and not hasMarker(card, 'Unfreezable'):
            freeze(card, unfreeze = False, silent = True)

   # Calculates and applies attack damage
   if automations['AttackDmg']:
      blockers = getGlobalVar('Blockers')
      uattack = getGlobalVar('UnitedAttack')
      atkCards = getAttackingCards()
      for card in atkCards:
         dmg = getMarker(card, 'BP')
         pdmg = 0  # Piercing damage
         isUA = len(uattack) > 0 and uattack[0] == card._id
         if isUA:
            for x in range(1, len(uattack)):
               pdmg += getMarker(Card(uattack[x]), 'BP')
         # Attacker is blocked
         if card._id in blockers:
            blocker = Card(blockers[card._id])
            # Add discarded cards to action local variables & trigger game event
            addActionTempVars('attacker', [card])
            triggerGameEvent([GameEvents.Blocks, blocker._id], blocker._id)
            # Trigger blocked event if not in UA
            if pdmg == 0:
               triggerGameEvent([GameEvents.Blocked, card._id], card._id)
            blocker_bp = getMarker(blocker, 'BP')
            dealDamage(dmg + pdmg, blocker, card)
            dealDamage(blocker_bp, card, blocker)
            # Blocker damages to chars in an United Attack
            if isUA and blocker_bp > dmg:
               new_bp = blocker_bp - dmg
               for x in range(1, len(uattack)):
                  uacard = Card(uattack[x])
                  rest_bp = getMarker(uacard, 'BP') - new_bp
                  dealDamage(new_bp, uacard, blocker)
                  if rest_bp < 0:
                     new_bp = abs(rest_bp)
                  else:
                     break
            # Piercing damage of an United Attack
            if (
                  len(players) > 1 and
                  getRule('piercing') and
                  (pdmg > 0 or hasMarker(card, 'Pierce')) and
                  dmg + pdmg > blocker_bp and
                  triggerGameEvent(Hooks.PreventPierce, blocker._id)
               ):
               dmg = dmg + pdmg - blocker_bp
               dealDamage(dmg, players[1], card, isPiercing = True)
         # Unblocked attacker
         elif len(players) > 1:
            dealDamage(dmg + pdmg, players[1], card)
            triggerGameEvent([GameEvents.PlayerCombatDamaged, card._id], card._id)
   
   # Trigger event
   triggerGameEvent(GameEvents.EndPhase)
   # Remove events that should end when the turns finishes
   for restr in RS_KW_RESTRS_CLEANUP:
      cleanupGameEvents(restr)
      
   # Discard opponent reaction cards
   oppReactionCards = (card for card in table
      if card.controller != me
      and isReaction(card))
   for card in oppReactionCards:
      remoteCall(card.controller, 'discard', [card])


def cleanupPhaseStart():
   # Trigger event
   triggerGameEvent(GameEvents.CleanupPhase)
   
   clearKOedChars()

   # Clean my ring
   myCards = (card for card in table
      if card.controller == me)
   for card in myCards:
      if isCharacter(card):
         # Remove script makers
         removeMarker(card, 'Attack')
         removeMarker(card, 'United Attack')
         removeMarker(card, 'Counter-attack')
         removeMarker(card, 'Unfreezable')
         removeMarker(card, 'Pierce')
         # Clears targets, colors, freezes characters and resets position
         alignCard(card)
         if card.highlight == ActivatedColor:
            card.highlight = None
      # Discard any Action or Reaction card left in the table (just in case player forgot to remove them)
      else:
         discard(card)
   clearAll()


def clearKOedChars():
   # KOs characters with 0 BP
   if automations['AttackDmg']:
      charCards = (card for card in table
         if isCharacter(card) and not isAttached(card))
      for card in charCards:
         if getMarker(card, 'BP') == 0:
            notify("{}'s {} BP is 0. It will be KOed from the ring".format(card.controller, card))
            remoteCall(card.controller, "destroy", [card])


#------------------------------------------------------------------------------
# Play automations
#------------------------------------------------------------------------------

def playAuto(card, slotIdx=None, force=False):
   debug(">>> playAuto({})".format(card)) #Debug
   phaseIdx = currentPhase()[1]

   # Player plays a Character card
   if isCharacter(card):
      # If a char has been selected, backup that char instead
      targets = getTargetedCards(card)
      if len(targets) > 0:
         backup(card)
         return
      # Check if the card can be legally played
      if (not me.isActive or phaseIdx != MainPhase) and not force:
         information("Character cards can only be played on your Main Phase.")
         return
      # Limit of chars played per turn
      charsPlayed = getState(me, 'charsPlayed')
      if charsPlayed >= CharsPerTurn:
         if not confirm("Only {} character per turn can be played\n(you have played {} characters).\nProceed anyway?".format(CharsPerTurn, charsPlayed)):
            return
      # BP limit?
      bplimit = getRule('play_char_bp_limit')
      if bplimit:
         bplimit = reduce(lambda a,b: min(a,b), bplimit)
         if num(card.BP) / BPMultiplier >= bplimit:
            warning(MSG_RULES['play_char_bp_limit'][True].format(bplimit))
            return
      # Player has any empty slot in his ring?
      myRing = getGlobalVar('Ring', me)
      if myRing.count(None) == 0:
         warning("There is no emply slot in your ring where to play a character card.")
         return
      # Prompt the player to select an Empty Slot
      if slotIdx == None:
         slotIdx = askForSlot()
         if slotIdx == -1:
            return
      # Is really that slot empty?
      debug("Selected slot: {} ({})".format(slotIdx, myRing[slotIdx]))
      if myRing[slotIdx] != None:
         warning("Character card can't be played.\nThe selected slot is not empty (it's taken up by {}).\nIf you want to backup, please first target a character in your ring.".format(Card(myRing[slotIdx]).Name))
         return
      # Pay SP cost
      if not payCostSP(card.SP, card, cardType = CharType):
         return
      # Finally, the card is played
      placeCard(card, card.Type, PlayAction, slotIdx)
      # Parse the card to enable card autoscripts
      removeParsedCard(card)
      pcard = parseCard(card)
      setMarker(card, 'BP', num(card.BP) / BPMultiplier)
      # Triggers a hook whether the character can have the "just entered" marker
      if triggerHook(Hooks.PlayAsFresh, card._id):
         setMarker(card, 'Just Entered')
      putAtSlot(card, slotIdx)
      setState(me, 'charsPlayed', charsPlayed + 1)
      if pcard.hasEffect() and pcard.ability.type == InstantAbility:
         whisper(MSG_HINT_ACTIVATE)

   # Player plays an Action card
   elif isAction(card):
      # Triggers a hook to check if the player can play action cards
      if not triggerHook(Hooks.BeforePlayAC, me._id):
         return
      # Check if the card can be legally played
      if not me.isActive or phaseIdx != MainPhase:
         information("Action cards can only be played on your Main Phase.")
         return
      # Pay SP cost
      if not payCostSP(card.SP, card, cardType = ActionType):
         return
      placeCard(card, card.Type, PlayAction)
      # Parse the card to enable card autoscripts
      removeParsedCard(card)
      parseCard(card)
      whisper(MSG_HINT_ACTIVATE)
      # Remove "until next action card" events
      cleanupGameEvents(RS_KW_RESTR_UNAC)

   # Player plays a Reaction card
   elif isReaction(card):
      # Check if the card can be legally played
      if me.isActive or phaseIdx != BlockPhase:
         information("Reaction cards can only be played in enemy's Counter-attack Phase.")
         return
      # Triggers a hook to check if the player can play reaction cards
      if not triggerHook(Hooks.BeforePlayRE, me._id):
         return
      # Pay SP cost
      if not payCostSP(card.SP, card, cardType = ReactionType):
         return
      placeCard(card, card.Type, PlayAction)
      # Parse the card to enable card autoscripts
      removeParsedCard(card)
      parseCard(card)
      whisper(MSG_HINT_ACTIVATE)

   return True


def backupAuto(card):
   debug(">>> backupAuto()") #Debug

   # Check if the card can be legally played
   if not me.isActive or currentPhase()[1] != MainPhase:
      information("Characters can only be backed-up on your Main Phase.")
      return
   # Only for character cards
   if not isCharacter(card):
      warning("You can only backup with Character cards.")
      return
   # Check if a valid char has been selected
   myRing = getGlobalVar('Ring', me)
   targets = getTargetedCards(card)
   if len(targets) == 0 or not targets[0]._id in myRing:
      warning(MSG_SEL_CHAR_RING)
      return
   target = targets[0]
   # Backup limit
   backupsPlayed = getState(me, 'backupsPlayed')
   if backupsPlayed >= BackupsPerTurn:
      if triggerHook(Hooks.BackupLimit, target._id):
         if not confirm("Can't backup more than {} character per turn.\nProceed anyway?".format(CharsPerTurn)):
            return
   # Target just entered the ring?
   if MarkersDict['Just Entered'] in target.markers and not getRule('backup_fresh'):
      if not confirm("Characters that just entered the ring this turn can't be backed-up.\nProceed anyway?"):
         return
   # Target is frozen?
   if isFrozen(target):
      warning("Frozen characters can't be backed-up.")
      return
   # Check compatible backups
   acceptedBackups = getAcceptedBackups(target)
   if not card.Subtype in acceptedBackups:
      warning("Incompatible backups.\n{} only accepts {} character types.".format(target.Name, ', '.join(filter(None, acceptedBackups))))
      return
   # Check remaining backups
   avlbckps = acceptedBackups.count(card.Subtype)
   backups = getGlobalVar('Backups')
   for id in backups:
      if backups[id] == target._id:
         if Card(id).Subtype == card.Subtype:
            avlbckps -= 1
   if avlbckps <= 0:
      qty = acceptedBackups.count(card.Subtype)
      warning("{} can't be backed-up with more than {} {} card{}.".format(target.Name, qty, card.Subtype, plural(qty)))
      return
   # It's a legal backup
   attach(card, target)
   placeCard(card, card.Type, BackupAction, target)
   card.sendToBack()
   setMarker(card, 'Backup')
   addMarker(target, 'BP', BackupRaiseBP)  # Backed-up char's BP is raised
   setState(me, 'backupsPlayed', backupsPlayed + 1)
   triggerGameEvent(GameEvents.BackedUp, target._id)
   return target


def attackAuto(card):
   debug(">>> attackAuto()") #Debug

   # Check if we can attack
   if not me.isActive or currentPhase()[1] != AttackPhase:
      information("You can only attack in your Attack Phase.")
      return
   # Only for character cards...
   if not isCharacter(card):
      information("You can only attack with Character cards.")
      return
   # ... in player's ring
   slotIdx = getSlotIdx(card)
   if slotIdx == -1:
      warning("Please attack with a character in your ring.")
      return
   # Triggers a hook to check if the character can attack
   if not triggerHook([Hooks.BeforeAttack, card._id], card._id):
      return
   # Cancels the character's attack if it's already attacking
   if hasMarker(card, 'Attack') or hasMarker(card, 'United Attack'):
      removeMarker(card, 'Attack')
      removeMarker(card, 'United Attack')
      removeMarker(card, 'Unfreezable')
      clear(card, silent = True)
      alignCard(card)
      notify('{} cancels the attack with {}'.format(me, card))
      rearrangeUAttack(card)
      return
   # Char just entered the ring?
   if hasMarker(card, 'Just Entered'):
      if not confirm("Characters that just entered the ring can't attack this turn.\nProceed anyway?"):
         return
   # Frozen char?
   if isFrozen(card):
      warning("Frozen characters can't attack this turn.")
      return
   # United attack?
   targets = getTargetedCards(card)
   if len(targets) > 0:
      unitedAttack(card)
      return

   # Perform the attack
   setMarker(card, 'Attack')
   alignCard(card, slotIdx)

   return True


def unitedAttackAuto(card):
   debug(">>> unitedAttackAuto()") #Debug

   # Check if an attacking char has been selected
   myRing = getGlobalVar('Ring', me)
   targets = getTargetedCards(card)
   if len(targets) == 0 or not targets[0]._id in myRing or (not MarkersDict['Attack'] in targets[0].markers and not MarkersDict['United Attack'] in targets[0].markers):
      warning("Please select an attacking character in your ring.\n(Shift key + Left click on a character).")
      return
   target = targets[0]
   # Allowed uattacks
   uattack = getGlobalVar('UnitedAttack')
   if len(uattack) > 0:
      if uattack[0] != target._id:
         # If targeting other char in the uattack, change target to lead char
         if target._id in uattack:
            target.target(False)
            target = Card(uattack[0])
         else:
            warning("Only one United Attack is allowed.")
            return
   # Max chars per United Attack
   united = [c for c in table
      if c.controller == me
      and MarkersDict['United Attack'] in c.markers]
   if len(united) >= MaxCharsUAttack:
      warning("Can't be more than {} characters in a United Attack.".format(MaxCharsUAttack+1))
      return
   # Cost
   cost = (len(united)+1) * UAttackCost
   if cost > me.SP:
      type = 'Double' if len(united) == 0 else 'Triple'
      if not confirm("You do not seem to have enough SP to do a {} United Attack (it costs {}).\nProceed anyway?".format(type, cost)):
         return

   # Update UnitedAttack list
   uattack = getGlobalVar('UnitedAttack')
   if len(uattack) == 0:
      uattack.extend([target._id, card._id])
   else:
      uattack.append(card._id)
   setGlobalVar('UnitedAttack', uattack)
   debug("UnitedAttack: {}".format(uattack))

   setMarker(card, 'United Attack')
   target.target(False)
   alignCard(card)

   return target


def blockAuto(card):
   debug(">>> blockAuto()") #Debug

   # Check if the card can be legally played
   if me.isActive or currentPhase()[1] != BlockPhase:
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
      warning("Frozen characters can't counter-attack.")
      return
   # Triggers a hook to check if the character can counter-attack
   if not triggerHook([Hooks.BeforeBlock, card._id], card._id):
      return
   # Cancels the character's counter-attack if it's already blocking
   blockers = getGlobalVar('Blockers')
   if MarkersDict['Counter-attack'] in card.markers:
      removeMarker(card, 'Counter-attack')
      clear(card, silent = True)
      alignCard(card)
      for i in blockers:
         if blockers[i] == card._id:
            del blockers[i]
            debug("Removed blocker {}".format(blockers)) #Debug
            setGlobalVar('Blockers', blockers)
            break
      notify('{} cancels the counter-attack with {}'.format(me, card))
      return
   # Check if an attacking enemy char has been selected
   enemyRing = getGlobalVar('Ring', players[1])
   targets = getTargetedCards(card, True, False)
   if len(targets) == 0 or not targets[0]._id in enemyRing or not MarkersDict['Attack'] in targets[0].markers:
      warning("Please select an attacking enemy character (Shift key + Left click on a character).\nIf blocking an United Attack, then select the leading character.")
      return
   target = targets[0]
   # An attacker can only be blocked by exactly 1 char
   if target._id in blockers:
      warning("An attacking character can only be blocked by exactly one char")
      return

   # Triggers a hook to check if block is possible
   addActionTempVars('attacker', [target])
   addActionTempVars('blocker', [card])
   if not triggerHook([Hooks.CanBeBlocked, target._id], target._id):
      return

   setMarker(card, 'Counter-attack')
   # Save attacker => blocker
   blockers[target._id] = card._id
   setGlobalVar('Blockers', blockers)
   # card.arrow(target)
   target.target(False)
   alignCard(card)

   return target


def activateAuto(card):
   debug(">>> activateAuto()") #Debug

   if card.highlight == ActivatedColor:
      whisper("{}'s ability or effect has already been activated".format(card))
      return
   # Character ability
   if isCharacter(card):
      pcard = getParsedCard(card)
      if not pcard.hasEffect():
         whisper("{} has no ability to activate".format(card))
         return
      debug("Trying to activate {}'s ability {} {}".format(card.Name, pcard.ability.type, pcard.ability.name))
      # Activate [] and /\ only in player's Main Phase
      if pcard.ability.type in [InstantAbility, TriggerAbility] and (not me.isActive or currentPhase()[1] != MainPhase):
         information("You can only activate {} or {} abilities in your Main Phase.".format(TriggerUniChar, InstantUniChar))
         return
      # /\ abilities
      if pcard.ability.type == InstantAbility:
         # Check if [] abilites can be activated
         if not getRule('ab_instant_act'):
            warning(MSG_RULES['ab_instant_act'][False])
            return
         # Activate only once
         if not hasMarker(card, 'Just Entered'):
            warning("{} abilities can only be activated once when character just enters the ring.".format(InstantUniChar))
            return
      # [] abilities
      if pcard.ability.type == TriggerAbility:
         # Check if [] abilites can be activated
         if not getRule('ab_trigger_act'):
            warning(MSG_RULES['ab_trigger_act'][False])
            return
         # Just entered?
         if not getRule('ab_trigger_fresh') and hasMarker(card, 'Just Entered'):
            if not confirm("Can't activate {} abilities of characters that just entered the ring.\nProceed anyway?".format(TriggerUniChar)):
               return
         # Frozen or attacking?
         if isFrozen(card) or hasMarker(card, 'Attack'):
            warning("Can't activate {} abilities of frozen or attacking characters.".format(TriggerUniChar))
            return
      # () abilities
      if pcard.ability.type == AutoAbility:
         # Nor in a United Attack
         if hasMarker(card, 'United Attack'):
            warning("Can't activate {} abilities of characters which joined a United Attack.".format(AutoUniChar))
            return

      # Activate [] ability?
      if pcard.ability.type == TriggerAbility:
         if not confirm("Activate {}'s ability {} {}?\n\n\n{}".format(card.Name, pcard.ability.unicodeChar, pcard.ability.name, pcard.ability.rules)):
            return
      # Activate the ability
      return pcard.activateEffect()
   # Rest of cards
   else:
      pcard = getParsedCard(card)
      return pcard.activateEffect()


def rearrangeUAttack(card):
   # Rearrange or cancels a uattack if the card was part of it
   debug(">>> rearrangeUAttack()") #Debug
   uattack = getGlobalVar('UnitedAttack')
   if card._id in uattack:
      notify("{} was part of an United Attack. Now it will be rearranged.".format(card))
      uatttackIdx = uattack.index(card._id)
      uattack.remove(card._id)
      uattack = filter(None, uattack)
      setGlobalVar('UnitedAttack', uattack)
      # If it was the lead card, or only 1 char left, cancel uattack
      if uatttackIdx == 0 or len(uattack) == 1:
         notify('{} cancels the United Attack'.format(me))
         for cid in uattack:
            c = Card(cid)
            removeMarker(c, 'United Attack')
            setMarker(c, 'Attack')
            c.highlight = AttackColor
            alignCard(c)
         clearGlobalVar('UnitedAttack')
      # Reorder remaining united attackers
      else:
         for cid in uattack[1:]:
            alignCard(Card(cid))
      debug("UnitedAttack: {}".format(getGlobalVar('UnitedAttack')))
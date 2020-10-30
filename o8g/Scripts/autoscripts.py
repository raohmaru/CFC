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

#------------------------------------------------------------------------------
# Start/End of Turn/Phase triggers
#------------------------------------------------------------------------------

def triggerPhaseEvent(phase, oldPhase = 0):
   # Function which triggers effects at the start or end of the phase
   debug(">>> triggerPhaseEvent({})".format(phase))
   mute()
   if not settings['Play']: return
   
   # Going backwards?
   if phase < oldPhase: return
   
   skipPhases = getState(me, 'skip')
   if phase in skipPhases:
      notify("{} skips his {} phase due to an ability.".format(me, Phases[phase]))
      skipPhases.remove(phase)  # remove by value
      setState(me, 'skip', skipPhases)
      nextPhase(False)
      return

   if   phase == ActivatePhase: activatePhaseStart()
   elif phase == DrawPhase:
      if turnNumber() == 1:
         notify("{} skips their {} phase (the first player must skip it during their first turn).".format(me, Phases[phase]))
         nextPhase(False)
         return
      else:
         drawPhaseStart()
   elif phase == MainPhase:   mainPhaseStart()
   elif phase == AttackPhase: attackPhaseStart()
   elif phase == BlockPhase:
      if len(getAttackingCards(me, True)) == 0:
         notify("{} skips their {} phase because there are no attacking characters.".format(me, Phases[phase]))
         nextPhase(False)
         return
      else:
         blockPhaseStart()
   elif phase == EndPhase:      endPhaseStart()
   elif phase == CleanupPhase:  cleanupPhaseStart()
   
   global phaseOngoing
   phaseOngoing = False
   
   # Automatic phase change
   if settings['Phase']:
      if not getStop(phase) and (
            phase not in [MainPhase, AttackPhase, BlockPhase, EndPhase]
            or phase == EndPhase and len(getAttackingCards()) == 0
      ):
         # time.sleep(0.1)  # Blocks main thread
         # Waiting for opponent's ping does not seems a good idea. Eitherway, in online games
         # there is a delay before moving to next phase.
         # rnd(1, 100)  # Trying to delay nextPhase
         # update()
         nextPhase(False)
      elif getStop(phase):
         addButton('NextButton')


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
         removeMarker(card, 'Counter-attack')
         clear(card)
         alignCard(card)
      # Discard any Action or Reaction card left in the table (just in case player forgot to remove them)
      else:
         discard(card)
   frostedChars = ''
   if frosted:
      frostedChars = " but {}".format(cardsNamesStr(frosted))
   notify("{} unfreezes all characters in their ring{}.".format(me, frostedChars))
   # Trigger event
   triggerGameEvent(GameEvents.ActivatePhase)
   cleanupGameEvents(RS_KW_RESTR_UYNT)
   # Add buttons
   if not settings['Phase']:
      addButton('NextButton')


def drawPhaseStart():
   if settings['Play']:
      if len(me.Deck) == 0 and len(players) > 1 and not tutorial:
         notify("{} has no cards in their deck and therefore can't draw.".format(me))
         notifyWin(getOpp())
      else:
         draw()
   # Trigger event
   triggerGameEvent(GameEvents.DrawPhase)
   alignCards()


def mainPhaseStart():
   alignCards()
   if settings['Phase']:
      addButton('NextButton')
      
   for card in table:
      card.target(False)


def attackPhaseStart():
   preparePhase()
   clearKOedChars()
   for card in table:
      if card.controller == me:
         # Discard action cards I have played
         if isAction(card):
            discard(card)
         elif isCharacter(card):
            card.target(False)
            alignCard(card)


def blockPhaseStart():
   if not tutorial:
      removeButton('NextButton')
   uattack = getGlobalVar('UnitedAttack')
   # Attacking chars event not in UA
   atkCards = getAttackingCards()
   if settings['Play']:
      if len(uattack) > 0:
         chars = len(uattack) - 1
         uatype = ["Double", "Triple"][chars-1] + " United Attack"
         uacost = "ua{}".format(len(uattack))
         payCostSP(-chars*UAttackCost, uatype, "do a {}".format(uatype), uacost)
         notify("{} has paid the cost of the {}".format(me, uatype))
   triggerGameEvent(GameEvents.BlockPhase)
   for card in atkCards:
      if len(uattack) == 0 or uattack[0] != card._id:
         triggerGameEvent([GameEvents.Attacks, card._id], card._id)
   alignCards()
   # Pass priority to opponent
   setState(None, 'priority', getOpp()._id)


def endPhaseStart():
   preparePhase()
   clearKOedChars()

   # Freeze attacking characters
   freezeAtk = getRule('attack_freeze')
   myCards = (card for card in table
      if card.controller == me)
   for card in myCards:
      if isCharacter(card):
         alignCard(card)
         if freezeAtk and isAttacking(card) and not hasMarker(card, 'Unfreezable'):
            freeze(card, unfreeze = False, silent = True)
      else:
         discard(card)

   # Calculates and applies attack damage
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
         # Add attacking cards to action local variables & trigger game event
         addTempVar('attacker', [card])
         addTempVar('uaBP', dmg + pdmg)
         triggerGameEvent([GameEvents.Blocks, blocker._id], blocker._id)
         update()
         # Trigger blocked event if not in UA
         if pdmg == 0:
            triggerGameEvent([GameEvents.Blocked, card._id], card._id)
         blocker_bp = getMarker(blocker, 'BP')
         dealDamage(dmg + pdmg, blocker, card)
         dealDamage(blocker_bp, card, blocker)
         # Blocker damages to chars in United Attack
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
         # Piercing damage of United Attack
         uadmg = dmg + pdmg - blocker_bp
         if (
               len(players) > 1 and
               getRule('piercing') and
               uadmg > 0 and
               (
                  (isUA and triggerHook([Hooks.PreventPierce, blocker._id], blocker._id) != False)
                  # One does not simply stop Haohmaru
                  or hasMarker(card, 'Pierce')
               )
            ):               
            dealDamage(uadmg, players[1], card, isPiercing = True)
         elif pdmg > 0 and uadmg > 0:
            notify("{} points of piercing damage were prevented.".format(uadmg))
      # Unblocked attacker
      elif len(players) > 1:
         doDamage = True
         if triggerHook([Hooks.CancelCombatDamage, card._id], card._id) == True:
            doDamage = False
         if doDamage:
            dealDamage(dmg + pdmg, players[1], card)
         triggerGameEvent([GameEvents.PlayerCombatDamaged, card._id], card._id)
      update() # Syncs the game state along players. Also delays animations.

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
   
   # Remove buttons?
   if settings['Phase'] and not atkCards:
      removeButton('NextButton')
   else:
      addButton('NextButton')


def cleanupPhaseStart():
   if settings['Phase']:
      removeButton('NextButton')
   preparePhase()
   clearKOedChars()
   rnd(10, 1000)  # Delay until all animation is done
   clearAll()
   triggerGameEvent(GameEvents.CleanupPhase)
   rnd(10, 1000)  # Delay until all animation is done
   # Clean up my ring
   myCards = [card for card in table
      if card.controller == me]
   for card in myCards:
      if isCharacter(card):
         # Remove scripted makers
         removeMarker(card, 'Attack')
         removeMarker(card, 'United Attack')
         removeMarker(card, 'Counter-attack')
         removeMarker(card, 'Unfreezable')
         removeMarker(card, 'Pierce')
         # Clears targets, colors and resets position
         alignCard(card)
         if card.highlight == ActivatedColor:
            card.highlight = None
      # Discard any Action or Reaction card left in the table (just in case player forgot to remove them)
      else:
         discard(card)


def clearKOedChars():
   # KOs characters with 0 BP
   for card in getRing():
      if getMarker(card, 'BP') == 0:
         notify("{}'s {} BP is 0. It will be KOed from the ring.".format(card.controller, card))
         if card.controller == me:
            destroy(card)
            update()  # Syncs the game state along players. Also delays animations.
         else:
            remoteCall(card.controller, "destroy", [card, 0, 0, card.controller])
            remoteCall(card.controller, "update", [])


def preparePhase():
   clearGlobalVar('TempVars') # Reset action local variables
   
   # In multiplayer games global variables could not be sync if players simultaneously modify them.
   # Nevertheless, needs more testing to ensure that this is absolutely necessary.

   cards = [c._id for c in table
            if isCharacter(c)]
   
   # Ensure there aren't any "ghost" id in the ring
   ring = getGlobalVar('Ring', me)
   changed = False
   for id in ring:
      if id != None and id not in cards:
         ring[ring.index(id)] = None
         changed = True
   if changed:
      setGlobalVar('Ring', ring, me)
   
   if len(players) > 1:
      ring = getGlobalVar('Ring', players[1])
      changed = False
      for id in ring:
         if id != None and id not in cards:
            ring[ring.index(id)] = None
            changed = True
      if changed:
         setGlobalVar('Ring', ring, players[1])
      
   # Events
   ge = getGlobalVar('GameEvents')
   changed = False
   for e in list(reversed(ge)):
      if e['restr'] is None:
         source = e['source']
         id = e['id']
         if (
            (source and (source not in cards and isCharacter(Card(source)) or not Card(source).Rules))
            or (id not in cards and isCharacter(Card(id)) or not Card(id).Rules)
         ):
            ge.remove(e)
            changed = True
   if changed:
      setGlobalVar('GameEvents', ge)
   
   # Modifiers
   Modifiers = getGlobalVar('Modifiers')
   changed = False
   for t in Modifiers:
      for m in list(reversed(Modifiers[t])):
         if not m[0] in cards and isCharacter(Card(m[0])):
            Modifiers[t].remove(m)
            changed = True
   if changed:
      setGlobalVar('Modifiers', Modifiers)
   
   # Rules
   Rules = getGlobalVar('Rules')
   changed = False
   for r in Rules:
      for id in Rules[r].keys():
         if not id in cards and isCharacter(Card(id)):
            del Rules[r][id]
            changed = True
   if changed:
      setGlobalVar('Rules', Rules)
      
   # Unhighlight avaible backup cards in hand
   for c in me.hand:
      if c.highlight == InfoColor:
         c.highlight = None
   
   update()


#------------------------------------------------------------------------------
# Play settings
#------------------------------------------------------------------------------

def playAuto(card, slotIdx=None, force=False):
   debug(">>> playAuto({})".format(card))
   preparePhase()
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
      charsPerTurn = getState(me, 'charsPerTurn')
      if charsPlayed >= charsPerTurn:
         warning("Only {} character card{} per turn can be played.\n(You have played {} character{}.)".format(charsPerTurn, plural(charsPerTurn), charsPlayed, plural(charsPlayed)))
         return
      # BP limit?
      bplimit = getRule('play_char_bp_limit')
      if bplimit:
         bplimit = reduce(lambda a,b: min(a,b), bplimit)
         if num(card.BP) >= bplimit:
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
      # Is really empty that slot?
      debug("Selected slot: {} ({})".format(slotIdx, myRing[slotIdx]))
      if myRing[slotIdx] != None:
         warning("Character card can't be played, the slot is not empty (it's taken up by {}).\nIf you want to backup, please first target a character in your ring.".format(Card(myRing[slotIdx]).Name))
         return
      # Pay SP cost
      if not payCostSP(card.SP, card, type = CharType):
         return
      # Finally, the card is played
      placeCard(card, card.Type, PlayAction, slotIdx)
      # Parse the card to enable card autoscripts
      removeParsedCard(card)
      pcard = parseCard(card)
      setMarker(card, 'BP', num(card.BP))
      # Triggers a hook whether the character can have the "just entered" marker
      if triggerHook(Hooks.PlayAsFresh, card._id) != False:
         setMarker(card, 'Just Entered')
      putAtSlot(card, slotIdx)
      setState(me, 'charsPlayed', charsPlayed + 1)

   # Player plays an Action card
   elif isAction(card):
      # Triggers a hook to check if the player can play action cards
      if triggerHook(Hooks.BeforePlayAC, me._id) == False:
         return
      # Check if the card can be legally played
      if not me.isActive or phaseIdx != MainPhase:
         information("Action cards can only be played on your Main Phase.")
         return
      # Pay SP cost
      if not payCostSP(card.SP, card, type = ActionType):
         return
      placeCard(card, card.Type, PlayAction)
      # Parse the card to enable card autoscripts
      removeParsedCard(card)
      parseCard(card)
      # Remove "until next action card" events
      cleanupGameEvents(RS_KW_RESTR_UNAC)

   # Player plays a Reaction card
   elif isReaction(card):
      # Check if the card can be legally played
      if (me.isActive or phaseIdx != BlockPhase) and not debugging and not tutorial:
         information("Reaction cards can only be played in enemy's Counter-attack Phase.")
         return
      # Triggers a hook to check if the player can play reaction cards
      if triggerHook(Hooks.BeforePlayRE, me._id) == False:
         return
      # Pay SP cost
      if not payCostSP(card.SP, card, type = ReactionType):
         return
      placeCard(card, card.Type, PlayAction)
      # Parse the card to enable card autoscripts
      removeParsedCard(card)
      parseCard(card)

   return True


def backupAuto(card, target = None):
   debug(">>> backupAuto()")

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
   if not target:
      targets = getTargetedCards(card)
      if len(targets) == 0 or not targets[0]._id in myRing:
         targets = []
         # Get a compatible character in the ring
         for c in getRing(me):
            acceptedBackups = getAcceptedBackups(c)
            if card.Subtype in acceptedBackups:
               targets.append(c)
         if targets:
            targets = showCardDlg(targets, 'Select a character to back-up')
            if targets == None:
               return
         else:
            warning('There are not compatible characters to back-up in your ring.')
            return
      target = targets[0]
   # Target is frozen?
   if isFrozen(target):
      warning("Frozen characters can't be backed-up.")
      return
   # Target just entered the ring?
   if MarkersDict['Just Entered'] in target.markers and not getRule('backup_fresh'):
      warning("Characters that just entered the ring this turn can't be backed-up.")
      return
   # Backup limit
   backupsPlayed = getState(me, 'backupsPlayed')
   if backupsPlayed >= BackupsPerTurn:
      if getRule('backup_limit') and triggerHook([Hooks.BackupLimit, target._id]) != False:
         warning("Can't backup more than {} character per turn.".format(BackupsPerTurn))
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
   oldBP = getMarker(target, 'BP')
   addMarker(target, 'BP', BackupRaiseBP)  # Backed-up char's BP is raised
   setState(me, 'backupsPlayed', backupsPlayed + 1)
   triggerGameEvent(GameEvents.BackedUp, target._id)
   return (target, oldBP)


def attackAuto(card, force = False):
   debug(">>> attackAuto()")

   # Check if we can attack
   if not force and (not me.isActive or currentPhase()[1] != AttackPhase):
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
   if not getRule('attack'):
      warning(MSG_ERR_CANNOT_ATTACK.format(card.Name))
      return
   # Triggers a hook to check if the character can attack
   if triggerHook([Hooks.BeforeAttack, card._id], card._id) == False:
      return
   # Cancels the character's attack if it's already attacking
   if isAttacking(card):
      cancelAttack(card)
      return
   # Char just entered the ring?
   if hasMarker(card, 'Just Entered'):
      warning(MSG_ERR_ATTACK_FRESH)
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


def unitedAttackAuto(card, targets = None, force = False):
   debug(">>> unitedAttackAuto()")

   # Is char in player's ring?
   if not charIsInRing(card):
      warning(MSG_ERR_ATTACK_CHAR_RING)
      return 
   # If is the only attacker, do a regular attack
   if len(getAttackingCards(me)) == 0:
      attack(card)
      return
   # Check if attack is allowed
   if not getRule('attack'):
      warning(MSG_ERR_CANNOT_ATTACK.format(card.Name))
      return
   # Char just entered the ring?
   if hasMarker(card, 'Just Entered'):
      warning(MSG_ERR_ATTACK_FRESH)
      return
   # Triggers a hook to check if the character can attack
   if triggerHook([Hooks.BeforeAttack, card._id], card._id) == False:
      return
   # Cancels the character's attack if it's already attacking
   if not force and isAttacking(card):
      cancelAttack(card)
      return
   # Check if an attacking char has been selected
   myRing = getGlobalVar('Ring', me)
   if not targets:
      targets = getTargetedCards(card)
   if len(targets) == 0 or not targets[0]._id in myRing or not isAttacking(targets[0]):
      if not force:
         targets = getAttackingCards()
         if len(targets) > 1:
            targets = showCardDlg(targets, 'Select an attacking character to join an United Attack.')
         if not targets:
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
   # Current chars in the United Attack
   united = [c for c in table
      if c.controller == me
      and MarkersDict['United Attack'] in c.markers]
   # Max chars per United Attack
   if len(united) >= MaxCharsUAttack:
      if not force:
         warning(MSG_UA_MAX.format(MaxCharsUAttack+1))
      else:
         notify(MSG_UA_MAX.format(MaxCharsUAttack+1))
      return
   totalUnited = len(united) + 1 # Chars in UA + current char
   # Cost
   if not force:
      cost = totalUnited * UAttackCost
      cost = getCostMod(cost, "ua" + str(totalUnited+1))
      if cost > me.SP:
         type = ["Double", "Triple"][totalUnited-1]
         warning("You do not have enough SP to do a {} United Attack (it costs {} SP).".format(type, cost))
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
   removeMarker(card, 'Attack')
   target.target(False)
   alignCard(card)
   card.highlight = UnitedAttackColor  # yep also in actions.py unitedAttack()

   return target


def blockAuto(card, targets = None):
   debug(">>> blockAuto()")

   # Check if the card can be legally played
   if (me.isActive or currentPhase()[1] != BlockPhase) and not tutorial:
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
   if triggerHook([Hooks.BeforeBlock, card._id], card._id) == False:
      return
   # Cancels the character's counter-attack if it's already blocking
   if MarkersDict['Counter-attack'] in card.markers:
      cancelBlock(card)
      return
   # Check if an attacking enemy char has been selected
   blockers = getGlobalVar('Blockers')
   enemyRing = getGlobalVar('Ring', players[1])
   targeted = False
   if not targets:
      targets = getTargetedCards(card, True, False)
      targeted = True
   if len(targets) > 0:
      if not targets[0]._id in enemyRing or not isAttacking(targets[0], False):
         if targeted:
            warning("Please select an attacking character (Shift key + Left click on a character card).\nIf blocking an United Attack, then select the leading character.")
         return
   if len(targets) == 0:
      # Automatically select an attacking character if there is only one...
      atkCards = [c for c in getAttackingCards(getOpp())
         if c._id not in blockers]
      if len(atkCards) == 1:
         targets = atkCards
      elif len(atkCards) > 1:
         # ...or show card dialog to choose
         targets = showCardDlg(atkCards, 'Select an attacking character to counter-attack with {}.'.format(card.Name))
      else:
         whisper('There are not available attacking characters to block.')
         whisper("({})".format(MSG_ERR_BLOCK_ONE))
      if not targets:
         return
   target = targets[0]
   # An attacker can only be blocked by exactly 1 char
   if target._id in blockers:
      warning(MSG_ERR_BLOCK_ONE)
      return

   # Triggers a hook to check if block is possible
   addTempVar('attacker', [target])
   addTempVar('blocker', [card])
   if triggerHook([Hooks.CanBeBlocked, target._id], target._id) == False:
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
   debug(">>> activateAuto()")
   
   preparePhase()

   if card.highlight == ActivatedColor:
      notify("{}'s ability or effect has already been activated".format(card))
      return
   # Character ability
   if isCharacter(card):
      pcard = getParsedCard(card)
      if not pcard.hasEffect():
         notify("{} has no ability to activate".format(card))
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
            if not settings['Activate']:
               warning(MSG_RULES['ab_instant_act'][False])
            else:
               playSnd('cancel-2')
            notify(MSG_RULES['ab_instant_act'][False])
            return
         # Activate only once
         if not hasMarker(card, 'Just Entered'):
            warning("{} abilities can only be activated once when the character just enters the ring.".format(InstantUniChar))
            return
      # [] abilities
      if pcard.ability.type == TriggerAbility:
         # Check if [] abilites can be activated
         if not getRule('ab_trigger_act'):
            warning(MSG_RULES['ab_trigger_act'][False])
            return
         # Just entered?
         if not getRule('ab_trigger_fresh') and hasMarker(card, 'Just Entered'):
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
      pcard = getParsedCard(card)
      return pcard.activateEffect()


#---------------------------------------------------------------------------
# Related functions
#---------------------------------------------------------------------------

def rearrangeUAttack(card):
   # Rearrange or cancels a uattack if the card was part of it
   debug(">>> rearrangeUAttack()")
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
      debug("UnitedAttack: {}".format(uattack))
      

def cancelAttack(card, silent = False):
   removeMarker(card, 'Attack')
   removeMarker(card, 'United Attack')
   removeMarker(card, 'Unfreezable')
   clear(card)
   alignCard(card)
   rearrangeUAttack(card)
   if not silent:
      notify('{} cancels the attack with {}'.format(me, card))
      playSnd('cancel-1')
   

def cancelBlock(card, silent = False):
   removeMarker(card, 'Counter-attack')
   clear(card)
   alignCard(card)
   blockers = getGlobalVar('Blockers')
   for i in blockers:
      if blockers[i] == card._id:
         del blockers[i]
         debug("Removed blocker {}".format(blockers))
         setGlobalVar('Blockers', blockers)
         break
   if not silent:
      notify('{} cancels the counter-attack with {}'.format(me, card))
      playSnd('cancel-1')

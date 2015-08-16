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

def triggerPhaseEvent(phase): # Function which triggers effects at the start or end of the phase
   debug(">>> triggerPhaseEvent({})".format(phase)) #Debug
   mute()
   if not automations['Phase']: return
   
   if phase == ActivatePhase:
      # Unfreeze characters in the player's ring, clear colors and remove script markers
      notify("{} unfreezes all characters in their ring.".format(me))
      myCards = (card for card in table
         if card.controller == me)
      for card in myCards:
         if card.Type == 'Character':
            if not MarkersDict['DoesntUnfreeze'] in card.markers:
               freeze(card, unfreeze = True, silent = True)
            removeMarker(card, 'JustEntered')
            clear(card, silent = True)
         # Discard any Action or Reaction card left in the table (just in case player forgot to remove them)
         elif card.Type == 'Action' or card.Type == 'Reaction':
            discard(card)
   
   elif phase == DrawPhase:
      if automations['Play']:
         if len(me.Deck) == 0 and len(players) > 1:
            notify("{} has no cards in their deck and therefore can't draw.\n{} wins the game!".format(me,players[1]))
   
   elif phase == BlockPhase:
      if automations['Play']:
         uattack = getGlobalVar('UnitedAttack')
         if len(uattack) > 0:
            chars = len(uattack) - 1
            payCostSP(-chars*UAttackCost, msg = "do a {} United Attack".format("Double" if chars == 1 else "Triple"))
   
   elif phase == EndPhase:
      myCards = (card for card in table
         if card.controller == me)
      for card in myCards:
         if card.Type == 'Character':
            if (MarkersDict['Attack'] in card.markers or MarkersDict['UnitedAttack'] in card.markers) and not MarkersDict['NoFreeze'] in card.markers:
               freeze(card, unfreeze = False, silent = True)
   
   elif phase == CleanupPhase:
      myCards = (card for card in table
         if card.controller == me)
      for card in myCards:
         if card.Type == 'Character':
            # Clears targets, colors, freezes characters and resets position
            alignCard(card)
            # Remove script makers
            removeMarker(card, 'Attack')
            removeMarker(card, 'UnitedAttack')
            removeMarker(card, 'CounterAttack')
            removeMarker(card, 'NoFreeze')
         # Discard any Action or Reaction card left in the table (just in case player forgot to remove them)
         elif card.Type == 'Action' or card.Type == 'Reaction':
            discard(card)
      clearAll()


#------------------------------------------------------------------------------
# Play automations
#------------------------------------------------------------------------------

def playAuto(card, slotIdx=None):
   debug(">>> playAuto({})".format(card)) #Debug
   global charsPlayed
   phaseIdx = getGlobalVar('PhaseIdx', me)
   
   # Player plays a Character card
   if card.Type == 'Character':
      # If a char has been selected, backup that char instead
      targets = getTargetedCards(card)
      if len(targets) > 0:
         backup(card)
         return
      # Check if the card can be legally played
      if not me.isActivePlayer or phaseIdx != MainPhase:
         information("Character cards can only be played on your Main Phase.")
         return
      # Limit of chars played per turn
      if charsPlayed >= CharsPerTurn:
         if not confirm("Only {} character per turn can be played.\nProceed anyway?".format(CharsPerTurn)):
            return
      # Player has any empty slot in his ring?
      myRing = getGlobalVar('Ring', me)
      if myRing.count(None) == 0:
         warning("There is no emply slot in your ring where to play a character card.")
         return
      # Prompt the player to select an Empty Slot
      if slotIdx == None:
         emptySlots = []
         for i, id in enumerate(myRing):
            if id == None:
               emptySlots.append(str(i+1))
         slotIdx = askChoice("Select an empty slot:", emptySlots)
         debug("Selected option {} ({})".format(slotIdx, slotIdx-1))
         if slotIdx == 0:
            return
         slotIdx = int(emptySlots[slotIdx-1]) - 1
      # Is really that slot empty?
      debug("Selected slot: {} ({})".format(slotIdx, myRing[slotIdx]))
      if myRing[slotIdx] != None:
         warning("Character card can't be played.\nThe selected slot is not empty (it's taken up by {}).\nIf you want to backup, please first target a character in your ring.".format(Card(myRing[slotIdx]).Name))
         return
      # Pay SP cost
      if payCostSP(card.SP) == ERR_CANT_PAY_SP:
         return
      # Finally, the card is played
      placeCard(card, card.Type, PlayAction, slotIdx)
      setMarker(card, 'BP', num(card.BP) / 100)
      setMarker(card, 'JustEntered')
      myRing[slotIdx] = card._id
      setGlobalVar('Ring', myRing, me)
      charsPlayed += 1
      debug("{}'s ring: {}".format(me, myRing))
   
   # Player plays an Action card
   elif card.Type == 'Action':
      # Check if the card can be legally played
      if not me.isActivePlayer or phaseIdx != MainPhase:
         information("Action cards can only be played on your Main Phase.")
         return
      # Pay SP cost
      if payCostSP(card.SP) == ERR_CANT_PAY_SP:
         return
      placeCard(card, card.Type, PlayAction)
   
   # Player plays a Reaction card
   elif card.Type == 'Reaction':
      # Check if the card can be legally played
      if me.isActivePlayer or getGlobalVar('PhaseIdx', players[1]) != BlockPhase:
         information("Reaction cards can only be played in enemy's Counter-attack Phase.")
         return
      # Pay SP cost
      if payCostSP(card.SP) == ERR_CANT_PAY_SP:
         return
      placeCard(card, card.Type, PlayAction)
   # Player plays an unknow card
   else:
      placeCard(card, card.Type)
      
   return True


def backupAuto(card):
   debug(">>> backupAuto()") #Debug
   global backupsPlayed
   
   # Check if the card can be legally played
   if not me.isActivePlayer or getGlobalVar('PhaseIdx', me) != MainPhase:
      information("Characters can only be backed-up on your Main Phase.")
      return
   # Only for character cards
   if card.Type != 'Character':
      warning("You can only backup with Character cards.")
      return
   # Check if a valid char has been selected
   myRing = getGlobalVar('Ring', me)
   targets = getTargetedCards(card)
   if len(targets) == 0 or not targets[0]._id in myRing:
      warning("Please select a character in your ring.\n(Shift key + Left click on a character).")
      return
   target = targets[0]
   # Backup limit
   if backupsPlayed >= BackupsPerTurn:
      if not confirm("Can't backup more than {} character per turn.\nProceed anyway?".format(CharsPerTurn)):
         return
   # Target just entered the ring?
   if MarkersDict['JustEntered'] in target.markers:
      if not confirm("Characters that just entered the ring this turn can't be backed-up.\nProceed anyway?"):
         return
   # Target is freezed?
   if target.orientation & Rot90 == Rot90:
      warning("Freezed characters can't be backed-up.")
      return
   # Check compatible backups
   acceptedBackups = (target.properties['Backup 1'], target.properties['Backup 2'], target.properties['Backup 3'])
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
      warning("{} can't be backed-up with more than {} {} card(s).".format(target.Name, acceptedBackups.count(card.Subtype), card.Subtype))
      return   
   # It's a legal backup
   attach(card, target)
   placeCard(card, card.Type, BackupAction, target)
   card.sendToBack()
   setMarker(card, 'Backup')
   addMarker(target, 'BP', BackupRaiseBP)  # Backed-up char's BP is raised
   backupsPlayed += 1
   return target


def attackAuto(card):
   debug(">>> attackAuto()") #Debug
   
   # Check if we can attack
   if not me.isActivePlayer or getGlobalVar('PhaseIdx', me) != AttackPhase:
      information("You can only attack in your Attack Phase.")
      return
   # Only for character cards...
   if card.Type != 'Character':
      information("You can only attack with Character cards.")
      return
   # ... in player's ring
   slotIdx = getSlotIdx(card)
   myRing = getGlobalVar('Ring', me)
   if slotIdx == -1 or myRing[slotIdx] != card._id:
      warning("Please attack with a character in your ring.")
      return
   # Cancels the character's attack if it's already attacking
   if MarkersDict['Attack'] in card.markers or MarkersDict['UnitedAttack'] in card.markers:
      removeMarker(card, 'Attack')
      removeMarker(card, 'UnitedAttack')
      removeMarker(card, 'NoFreeze')
      clear(card, silent = True)
      alignCard(card)
      notify('{} cancels the attack with {}'.format(me, card))
      # Was the card in a uattack?
      uattack = getGlobalVar('UnitedAttack')
      if card._id in uattack:
         uatttackIdx = uattack.index(card._id)
         uattack.remove(card._id)
         setGlobalVar('UnitedAttack', uattack)
         # If it was the lead card, or only 1 char left, cancel uattack
         if uatttackIdx == 0 or len(uattack) == 1:
            for cid in uattack:
               c = Card(cid)
               removeMarker(c, 'UnitedAttack')
               setMarker(c, 'Attack')
               c.highlight = AttackColor
            clearGlobalVar('UnitedAttack')
         debug("UnitedAttack: {}".format(getGlobalVar('UnitedAttack')))
      return
   # Char just entered the ring?
   if MarkersDict['JustEntered'] in card.markers:
      if not confirm("Characters that just entered the ring can't attack this turn.\nProceed anyway?"):
         return
   # Frozen char?
   if card.orientation & Rot90 == Rot90:
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
   if len(targets) == 0 or not targets[0]._id in myRing or (not MarkersDict['Attack'] in targets[0].markers and not MarkersDict['UnitedAttack'] in targets[0].markers):
      warning("Please select an attacking character in your ring.\n(Shift key + Left click on a character).")
      return
   target = targets[0]   
   # Allowed uattacks
   uattack = getGlobalVar('UnitedAttack')
   if len(uattack) > 0:
      if uattack[0] != target._id:
         # If targetting other char in the uattack, change target to lead char
         if target._id in uattack:
            target = Card(uattack[0])
         else:
            warning("Only one United Attack is allowed.")
            return
   # Max chars per United Attack
   united = [c for c in table
      if c.controller == me
      and MarkersDict['UnitedAttack'] in c.markers]
   if len(united) >= MaxCharsUAttack:
      warning("Can't be more than {} characters in a United Attack.".format(MaxCharsUAttack+1))
      return
   # Cost
   cost = (len(united)+1) * UAttackCost
   if cost > me.SP:
      type = 'Double' if len(united) == 0 else 'Triple'
      if not confirm("You do not seem to have enough SP to do a {} United Attack (it costs {}).\nProceed anyway?".format(type, cost)):
         return
   
   setMarker(card, 'UnitedAttack')
   card.arrow(target)
   target.target(False)
   alignCard(card, getSlotIdx(card))
   
   # Update UnitedAttack list
   uattack = getGlobalVar('UnitedAttack')
   if len(uattack) == 0:
      uattack.extend([target._id, card._id])
   else:
      uattack.append(card._id)
   setGlobalVar('UnitedAttack', uattack)
   debug("UnitedAttack: {}".format(uattack))
   
   return target


def blockAuto(card):
   debug(">>> blockAuto()") #Debug
   
   # Check if the card can be legally played
   if me.isActivePlayer or getGlobalVar('PhaseIdx', players[1]) != BlockPhase:
      information("You can only counter-attack in enemy's Counter-attack Phase.")
      return      
   # Only for character cards...
   if card.Type != 'Character':
      information("You can only counter-attack with character cards.")
      return
   # ... in player's ring
   slotIdx = getSlotIdx(card)
   myRing = getGlobalVar('Ring', me)
   if slotIdx == -1 or myRing[slotIdx] != card._id:
      warning("Please counter-attack with a character in your ring.")
      return
   # Frozen char?
   if card.orientation & Rot90 == Rot90:
      warning("Frozen characters can't counter-attack.")
      return
   # Cancels the character's counter-attack if it's already blocking
   if MarkersDict['CounterAttack'] in card.markers:
      removeMarker(card, 'CounterAttack')
      clear(card, silent = True)
      alignCard(card)
      notify('{} cancels the counter-attack with {}'.format(me, card))  
      return
   # Check if an attacking enemy char has been selected
   enemyRing = getGlobalVar('Ring', players[1])
   targets = getTargetedCards(card, True, False)
   if len(targets) == 0 or not targets[0]._id in enemyRing or not MarkersDict['Attack'] in targets[0].markers:
      warning("Please select an attacking enemy character.\n(Shift key + Left click on a character).")
      return
   target = targets[0]
   # Block the first char in a United Attack
   if MarkersDict['UnitedAttack'] in target.markers:
      warning("Please select the first attacking character of the United Attack.")
      return
   # An attacker can only be blocked by exactly 1 char
   slotIdx = getSlotIdx(target, players[1])
   if slotIdx == -1 or myRing[slotIdx] != None:
      warning("An attacking character can only be blocked by exactly one char")
   
   setMarker(card, 'CounterAttack')
   # card.arrow(target)
   target.target(False)
   coords = CardsCoords['Attack'+`slotIdx`]
   alignCard(card, coords[0], coords[1])
      
   return target
   

def activateAuto(card):
   debug(">>> activateAuto()") #Debug
   
   if card.highlight == ActivatedColor:
      whisper("{}'s ability or effect has already been activated".format(card))
      return   
   # Character ability
   if card.Type == 'Character':
      if MarkersDict['NoAbility'] in card.markers:
         return
      pcard = getParsedCard(card)
      if not pcard.hasEffect():
         return
      debug("Trying to activate {}'s ability {} {}".format(card.Name, pcard.ability_type, pcard.ability_name))
      # Activate [] and /\ only in player's Main Phase
      if pcard.ability_type in [InstantAbility, ActivatedAbility] and (not me.isActivePlayer or getGlobalVar('PhaseIdx', me) != MainPhase):
         information("You can only activate [ ] or /\\ abilities in your Main Phase.")
         return
      # /\ abilities
      if pcard.ability_type == InstantAbility:
         # Activate only once
         if not MarkersDict['JustEntered'] in card.markers:
            warning("/\\ abilities can only be activated once when character just enters the ring.")
            return
      # [] abilities
      if pcard.ability_type == ActivatedAbility:  
         # Just entered?
         if MarkersDict['JustEntered'] in card.markers:
            warning("Can't activate [ ] abilities of characters that just entered the ring.")
            return
         # Frozen or attacking?
         if card.orientation & Rot90 == Rot90 or MarkersDict['Attack'] in card.markers:
            warning("Can't activate [ ] abilities of frozen or attacking characters.")
            return
      # () abilities
      if pcard.ability_type == AutoAbility:
         # Nor in a United Attack
         if MarkersDict['UnitedAttack'] in card.markers:
            warning("Can't activate ( ) abilities of characters which joined a United Attack.")
            return
      
      # Activate [] ability?
      if pcard.ability_type == ActivatedAbility:
         if not confirm("Activate {}'s ability {} {}?".format(card.Name, pcard.ability_type, pcard.ability_name)):
            return
      # Activate the ability
      return pcard.activateEffect()
   # Rest of cards
   else:
      pcard = getParsedCard(card)
      return pcard.activateEffect()
   
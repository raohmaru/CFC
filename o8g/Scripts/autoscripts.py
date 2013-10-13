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

def triggerPhaseEvent(phase = 'Start'): # Function which triggers effects at the start or end of the phase
   debugNotify(">>> triggerPhaseEvent({})".format(phase)) #Debug
   mute()
   if not automations['Phase']: return
   
   if phase == 'Activate':
      # Unfreeze characters in the player's ring, clear colors and remove script markers
      notify("{} unfreezes all characters in their ring.".format(me))
      myCards = (card for card in table
         if card.controller == me
         and card.model != TokensDict['Empty Slot'])
      for card in myCards:
         if not MarkersDict['DoesntUnfreeze'] in card.markers:
            freeze(card, unfreeze = True, silent = True)
         removeMarker(card, 'JustEntered')
         clear(card, silent = True)
   
   if phase == 'Draw':
      if automations['Play']:
         if len(me.Deck) == 0:
            notify("{} has no cards in their deck and therefore can't draw.\n{} wins the game!".format(me,players[1]))
   
   if phase == 'Counterattack':
      if automations['Play']:
         united = [card for card in table
            if card.controller == me
            and MarkersDict['UnitedAttack'] in card.markers]
         payCostSP(-len(united)*UnitedAttackCost, msg = "do a {} United Attack".format('Double' if len(united) == 0 else 'Triple'))
   
   elif phase == 'End':
      myCards = (card for card in table
         if card.controller == me
         and card.model != TokensDict['Empty Slot'])
      for card in myCards:
         if card.Type == 'Character':
            # Clears targets, colors, freeze and resets position
            slotIdx = getSlotIdx(card)
            if slotIdx != -1:
               coords = CardsCoords['Slot'+`slotIdx`]
               alignCard(card, coords[0], coords[1])
            if card.highlight in [AttackColor, UnitedAttackColor, ActivatedColor]:
               freeze(card, unfreeze = False, silent = True)
            # Remove script makers
            removeMarker(card, 'Attack')
            removeMarker(card, 'UnitedAttack')
            removeMarker(card, 'CounterAttack')
         # Discard any Action or Reaction card left in the table (just in case player forgot to remove them)
         elif card.Type == 'Action' or card.Type == 'Reaction':
            discard(card)
      clearAll()


#------------------------------------------------------------------------------
# Play automations
#------------------------------------------------------------------------------

def playAuto(card):
   debugNotify(">>> playAuto()") #Debug
   global charsPlayed
   
   # Player plays a Character card
   if card.Type == 'Character':
      # If a char has been selected, backup that char instead
      targets = [c for c in table
         if c.targetedBy
         and c.controller == me]
      if len(targets) > 0 and targets[0].Type == 'Character':
         backup(card)
         return
      # Check if the card can be legally played
      if not me.isActivePlayer or phaseIdx != 3:
         information("Character cards can only be played on your Main Phase.")
         return
      # Player has any empty slot in his ring?
      myRing = eval(me.getGlobalVariable('Ring'))
      if myRing.count(None) == 0:
         information("You need an emply slot in your ring to play a character card.")
         return
      # Now checks if an Empty Slot token owned by the player has been selected
      target = [c for c in targets
         if c.model == TokensDict['Empty Slot']]
      if len(target) == 0:
         information("Please select an empty slot in your ring to play a character card.\n(Shift key + Left click on an empty slot).")
         return
      # Is really that slot empty?
      slotIdx = getSlotIdx(target[0])
      if slotIdx == -1 or myRing[slotIdx] != None:
         warning("Character card can't be played.\nThe selected slot is not empty (it's taken up by {}).".format(Card(myRing[slotIdx]).Name))
         return
      # Limit of chars played per turn
      if charsPlayed >= CharsPerTurn:
         if not confirm("Only {} character per turn can be played.\nProceed anyway?".format(CharsPerTurn)):
            return
      # Pay SP cost
      if payCostSP(card.SP) == 'ABORT':
         return
      # Finally, the card is played
      placeCard(card, card.Type, 'play', slotIdx)
      card.markers[MarkersDict['HP']] = num(card.BP) / 100
      card.markers[MarkersDict['JustEntered']] = 1
      target[0].target(False)
      myRing[slotIdx] = card._id
      me.setGlobalVariable('Ring', str(myRing))
      charsPlayed += 1
      debugNotify("{}'s ring: {}".format(me, myRing))
   
   # Player plays an Action card
   elif card.Type == 'Action':
      # Check if the card can be legally played
      if not me.isActivePlayer or phaseIdx != 3:
         information("Action cards can only be played on your Main Phase.")
         return
      # Pay SP cost
      if payCostSP(card.SP) == 'ABORT':
         return
      placeCard(card, card.Type, 'play')
   
   # Player plays a Reaction card
   elif card.Type == 'Reaction':
      # Check if the card can be legally played
      if me.isActivePlayer or phaseIdx != 4:
         information("Reaction cards can only be played in enemy's Counter-attack Phase.")
         return
      # Pay SP cost
      if payCostSP(card.SP) == 'ABORT':
         return
      placeCard(card, card.Type, 'play')
   # Player plays an unknow card
   else:
      placeCard(card, card.Type)
      
   return True

def backupAuto(card):
   debugNotify(">>> backupAuto()") #Debug
   global backupsPlayed
   
   # Check if the card can be legally played
   if not me.isActivePlayer or phaseIdx != 3:
      information("Characters can only be backed-up on your Main Phase.")
      return
   # Only for character cards
   if card.Type != 'Character':
      information("You can only backup with Character cards.")
      return
   # Check if a valid char has been selected
   myRing = eval(me.getGlobalVariable('Ring'))
   target = [c for c in table
      if c.targetedBy
      and c.controller == me]
   if len(target) == 0 or target[0].Type != 'Character' or not target[0]._id in myRing:
      information("Please select a character in your ring.\n(Shift key + Left click on a character).")
      return
   target = target[0]
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
   backups = eval(getGlobalVariable('Backups'))
   for id in backups:
      if backups[id] == target._id:
         if Card(id).Subtype == card.Subtype:
            avlbckps -= 1
   if avlbckps <= 0:
      warning("{} can't be backed-up with more than {} {} card(s).".format(target.Name, acceptedBackups.count(card.Subtype), card.Subtype))
      return   
   # It's a legal backup
   attach(card, target)
   placeCard(card, card.Type, 'backup', target)
   card.sendToBack()
   target.markers[MarkersDict['HP']] += BackupRaiseBP  # Backed-up char's BP is raised
   backupsPlayed += 1
   return target

def attackAuto(card):
   debugNotify(">>> attackAuto()") #Debug
   
   # Check if we can attack
   if not me.isActivePlayer or phaseIdx != 3:
      information("You can only attack in your Main Phase.")
      return
   # Only for character cards
   if card.Type != 'Character':
      information("You can only attack with Character cards.")
      return
   # Move the card to the attack position
   slotIdx = getSlotIdx(card)
   myRing = eval(me.getGlobalVariable('Ring'))
   if slotIdx == -1 or myRing[slotIdx] != card._id:
      warning("Please attack with a character in your ring.")
      return
   # Char just entered the ring?
   if MarkersDict['JustEntered'] in card.markers:
      if not confirm("Characters that just entered the ring can't attack this turn.\nProceed anyway?"):
         return
   # Frozen char?
   if card.orientation & Rot90 == Rot90:
      warning("Frozen characters can't attack this turn.")
      return
   # Perform the attack
   card.markers[MarkersDict['Attack']] = 1
   coords = CardsCoords['Attack'+`slotIdx`]
   alignCard(card, coords[0], coords[1])
   
   return True

def unitedAttackAuto(card):
   debugNotify(">>> unitedAttackAuto()") #Debug
   
   # Check if an attacking char has been selected
   myRing = eval(me.getGlobalVariable('Ring'))
   targets = [c for c in table
      if c.targetedBy
      and c.controller == me
      and c.Type == 'Character']
   if len(targets) == 0 or not targets[0]._id in myRing or not MarkersDict['Attack'] in targets[0].markers:
      information("Please select an attacking character in your ring.\n(Shift key + Left click on a character).")
      return
   target = targets[0]   
   # Max chars per United Attack
   united = [c for c in table
      if c.controller == me
      and MarkersDict['UnitedAttack'] in c.markers]
   if len(united) >= MaxUnitedAttack:
      warning("Can't be more than {} charactars in a United Attack.".format(MaxUnitedAttack+1))
      return
   # Cost
   cost = (len(united)+1) * UnitedAttackCost
   if cost > me.SP:
      type = 'Double' if len(united) == 0 else 'Triple'
      if not confirm("You do not seem to have enough SP to do a {} United Attack (it costs {}).\nProceed anyway?".format(type, cost)):
         return
   
   if not attackAuto(card): return
   
   card.markers[MarkersDict['UnitedAttack']] = 1
   card.arrow(target)
   
   return target

def blockAuto(card):
   debugNotify(">>> blockAuto()") #Debug
   
   # Check if the card can be legally played
   if me.isActivePlayer or phaseIdx != 4:
      information("You can only counter-attack in enemy's Counter-attack Phase.")
      return      
   # Only for character cards
   if card.Type != 'Character':
      information("You can only counter-attack with Character cards.")
      return
   # Frozen char?
   if card.orientation & Rot90 == Rot90:
      warning("Frozen characters can't counter-attack.")
      return
   
   card.markers[MarkersDict['CounterAttack']] = 1
   return True
   
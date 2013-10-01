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
      # Unfreeze characters in the player's ring
      myCards = (card for card in table
         if card.controller == me)
      for card in myCards:
         if card.highlight != DoesntUnfreezeColor:
            freeze(card, unfreeze = True, silent = True)
         card.highlight = None
   
   elif phase == 'End':
      myCards = (card for card in table
         if card.controller == me)
      for card in myCards:
         # Clears targets, colors and freeze characters in the player's ring
         if card.highlight == AttackColor or card.highlight == ActivatedColor:
            freeze(card, unfreeze = False, silent = True)
         # Discard any Action or Reaction card left in the table (just in case player forgot to remove them)
         if card.Type == 'Action' or card.Type == 'Reaction':
            discard(card)
      clearAll()


#------------------------------------------------------------------------------
# Play automations
#------------------------------------------------------------------------------

def playAuto(card):
   # Player plays a Character card
   if card.Type == 'Character':
      # Check if the card can be legally played
      if not me.isActivePlayer or phaseIdx != 3:
         information("Character cards can only be played on your Main Phase.")
         return
      # If a char has been selected, backup that char
      targets = [c for c in table
         if c.targetedBy
         and c.controller == me]
      if len(targets) > 0 and targets[0].Type == 'Character':
         backup(card)
         return
      # Player has any empty slot?
      myRing = eval(me.getGlobalVariable('Ring'))
      if myRing.count(None) == 0:
         information("You need an emply slot in your ring to play a character card.")
         return
      # Now checks if an Empty Slot token owned by the player has been selected
      target = [c for c in targets
         if c.model == TokensDict['Empty Slot']]
      if len(target) == 0:
         information("Please select an empty slot in your ring to play a character card (Shift key + Left click).")
         return
      # Is really the slot empty?
      slotNum = slots.get(target[0]._id, 0)
      if myRing[slotNum] != None:
         information("Character card can't be played. The selected slot is not empty (it's taken up by {}).".format(Card(myRing[slotNum]).Name))
         return
      # Pay SP cost
      if payCostSP(card.SP) == 'ABORT':
         return
      # Finally, the card is played
      placeCard(card, card.Type, 'play', slotNum)
      card.markers[MarkersDict['HP']] = num(card.BP) / 100
      target[0].target(False)
      myRing[slotNum] = card._id
      me.setGlobalVariable('Ring', str(myRing))
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
         information("Reaction cards can only be played on enemy's Counter-attack Phase.")
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
   
   # Only for character cards
   if card.Type != 'Character':
      information("You can only backup with Character cards.")
      return
   # Check if the card can be legally played
   if not me.isActivePlayer or phaseIdx != 3:
      information("Characters can only be backed-up on your Main Phase.")
      return
   # Check if a valid char has been selected
   myRing = eval(me.getGlobalVariable('Ring'))
   target = [c for c in table
      if c.targetedBy
      and c.controller == me]
   if len(target) == 0 or target[0].Type != 'Character' or not target[0]._id in myRing:
      information("Please select a character in your ring (Shift key + Left click).")
      return
   # Check compatible backups
   target = target[0]
   acceptedBackups = (target.properties['Backup 1'], target.properties['Backup 2'], target.properties['Backup 3'])
   if not card.Subtype in acceptedBackups:
      information("Incompatible backups.\n{} only accepts {}.".format(target.Name, acceptedBackups))
      return
   # Check remaining backups
   avlbckps = acceptedBackups.count(card.Subtype)
   debugNotify("avlbckps: {}".format(avlbckps))
   debugNotify("BACKUPS:")
   backups = eval(getGlobalVariable('Backups'))
   for id in backups:
      if backups[id] == target._id:
         if Card(id).Subtype == card.Subtype:
            avlbckps -= 1
   debugNotify("avlbckps: {}".format(avlbckps))
   if avlbckps <= 0:
      information("{} can't be backed-up with more than {} {} card(s).".format(target.Name, acceptedBackups.count(card.Subtype), card.Subtype))
      return   
   # It's a legal backup
   attach(card, target)
   placeCard(card, card.Type, 'backup', target)
   card.sendToBack()
   target.markers[MarkersDict['HP']] += BackupRaiseBP  # Backed-up char's BP is raised
   return target
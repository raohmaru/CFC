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
      # Clears targets, colors and freeze characters in the player's ring
      myCards = (card for card in table
         if card.controller == me)
      for card in myCards:
         if card.highlight == AttackColor or card.highlight == ActivatedColor:
            freeze(card, unfreeze = False, silent = True)
      clearAll()
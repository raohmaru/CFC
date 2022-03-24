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
# Card automations
#---------------------------------------------------------------------------

def createGameCard(card, ruleId = None, init = True, dryRun = False, forceActivateAuto = False):
   """
   Wrapper for a Card object. Should only be called for cards just added to the table or when its effect changes.
   """
   if not card._id in gameCards or dryRun:
      debug(">>> createGameCard({}, {}, {}, {}, {})", card, ruleId, init, dryRun, forceActivateAuto)
      if isCharacter(card):
         gc = CharCard(card, ruleId)
      else:
         gc = GameCard(card, ruleId)
      if not dryRun:
         gameCards[card._id] = gc
      if init:
         gc.init(forceActivateAuto)
      if dryRun:
         return gc
   else:
      debug("GameCard for {} already exists", card)
   return gameCards.get(card._id)
   

def getGameCard(card):
   debug(">>> Retrieve GameCard for ID {} ({})", card._id, card)
   ruleId = None
   if card.controller != me:
      CharsAbilities = getGlobalVar('CharsAbilities')
      if card._id in CharsAbilities:
         ruleId = CharsAbilities[card._id]
      pcard = gameCards.get(card._id)
      # If the rule of the card has changed, re-create it
      if pcard and ruleId and pcard.rule_id != ruleId:
         debug("Updating GameCard")
         deleteGameCard(card)
   return createGameCard(card, ruleId, False)
   

def deleteGameCard(card):
   debug(">>> Remove GameCard for ID {} ({})", card._id, card)
   if card.controller == me:
      removeGameEventListener(card._id)
   gc = gameCards.pop(card._id, None)
   if gc:
      gc.destroy()
      del gc

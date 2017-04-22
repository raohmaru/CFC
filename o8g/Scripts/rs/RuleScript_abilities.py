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

#---------------------------------------------------------------------------
# Abilities class
#---------------------------------------------------------------------------

class RulesAbilities():
   """ Class to handle card's abilities """
   items = {}

   @staticmethod
   def register(name, func):
      RulesAbilities.items[name] = func
      
   
   @staticmethod   
   def add(abilites, card_id):
      for ability in abilites:
         if ability in RulesAbilities.items:
            debug("-- adding ability '%s' from %s" % (ability, Card(card_id)))
            # func = RulesAbilities.items[ability]
            func = eval(RulesAbilities.items[ability])  # eval is a necessary evil...
            func(card_id)
         else:
            debug("-- ability not found: {}".format(ability))
      

#---------------------------------------------------------------------------
# Abilities functions
#---------------------------------------------------------------------------

def ablUnblockable(card_id):
   debug(">>> ablUnblockable({})".format(card_id)) #Debug
   addGameEventListener(GameEvents.Blocked, 'ablUnblockable_listener', card_id, card_id)
   
def ablUnblockable_listener(card1_id, card2_id):
   """ Checks if the original card with the ability is equal to the second card the system wants to check """
   debug(">>> ablUnblockable_listener({}, {})".format(card1_id, card2_id)) #Debug      
   if card1_id == card2_id:
      card = Card(card1_id)
      warning("{} cannot be counter-attacked due to {}'s {} ability.".format(card.Name, card.Name, card.properties['Ability Name']))  
      return True
   return False


RulesAbilities.register('unblockable', 'ablUnblockable')
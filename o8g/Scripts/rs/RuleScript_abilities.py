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
   def register(name, func, events):
      RulesAbilities.items[name] = {
         'func': func,
         'events': events
      }
      
   
   @staticmethod   
   def addAll(abilites, card_id):
      for ability in abilites:
         RulesAbilities.add(ability, card_id)
   
   @staticmethod   
   def add(ability, card_id):
      if ability in RulesAbilities.items:
         debug("-- adding ability '{}' from {}".format(ability, Card(card_id)))
         # func = RulesAbilities.items[ability]['func']
         func = eval(RulesAbilities.items[ability]['func'])  # eval is a necessary evil...
         func(card_id)
      else:
         debug("-- ability not found: {}".format(ability))
      
   
   @staticmethod   
   def remove(ability, card_id):
      debug("-- removing ability '{}' from {}".format(ability, Card(card_id)))
      if ability in RulesAbilities.items:
         for event in RulesAbilities.items[ability]['events']:      
            removeGameEventListener(card_id, event)
      

#---------------------------------------------------------------------------
# Abilities functions
#---------------------------------------------------------------------------

def ablUnblockable(card_id):
   debug(">>> ablUnblockable({})".format(card_id)) #Debug
   addGameEventListener(GameEvents.Blocked, 'ablUnblockable_listener', card_id, card_id)
   
def ablUnblockable_listener(target_id, source_id):
   """ Checks if the original card with the ability is equal to the second card the system wants to check """
   debug(">>> ablUnblockable_listener({}, {})".format(target_id, source_id)) #Debug      
   if target_id == source_id:
      card = Card(target_id)
      warning("{} cannot be counter-attacked due to {}'s {} ability.".format(card.Name, card.Name, card.properties['Ability Name']))  
      return True
   return False


RulesAbilities.register('unblockable', 'ablUnblockable', [GameEvents.Blocked])
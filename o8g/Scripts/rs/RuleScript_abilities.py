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
   def add(ability, card_id, source_id=None, restr=None):
      if ability in RulesAbilities.items:
         debug("-- adding ability '{}' to {}".format(ability, Card(card_id)))
         func = RulesAbilities.items[ability]['func']
         # func = eval(RulesAbilities.items[ability]['func'])  # eval is a necessary evil...
         func(card_id, source_id, restr)
      else:
         debug("-- ability not found: {}".format(ability))
      
   
   @staticmethod   
   def remove(ability, card_id):
      card = Card(card_id)
      debug("-- removing ability '{}' from {}".format(ability, card))
      if ability in RulesAbilities.items:
         for event in RulesAbilities.items[ability]['events']:      
            if removeGameEventListener(card_id, event):
               notify("{} has lost the {} ability".format(card, ability))
      

#---------------------------------------------------------------------------
# Abilities functions
#---------------------------------------------------------------------------

def abl_unblockable(card_id, source_id=None, restr=None):
   debug(">>> abl_unblockable({}, {})".format(card_id, source_id)) #Debug
   if addGameEventListener(GameEvents.Blocked, 'abl_genericListener', card_id, source_id, restr, card_id, source_id, MSG_UNBLOCKABLE):
      notify("{} is unblockable".format(Card(card_id)))


def abl_cantBlock(card_id, source_id=None, restr=None):
   debug(">>> abl_cantBlock({}, {})".format(card_id, source_id)) #Debug
   addGameEventListener(GameEvents.BeforeBlock, 'abl_genericListener', card_id, source_id, restr, card_id, source_id, MSG_CANT_BLOCK)
   notify("{} cannot counter-attack".format(Card(card_id)))


def abl_genericListener(target_id, card_id, source_id=None, msg=None):
   """ Checks if the original card with the ability is equal to the second card the system wants to check """
   debug(">>> abl_genericListener({}, {}, {})".format(target_id, card_id, source_id)) #Debug      
   if target_id == card_id:
      card = Card(target_id)
      source = card
      if source_id is not None:
         source = Card(source_id)
      if msg is not None:
         warning(msg.format(card.Name, source.Name, source.properties['Ability Name']))
      return True
   return False


RulesAbilities.register('unblockable', abl_unblockable, [GameEvents.Blocked])
RulesAbilities.register('cantblock',   abl_cantBlock,   [GameEvents.BeforeBlock])
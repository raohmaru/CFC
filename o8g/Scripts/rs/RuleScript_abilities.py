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
   def add(abilityName, target_id, source_id=None, restr=None):
      if abilityName in RulesAbilities.items:
         ability = RulesAbilities.items[abilityName]
         obj = getPlayerOrCard(target_id)
         debug("-- adding ability '{}' to {}".format(abilityName, obj))
         func = ability['func']
         func(target_id, source_id, restr, ability['events'])
      else:
         debug("-- ability not found: {}".format(abilityName))
   
   
   @staticmethod   
   def remove(ability, card_id):
      card = Card(card_id)
      debug("-- removing ability '{}' from {}".format(ability, card))
      if ability in RulesAbilities.items:
         for event in RulesAbilities.items[ability]['events']:      
            if removeGameEventListener(card_id, event):
               notify("{} has lost the {} ability".format(card, ability))
      
      
#---------------------------------------------------------------------------
# Related functions
#---------------------------------------------------------------------------
               
def getPlayerOrCard(id):
   if id in [p._id for p in players]:
      return Player(id)
   else:
      return Card(id)
      
      
def getObjName(obj):
   if isinstance(obj, (int, long)):
      obj = getPlayerOrCard(obj)
   if hasattr(obj, 'Name'):
      return obj.Name
   else:
      return obj.name
      
      
def getTextualRestr(restr):
   if restr[1] in RS_KW_RESTR_LABELS:
      player = ''
      if restr[0]:
         player = 'his  '
      return RS_KW_RESTR_LABELS[restr[1]].format(player)
   return restr(1)
      

#---------------------------------------------------------------------------
# Abilities functions
#---------------------------------------------------------------------------

def abl_unblockable(card_id, source_id=None, restr=None, events=[]):
   debug(">>> abl_unblockable({}, {})".format(card_id, source_id)) #Debug
   if addGameEventListener(events[0], 'abl_genericListener', card_id, source_id, restr, [card_id, source_id, [MSG_UNBLOCKABLE, MSG_BLOCKABLE]]):
      notify("{} is unblockable {}".format(Card(card_id), getTextualRestr(restr)))


def abl_cantBlock(card_id, source_id=None, restr=None, events=[]):
   debug(">>> abl_cantBlock({}, {})".format(card_id, source_id)) #Debug
   if addGameEventListener(events[0], 'abl_genericListener', card_id, source_id, restr, [card_id, source_id, [MSG_CANT_BLOCK, MSG_CAN_BLOCK]]):
      notify("{} cannot counter-attack {}".format(Card(card_id), getTextualRestr(restr)))


def abl_cantPlayAC(player_id, source_id=None, restr=None, events=[]):
   debug(">>> abl_cantPlayAC({}, {})".format(player_id, source_id)) #Debug
   if addGameEventListener(events[0], 'abl_genericListener', player_id, source_id, restr, [player_id, source_id, [MSG_CANT_PLAY_AC, MSG_CAN_PLAY_AC]]):
      notify("{} cannot play action cards {}".format(Player(player_id), getTextualRestr(restr)))


def abl_genericListener(target_id, obj_id, source_id=None, msg=None):
   """ Checks if the original card with the ability is equal to the second card the system wants to check """
   debug(">>> abl_genericListener({}, {}, {})".format(target_id, obj_id, source_id)) #Debug      
   if target_id == obj_id:
      obj = getPlayerOrCard(target_id)
      source = obj
      if source_id is not None:
         source = Card(source_id)
      if msg is not None:
         warning(msg[0].format(getObjName(obj), source.Name, source.properties['Ability Name']))
      return True
   return False


RulesAbilities.register('unblockable', abl_unblockable, [GameEvents.Blocked])
RulesAbilities.register('cantblock',   abl_cantBlock,   [GameEvents.BeforeBlock])
RulesAbilities.register('cantplayac',  abl_cantPlayAC,  [GameEvents.BeforePlayAC])
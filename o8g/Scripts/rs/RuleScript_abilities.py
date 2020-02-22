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
   def register(name, events, checkFunc=None):
      msg = MSG_ABILITIES[name] if name in MSG_ABILITIES else None
      RulesAbilities.items[name] = {
         'events': events,
         'msg': msg,
         'checkFunc' : checkFunc
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
         abl_add(target_id, source_id, restr, ability['events'], ability['msg'], ability['checkFunc'])
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
   debug(">>> getTextualRestr({})".format(restr)) #Debug
   if not restr:
      return ''
   if restr[1] in RS_KW_RESTR_LABELS:
      player = ''
      if restr[0]:
         player = 'his  '
      return ' ' + RS_KW_RESTR_LABELS[restr[1]].format(player)
   return restr(1)
   
   
def notifyAbilityEnabled(target_id, source_id=None, msg=None, restr=None, isWarning=False):
   obj = getPlayerOrCard(target_id)
   source = obj
   if source_id is not None:
      source = Card(source_id)
   if msg is not None:
      func = warning if isWarning else notify
      name = obj
      if isPlayer(obj) or isWarning:
         name = getObjName(obj)
      func(msg[0].format(name, source.Name, source.properties['Ability Name'], restr))

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


def abl_cantPlayRE(player_id, source_id=None, restr=None, events=[]):
   debug(">>> abl_cantPlayRE({}, {})".format(player_id, source_id)) #Debug
   if addGameEventListener(events[0], 'abl_genericListener', player_id, source_id, restr, [player_id, source_id, [MSG_CANT_PLAY_RE, MSG_CAN_PLAY_RE]]):
      notify("{} cannot play reaction cards {}".format(Player(player_id), getTextualRestr(restr)))
      
      
def abl_unlimitedBackup(obj_id):
   return True


def abl_add(obj_id, source_id=None, restr=None, events=[], msg=None, checkFunc=None):
   debug(">>> abl_add({}, {}, {})".format(obj_id, source_id, events)) #Debug
   if addGameEventListener(events[0], 'abl_genericListener', obj_id, source_id, restr, [obj_id, source_id, msg, checkFunc]):
      notifyAbilityEnabled(obj_id, source_id, msg, getTextualRestr(restr))


def abl_genericListener(target_id, obj_id, source_id=None, msg=None, checkFunc=None):
   """ Checks if the original card with the ability is equal to the second card the system wants to check """
   debug(">>> abl_genericListener({}, {}, {}, {}, {})".format(target_id, obj_id, source_id, msg, checkFunc)) #Debug      
   if target_id == obj_id:
      if checkFunc is None:
         notifyAbilityEnabled(target_id, source_id, msg, isWarning=True)
         return True
      else:
         checkFunc = eval(checkFunc)
         return checkFunc(target_id)
   return False


RulesAbilities.register('unblockable',     [GameEvents.Block])
RulesAbilities.register('cantblock',       [GameEvents.BeforeBlock])
RulesAbilities.register('cantplayac',      [GameEvents.BeforePlayAC])
RulesAbilities.register('cantplayre',      [GameEvents.BeforePlayRE])
RulesAbilities.register('unlimitedbackup', [GameEvents.BackupLimit], 'abl_unlimitedBackup')
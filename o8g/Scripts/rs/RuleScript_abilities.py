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
   def register(name, event, checkFunc=None):
      msg = MSG_ABILITIES[name] if name in MSG_ABILITIES else None
      RulesAbilities.items[name] = {
         'event': event,
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
         abl_add(target_id, ability['event'], source_id, restr, ability['msg'], ability['checkFunc'])
      else:
         debug("-- ability not found: {}".format(abilityName))
   
   
   @staticmethod   
   def remove(ability, card_id):
      card = Card(card_id)
      debug("-- removing ability '{}' from {}".format(ability, card))
      if ability in RulesAbilities.items:
         if removeGameEventListener(card_id, RulesAbilities.items[ability]['event']):
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
      
      
def getTextualRestr(restr, player = None):
   if not restr:
      return ''
   if restr[1] in RS_KW_RESTR_LABELS:
      if not player:
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
      func(msg.format(name, source.Name, source.properties['Ability Name'], restr))

#---------------------------------------------------------------------------
# Abilities functions
#---------------------------------------------------------------------------

def callback_true(obj_id):
   return True
   
   
def abl_unfreezable(obj_id):
   setMarker(Card(obj_id), 'Unfreezable')
   return True
   
   
def abl_pierce(obj_id):
   setMarker(Card(obj_id), 'Pierce')
   return True
   
   
def abl_frosted(obj_id):
   card = Card(obj_id)
   if not hasMarker(card, 'Cannot Unfreeze'):
      doesNotUnfreeze(card)
   
   
def abl_removeFrost(obj_id):
   card = Card(obj_id)
   if hasMarker(card, 'Cannot Unfreeze'):
      doesNotUnfreeze(card)
   return True


def abl_add(obj_id, eventOrFunc, source_id=None, restr=None, msg=None, checkFunc=None):
   debug(">>> abl_add({}, {}, {}, {}, {}, {})".format(obj_id, eventOrFunc, source_id, restr, msg, checkFunc)) #Debug
   addEvent = True
   
   if restr and msg and len(msg) > 1:
      restr = list(restr) + [msg[1]]
      
   if callable(eventOrFunc):
      eventOrFunc(obj_id)
      eventOrFunc = Hooks.CallOnRemove
      addEvent = bool(restr)
      
   if addEvent:
      addGameEventListener(eventOrFunc, 'abl_genericListener', obj_id, source_id, restr, [obj_id, source_id, msg, checkFunc])
   if msg and source_id:
      notifyAbilityEnabled(obj_id, source_id, msg[0], getTextualRestr(restr))


def abl_genericListener(target_id, obj_id, source_id=None, msgOrFunc=None, checkFunc=None):
   """ Checks if the original card with the ability is equal to the second card the system wants to check """
   debug(">>> abl_genericListener({}, {}, {}, {}, {})".format(target_id, obj_id, source_id, msgOrFunc, checkFunc))
   callFunc = False
   if checkFunc is None and isinstance(msgOrFunc, basestring):
      checkFunc = msgOrFunc
      callFunc = True
   if target_id == obj_id or callFunc:
      debug("Invoking ability callback")
      if checkFunc is None:
         notifyAbilityEnabled(target_id, source_id, msgOrFunc[0], isWarning=(len(msgOrFunc) > 1))
         return True
      else:
         checkFunc = eval(checkFunc)
         return checkFunc(target_id)
   return False


RulesAbilities.register('unblockable',     Hooks.CanBeBlocked)
RulesAbilities.register('cantblock',       Hooks.BeforeBlock)
RulesAbilities.register('cantplayac',      Hooks.BeforePlayAC)
RulesAbilities.register('cantplayre',      Hooks.BeforePlayRE)
RulesAbilities.register('preventpierce',   Hooks.PreventPierce)
RulesAbilities.register('rush',            Hooks.PlayFresh)
RulesAbilities.register('unlimitedbackup', Hooks.BackupLimit,  'callback_true')
RulesAbilities.register('pierce',          GameEvents.Blocked, 'abl_pierce')
RulesAbilities.register('unfreezable',     GameEvents.Attacks, 'abl_unfreezable')
RulesAbilities.register('frosted',         abl_frosted,        'abl_removeFrost')
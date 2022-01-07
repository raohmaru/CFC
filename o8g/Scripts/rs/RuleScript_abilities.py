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
# Abilities class
#---------------------------------------------------------------------------

class RulesAbilities():
   """ Class to handle card's abilities """
   items = {}

   @staticmethod
   def register(name, event, checkFunc = None, onAdded = None, onRemoved = "abl_removed"):
      msg = MSG_AB[name] if name in MSG_AB else None
      RulesAbilities.items[name] = {
         'event'    : event,
         'msg'      : msg,
         'checkFunc': checkFunc,
         'onAdded'  : onAdded,
         'onRemoved': onRemoved
      }
      
   
   @staticmethod   
   def addAll(abilites, card_id):
      for ability in abilites:
         RulesAbilities.add(ability, card_id)
   
   
   @staticmethod   
   def add(abilityName, target_id, source_id = None, restr = None):
      if abilityName in RulesAbilities.items:
         ability = RulesAbilities.items[abilityName]
         obj = getPlayerOrCard(target_id)
         debug("-- adding ability '{}' to {}".format(abilityName, obj))
         abl_add(ability, target_id, source_id, restr)
         if ability['onAdded']:
            ability['onAdded'](obj, restr)
      else:
         debug("-- ability not found: {}".format(abilityName))
   
   
   @staticmethod   
   def remove(ability, card_id):
      card = Card(card_id)
      debug("-- removing ability '{}' from {}".format(ability, card))
      if ability in RulesAbilities.items:
         if removeGameEventListener(card_id, RulesAbilities.items[ability]['event'], 'abl_genericListener'):
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
   if not restr:
      return ''
   if restr[1] in RS_KW_RESTR_LABELS:
      player = me
      if restr[0] == RS_PREFIX_OPP:
         player = getOpp()
      return ' ' + RS_KW_RESTR_LABELS[restr[1]].format(player)
   return restr(1)
   
   
def notifyAbility(target_id, source_id = None, msg = None, restr = '', isWarning = False):
   obj = getPlayerOrCard(target_id)
   source = obj
   if source_id is not None:
      source = Card(source_id)
   if msg is not None:
      func = warning if isWarning else notify
      name = obj
      if isPlayer(obj) or isWarning:
         if isPlayer(obj) and isWarning:
            name = 'You'
         else:
            name = getObjName(obj)
      func(msg.format(name, source.Name, source.properties['Ability Name'], restr))


#---------------------------------------------------------------------------
# Abilities functions
#---------------------------------------------------------------------------

def abl_add(abl, obj_id, source_id = None, restr = None):
   event = abl['event']
   msg = abl['msg']
   checkFunc = abl['checkFunc']
   onRemove = abl['onRemoved']
   debug(">>> abl_add({}, {}, {}, {}, {}, {}, {})".format(obj_id, event, source_id, restr, msg, checkFunc, onRemove))
      
   eventAdded = addGameEventListener(event, 'abl_genericListener', obj_id, source_id, restr, [obj_id, source_id, msg, checkFunc, restr], onRemove = onRemove)
   if eventAdded and msg:
      notifyAbility(obj_id, source_id if source_id else obj_id, msg[0], getTextualRestr(restr))


def abl_genericListener(target_id, obj_id, source_id = None, msgOrFunc = None, checkFunc = None, restr = None):
   """ Checks if the original card with the ability is equal to the second card the system wants to check """
   debug(">>> abl_genericListener({}, {}, {}, {}, {})".format(target_id, obj_id, source_id, msgOrFunc, checkFunc))
   callFunc = False
   if checkFunc is None and isinstance(msgOrFunc, basestring):
      checkFunc = msgOrFunc
      callFunc = True
   if target_id == obj_id or callFunc:
      if checkFunc is None:
         debug("Ability callback: False")
         return False
      else:
         debug("Invoking ability callback: {}".format(checkFunc))
         checkFunc = eval(checkFunc)
         return checkFunc(target_id)
   return True


def callback_false(obj_id):
   return False
   
   
def abl_unfreezable(obj_id):
   setMarker(Card(obj_id), 'Unfreezable')
   return False
   
   
def abl_pierce(obj_id):
   setMarker(Card(obj_id), 'Pierce')
   return False
   
   
def abl_frosted_added(card, restr = None):
   if not hasMarker(card, 'Cannot Unfreeze'):
      doesNotUnfreeze(card, restr)
   
   
def abl_removeFrost(obj_id):
   card = Card(obj_id)
   if hasMarker(card, 'Cannot Unfreeze'):
      doesNotUnfreeze(card)
   return False


def abl_cantattack_added(card, restr = None):
   if isAttacking(card):
      cancelAttack(card)


def abl_cantblock_added(card, restr = None):
   setMarker(card, 'Cannot Block')
   if isBlocking(card):
      cancelBlock(card)


def abl_cantblock_removed(obj_id, source_id, msg, checkFunc, restr = None):
   removeMarker(Card(obj_id), 'Cannot Block')
   # It's mandatory to call this function
   abl_removed(obj_id, source_id, msg, checkFunc, restr)


def abl_rush_added(card, restr = None):
   if hasMarker(card, 'Just Entered'):
      removeMarker(card, 'Just Entered')
      

def abl_removed(obj_id, source_id, msg, checkFunc, restr = None):
   """
   On removed ability callback function.
   """
   # If msg has 2 items it means that it is a on/off message.
   # Then we want to show the message when the effect is gone because of the restr cleanup.
   if restr and msg and len(msg) == 2:
      notify(msg[1].format(getObjName(obj_id)))


RulesAbilities.register('unblockable',     Hooks.CanBeBlocked)
RulesAbilities.register('cantattack',      Hooks.BeforeAttack, onAdded = abl_cantattack_added)
RulesAbilities.register('cantblock',       Hooks.BeforeBlock, onAdded = abl_cantblock_added, onRemoved = 'abl_cantblock_removed')
RulesAbilities.register('cantplayac',      Hooks.BeforePlayAC)
RulesAbilities.register('cantplayre',      Hooks.BeforePlayRE)
RulesAbilities.register('preventpierce',   Hooks.PreventPierce)
RulesAbilities.register('rush',            Hooks.PlayAsFresh, onAdded = abl_rush_added)
RulesAbilities.register('unlimitedbackup', Hooks.BackupLimit,  'callback_false')
RulesAbilities.register('pierce',          GameEvents.Blocked, 'abl_pierce')
RulesAbilities.register('unfreezable',     GameEvents.Attacks, 'abl_unfreezable')
RulesAbilities.register('frosted',         Hooks.CallOnRemove, 'abl_removeFrost', abl_frosted_added)
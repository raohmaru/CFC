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
   """
   Class to handle card"s abilities.
   """
   items = {}

   @staticmethod
   def register(name, event, eventCallback = None, onAdded = None, onRemoved = "abl_removed"):
      msg = MSG_AB[name] if name in MSG_AB else None
      RulesAbilities.items[name] = {
         "event"        : event,
         "msg"          : msg,
         "eventCallback": eventCallback,
         "onAdded"      : onAdded,
         "onRemoved"    : onRemoved
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
         debug("-- adding ability '{}' to {}", abilityName, obj)
         abl_add(ability, target_id, source_id, restr)
         if ability["onAdded"]:
            debug("-- calling onAdded callback {}", ability["onAdded"].func_name)
            ability["onAdded"](obj, restr)
      else:
         debug("-- ability not found: {}", abilityName)
   
   
   @staticmethod   
   def remove(ability, card_id):
      card = Card(card_id)
      debug("-- removing ability '{}' from {}", ability, card)
      if removeGameEventListener(card_id, RulesAbilities.items[ability]["event"], "abl_genericListener"):
         notify("{} has lost the {} ability".format(card, ability))
      

#---------------------------------------------------------------------------
# Abilities functions
#---------------------------------------------------------------------------

def abl_add(abl, obj_id, source_id = None, restr = None):
   event = abl["event"]
   msg = abl["msg"]
   eventCallback = abl["eventCallback"]
   onRemove = abl["onRemoved"]
   debug(">>> abl_add({}, {}, {}, {}, {}, {}, {})", obj_id, event, source_id, restr, msg, eventCallback, onRemove)
   eventAdded = addGameEventListener(event, "abl_genericListener", obj_id, source_id, restr, args = [obj_id, source_id, msg, eventCallback, restr], onRemove = onRemove)
   if eventAdded and msg:
      notifyAbility(obj_id, source_id if source_id else obj_id, msg[0], getTextualRestr(restr))


def abl_genericListener(target_id, source_id, msgOrFunc = None, eventCallback = None, restr = None, eventTarget_id = None):
   """
   Listener executed after the event defined in the ability has triggered.
   Returns bool used by triggerHook() to continue or cancel an action.
   """
   debug(">>> abl_genericListener({}, {}, {}, {}, {})", target_id, source_id, msgOrFunc, eventCallback, eventTarget_id)
   if eventCallback is None and isinstance(msgOrFunc, basestring):
      eventCallback = msgOrFunc
   # Checks that the target of the event and the target of the ability are the same
   if target_id == eventTarget_id or eventCallback is not None:
      if eventCallback is None:
         debug("Ability callback -> False")
         return False
      else:
         res = eval(eventCallback)(target_id)
         debug("Ability callback {}({}) -> {}", eventCallback, target_id, res)
         return res
   return True


# Event callbacks ----------------------------------------------------------

def abl_callbackFalse(obj_id):
   return False


def abl_callbackTrue(obj_id):
   return True
   
   
def abl_unfreezable(obj_id):
   setMarker(Card(obj_id), "Unfreezable")
   return False  # Mandatory
   
   
def abl_pierce(obj_id):
   setMarker(Card(obj_id), "Pierce")
   return False  # Mandatory
   
   
def abl_removeFrost(obj_id):
   card = Card(obj_id)
   if hasMarker(card, "Cannot Unfreeze"):
      doesNotUnfreeze(card)
   return False  # Mandatory
   
   
def abl_cantattack(obj_id):
   pcard = getGameCard(Card(obj_id))
   # Disable ability if joining a UA
   return pcard.getState("joiningUA") == True
   

# On ability added callbacks -----------------------------------------------

def abl_frosted_added(card, restr = None):
   if not hasMarker(card, "Cannot Unfreeze"):
      doesNotUnfreeze(card, restr)


def abl_cantattack_added(card, restr = None):
   setMarker(card, "Cannot Attack")
   if isAttacking(card):
      cancelAttack(card)


def abl_cantblock_added(card, restr = None):
   setMarker(card, "Cannot Block")
   if isBlocking(card):
      cancelBlock(card)


def abl_rush_added(card, restr = None):
   if hasMarker(card, "Just Entered"):
      removeMarker(card, "Just Entered")
      

# On ability removed callbacks ---------------------------------------------

def abl_removed(obj_id, source_id, msg, eventCallback, restr = None):
   """
   On removed ability callback function.
   """
   # If msg has 2 items it means that it is a on/off message (see MSG_AB).
   # Then we want to show the message when the effect is gone because of the restr cleanup.
   if restr and msg and len(msg) == 2:
      notify(msg[1].format(getObjName(obj_id)))


def abl_cantblock_removed(obj_id, source_id, msg, eventCallback, restr = None):
   removeMarker(Card(obj_id), "Cannot Block")
   # It's mandatory to call this function
   abl_removed(obj_id, source_id, msg, eventCallback, restr)


def abl_cantattack_removed(obj_id, source_id, msg, eventCallback, restr = None):
   removeMarker(Card(obj_id), "Cannot Attack")
   # It's mandatory to call this function
   abl_removed(obj_id, source_id, msg, eventCallback, restr)


# Register abilities -------------------------------------------------------
#                       name,              event,               eventCallback,    onAdded,              onRemoved
RulesAbilities.register("unblockable",     Hooks.CanBeBlocked)
RulesAbilities.register("cantattack",      Hooks.BeforeAttack,  "abl_cantattack", abl_cantattack_added, "abl_cantattack_removed")
RulesAbilities.register("cantblock",       Hooks.BeforeBlock,   onAdded = abl_cantblock_added, onRemoved = "abl_cantblock_removed")
RulesAbilities.register("cantplayac",      Hooks.BeforePlayAC)
RulesAbilities.register("cantplayre",      Hooks.BeforePlayRE)
RulesAbilities.register("preventpierce",   Hooks.PreventPierce, "abl_callbackTrue")
RulesAbilities.register("rush",            Hooks.PlayAsFresh,   onAdded = abl_rush_added)
RulesAbilities.register("unlimitedbackup", Hooks.BackupLimit,   "abl_callbackFalse")
RulesAbilities.register("pierce",          GameEvents.Blocked,  "abl_pierce")
RulesAbilities.register("unfreezable",     GameEvents.Attacks,  "abl_unfreezable")
RulesAbilities.register("frosted",         Hooks.CallOnRemove,  "abl_removeFrost", abl_frosted_added)
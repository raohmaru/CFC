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
# Event system
#---------------------------------------------------------------------------

def addGameEventListener(event, callback, obj_id, source_id = None, restr = None, args = [], appliesto = None, onRemove = None):
   """
   Subscribes to a global event for the given card (obj_id).
   """
   GameEvents = getGlobalVar('GameEvents')
   prfx, eventName = RulesLexer.getPrefix(RS_PREFIX_EVENTS, event)
   # Do not add the same event again
   for e in GameEvents:
      if (
             e['event']    == eventName
         and e['id']       == obj_id
         and e['callback'] == callback
         and e['restr']    == restr
         and e['scope']    == prfx
         and e['args']     == args
      ):
         return False
   controller = Card(source_id).controller._id if source_id else me._id
   listener = {
      'event'     : eventName,
      'controller': controller,
      'id'        : obj_id,
      'source'    : source_id,
      'callback'  : callback,
      'restr'     : restr,
      'scope'     : prfx,
      'args'      : args,
      'appliesto' : appliesto,
      'onremove'  : onRemove
   }
   GameEvents.append(listener)
   setGlobalVar('GameEvents', GameEvents)
   debug("Added listener to game event '{}' -> {}", eventName, listener)
   return True


def removeGameEventListener(obj_id, eventName = None, callback = None):
   """
   Unsubscribes the given card (obj_id) from a global event. If the additional arguments are not defined
   it will remove all listeners the card was subscribed to.
   """
   debug(">>> removeGameEventListener({}, {}, {})", obj_id, eventName, callback)
   GameEvents = getGlobalVar('GameEvents')
   removed = False
   # Iterate it in reverse order because we are removing items
   for i, listener in reversed(list(enumerate(GameEvents))):
      if not eventName or eventName == listener['event']:
         if(
            (listener['id'] == obj_id or listener['source'] == obj_id) and
            (not callback or callback == listener['callback'])
         ):
            # Events with restrictions will be removed eventually in cleanupGameEvents()
            if listener['restr'] is None:
               del GameEvents[i]
               removed = True
               debug("Removed listener for event {} ({})", listener['event'], listener)
               # Invoke any callback
               onRemoveEvent(listener)
   if removed:
      setGlobalVar('GameEvents', GameEvents)
   return removed


def dispatchEvent(event, obj_id = None, args = []):
   """
   Sends a global event and executes the callbacks of all the listeners subscribed to the given event.
   """
   res = (None, None)
   if not settings['PlayAuto']:
      return res
   debug(">>> dispatchEvent({}, {}, {})", event, obj_id, args)
   GameEvents = getGlobalVar('GameEvents')
   for listener in GameEvents:
      if event == listener['event']:
         # Join the default args with the given args
         params = listener['args'] + args
         if (
            (not obj_id and (not listener['appliesto'] or listener['appliesto'] == RS_SUFFIX_ONCE))
            or listener['id'] == obj_id
            or listener['appliesto'] == RS_SUFFIX_ANY
         ):
            debug("-- Found listener {}", listener)
            res = (True, None)
            # Callback could be the ID of a card...
            if isinstance(listener['callback'], (int, long)):
               card = Card(listener['callback'])
               # Don't trigger auto ability for chars in a UA
               if inUAttack(card):
                  notify("{}'s ability cannot be activated because it joined an United Attack.".format(card))
                  res = (None, listener['callback'])
                  continue
               # Call callback
               scope = listener['scope']
               if (
                  # Event added by active player (me)
                  (not scope and me.isActive and listener['controller'] == me._id)
                  # Events affects any player
                  or scope == RS_PREFIX_ANY
                  # Event added by the opponent
                  or (scope == RS_PREFIX_OPP and listener['controller'] != me._id)
                  or obj_id  # FIXME Needed?
               ):
                  pcard = getGameCard(card)
                  if not pcard.rules.parsed:
                     pcard.init()
                  # Something happened during execution
                  if not pcard.rules.execAuto(None, event, *params):
                     res = (False, listener['callback'])
                  # This is fine
                  else:
                     playSnd('activate-3')
               if listener['appliesto'] == RS_SUFFIX_ONCE:
                  removeGameEventListener(card._id)
            # ... or the name of a global function
            else:
               try:
                  func = eval(listener['callback']) # eval is a necessary evil
               except:
                  debug("Callback function {} is not defined", listener['callback'])
                  continue
               res = (func(*params), listener['source'] or listener['id'])
   return res


def triggerHook(event, obj_id = None, args = []):
   """
   Hook system. It returns a boolean whether the given action defined by the hook is allowed or not or not.
   """
   res, source = dispatchEvent(event, obj_id, args)
   debug("triggerHook({}, {}, {}) => {}, {}", event, obj_id, args, res, source)
   # If the action is not allowed, maybe we should notify the player
   if res == False and source:
      if event in MSG_HOOKS_ERR:
         notifyAbility(args[0], source, MSG_HOOKS_ERR[event], isWarning = True)
   return res
   
   
def cleanupGameEvents(restr):
   """
   Dispatches an event it the restriction matches, then removes it. (Like "end of turn" events.)
   """
   debug(">>> cleanupGameEvents({})", restr)
   GameEvents = getGlobalVar('GameEvents')
   removed = False
   # Iterate it in reverse order because we are removing items
   for i, listener in reversed(list(enumerate(GameEvents))):
      if listener['restr'] is None:
         continue
      restrTarget = listener['restr'][0]
      evRestr     = listener['restr'][1]
      if evRestr == restr:
         # Remove event added by me that affects me, or added by the opp that affects me as well
         if (
            (listener['controller'] == me._id and restrTarget != RS_PREFIX_OPP) or
            (listener['controller'] != me._id and restrTarget == RS_PREFIX_OPP)
         ):
            del GameEvents[i]
            removed = True
            debug("Removed listener for event {} -> {}", listener['event'], listener)
            # Invoke any callback
            onRemoveEvent(listener)
   if removed:
      setGlobalVar('GameEvents', GameEvents)

   
def onRemoveEvent(listener):
   """
   Calls the "on remove" callback if any.
   """
   func = None
   if listener['event'] == Hooks.CallOnRemove:
      func = eval(listener['callback'])
   elif listener['onremove']:
      func = eval(listener['onremove'])
   if func:
      debug("Calling on removed callback {}()", func.func_name)
      func(*listener['args'])
   
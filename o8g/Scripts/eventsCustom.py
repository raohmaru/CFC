# Python Scripts for the Card Fighters' Clash definition for OCTGN
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
# Custom event handlers
#---------------------------------------------------------------------------

def addGameEventListener(event, callback, obj_id, source_id=None, restr=None, args=[], appliesto=None):
   ge = getGlobalVar('GameEvents')
   prfx, eventName = RulesLexer.getPrefix(RS_PREFIX_EVENTS, event)
   listener = {
      'event'     : eventName,
      'controller': me._id,
      'id'        : obj_id,
      'source'    : source_id,
      'callback'  : callback,
      'restr'     : restr,
      'scope'     : prfx,
      'args'      : args,
      'appliesto' : appliesto
   }
   for e in ge:
      if (
         e['event'] == eventName
         and e['id'] == obj_id
         and e['callback'] == callback
         and e['restr'] == restr
         and e['scope'] == prfx
         and e['args'] == args
      ):
         return False
   ge.append(listener)
   setGlobalVar('GameEvents', ge)
   debug("Added listener to game event '{}' -> {}".format(eventName, listener))
   return True


def removeGameEventListener(obj_id, eventName=None, callback=None):
   debug(">>> removeGameEventListener({}, {}, {})".format(obj_id, eventName, callback))
   ge = getGlobalVar('GameEvents')
   removed = False
   for i, listener in reversed(list(enumerate(ge))):
      if not eventName or eventName == listener['event']:
         if(
            (listener['id'] == obj_id or listener['source'] == obj_id) and
            (not callback or callback == listener['callback'])
         ):
            # Events with restrictions will be removed eventually
            if listener['restr'] is None:
               del ge[i]
               removed = True
               debug("Removed listener for event {} ({})".format(listener['event'], listener))
               # Maybe invoke the callback
               if listener['event'] == Hooks.CallOnRemove:
                  func = eval(listener['callback'])
                  func(*listener['args'])
   setGlobalVar('GameEvents', ge)
   return removed


def triggerGameEvent(event, *args):
   if not settings['Play']:
      return
   debug(">>> triggerGameEvent({}, {})".format(event, args))
   obj_id = None
   if isinstance(event, list):
      event, obj_id = event
   ge = getGlobalVar('GameEvents')
   res = (None, None)
   for listener in ge:
      if event == listener['event']:
         params = list(args) + listener['args']
         if (
            (not obj_id and (not listener['appliesto'] or listener['appliesto'] == RS_SUFFIX_ONCE))
            or listener['id'] == obj_id
            or listener['appliesto'] == RS_SUFFIX_ANY
         ):
            debug("-- Found listener {}".format(listener))
            res = (True, None)
            # Callback could be the ID of a card...
            if isinstance(listener['callback'], (int, long)):
               card = Card(listener['callback'])
               # Don't trigger auto ability for chars in a UA
               if inUAttack(card):
                  notify("{}'s ability cannot be activated because it joined an United Attack".format(card))
                  res = (None, listener['callback'])
                  continue
               # Call callback
               # if card.controller == me or event in GameEventsCallOnHost:
               scope = listener['scope']
               if (
                  (not scope and me.isActive and listener['controller'] == me._id)  # default is me
                  or scope == RS_PREFIX_ANY
                  or (scope == RS_PREFIX_OPP and listener['controller'] != me._id)
                  or obj_id  # needed?
               ):
                  pcard = getParsedCard(card)
                  if not pcard.rules.parsed:
                     pcard.init()
                  if not pcard.rules.execAuto(None, event, *params):
                     res = (False, listener['callback'])
               # elif listener['scope'] in RS_PREFIX_SCOPE or obj_id:
                  # debug("-- Effect controlled by {}. Sending remote event.".format(card.controller))
                  # remoteCall(card.controller, "remoteGameEvent", [listener['callback'], event]+list(params))
                  # rnd(10, 1000) # Wait until call has been executed
                  # update()
               if listener['appliesto'] == RS_SUFFIX_ONCE:
                  removeGameEventListener(card._id)
            # ... or the name of a global function
            else:
               try:
                  func = eval(listener['callback']) # eval is a necessary evil...
               except:
                  debug("Callback function {} is not defined".format(listener['callback']))
                  continue
               res = (func(*params), listener['source'] or listener['id'])
   return res


def triggerHook(event, *args):
   res, source = triggerGameEvent(event, *args)
   debug(">>> triggerHook({}, {}) => {}, {}".format(event, args, res, source))
   if res == False and source:
      ability = event
      if isinstance(event, list):
         ability = event[0]
      if ability in MSG_HOOKS_ERR:
         notifyAbility(args[0], source, MSG_HOOKS_ERR[ability], isWarning=True)   
   return res
   

# def remoteGameEvent(cardID, eventName, *args):
   # debug(">>> remoteGameEvent({}, {}, {})".format(cardID, eventName, args))
   # card = Card(cardID)
   # pcard = getParsedCard(card)
   # pcard.rules.execAuto(None, eventName, *args)
   
   
def cleanupGameEvents(restr):
   debug(">>> cleanupGameEvents({})".format(restr))
   ge = getGlobalVar('GameEvents')
   for i, listener in reversed(list(enumerate(ge))):
      if listener['restr'] is None:
         continue
      evRestrTarget = listener['restr'][0]
      evRestr       = listener['restr'][1]
      restrMsg      = listener['restr'][2] if len(listener['restr']) > 2 else None
      if evRestr == restr:
         # Remove event added by me that affects me, or added by the opp that affects me as well
         if (
            (listener['controller'] == me._id and evRestrTarget != RS_PREFIX_OPP) or
            (listener['controller'] != me._id and evRestrTarget == RS_PREFIX_OPP)
         ):
            # Removed message
            if restrMsg:
               notify(restrMsg.format(getObjName(listener['id'])))
            del ge[i]
            debug("Removed listener for event {} -> {}".format(listener['event'], listener))
            
            # Maybe invoke the callback
            if listener['event'] == Hooks.CallOnRemove:
               func = eval(listener['callback'])
               func(*listener['args'])
                  
   setGlobalVar('GameEvents', ge)

   
def getTargetofSourceEvent(source):
   targets = []
   ge = getGlobalVar('GameEvents')
   for listener in ge:
      if listener['source'] == source:
         targets.append(Card(listener['id']))
   debug(">>> getTargetofSourceEvent({}) -> {}".format(source, targets))
   return targets
   
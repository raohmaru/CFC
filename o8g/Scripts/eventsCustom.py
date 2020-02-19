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
# Custom event handlers
#---------------------------------------------------------------------------

def addGameEventListener(event, callback, obj_id, source_id=None, restr=None, args=[]):
   ge = getGlobalVar('GameEvents')
   prfx, eventName = RulesLexer.getPrefix(RS_PREFIX_EVENTS, event)
   if not eventName in ge:
      ge[eventName] = []
   listener = {
      'controller': me._id,
      'id'        : obj_id,
      'source'    : source_id,
      'callback'  : callback,
      'restr'     : restr,
      'scope'     : prfx,
      'args'      : args
   }
   for e in ge[eventName]:
      if e['id'] == obj_id and e['callback'] == callback and e['restr'] == restr and e['scope'] == prfx:
         return False
   ge[eventName].append(listener)
   setGlobalVar('GameEvents', ge)
   debug("Added listener to game event '{}' -> {}".format(eventName, listener))
   return True


def removeGameEventListener(obj_id, eventName=None):
   debug(">>> removeGameEventListener({}, {})".format(obj_id, eventName))
   ge = getGlobalVar('GameEvents')
   removed = False
   for e in ge:
      if not eventName or e == eventName:
         for i, listener in reversed(list(enumerate(ge[e]))):
            if listener['id'] == obj_id or listener['source'] == obj_id:
               # Events with restrictions will eventually be removed in due time
               if listener['restr'] is None:
                  del ge[e][i]
                  removed = True
                  debug("Removed listener for event {} {}".format(e, listener))
   setGlobalVar('GameEvents', ge)
   return removed


def triggerGameEvent(eventName, *args):
   debug(">>> triggerGameEvent({}, {})".format(eventName, args)) #Debug
   ge = getGlobalVar('GameEvents')
   if eventName in ge:
      for listener in ge[eventName]:
         debug("-- Found listener {}".format(listener))
         params = list(args) + listener['args']
         # Callback could be the ID of a card...
         if isinstance(listener['callback'], (int, long)):
            card = Card(listener['callback'])
            if card.controller == me:
               pcard = getParsedCard(card)
               pcard.rules.execAuto(None, eventName, *params)
            elif listener['scope'] in [RS_PREFIX_OPP,RS_PREFIX_ANY]:
               remoteCall(card.controller, "remoteGameEvent", [listener['callback'], eventName]+list(params))
               update()               
         # ... or the name of a global function
         else:
            try:
               func = eval(listener['callback'])  # eval is a necessary evil...
            except:
               debug("Callback function {} is not defined".format(listener['callback']))
               continue
            if func(*params):
               return False
   return True
   
   
def remoteGameEvent(cardID, eventName, *args):
   debug(">>> remoteGameEvent({}, {}, {})".format(cardID, eventName, args))
   card = Card(cardID)
   pcard = getParsedCard(card)
   pcard.rules.execAuto(None, eventName, *args)
   
   
def cleanupGameEvents(restr):
   debug(">>> cleanupGameEvents({})".format(restr)) #Debug
   ge = getGlobalVar('GameEvents')
   for e in ge:
      for i, listener in enumerate(ge[e]):
         if listener['restr'] is None:
            continue
         evRestrTarget, evRestr = listener['restr']
         if evRestr == restr:
            # Remove event added by me that affects me, or added by the opp that affects to me
            if (
               (listener['controller'] == me._id and evRestrTarget != RS_PREFIX_OPP) or
               (listener['controller'] != me._id and evRestrTarget == RS_PREFIX_OPP) or
               len(players) == 1  # for debuggin purposes
            ):
               # Removed message
               if listener['args'][2] and len(listener['args'][2]) > 1:
                  notify(listener['args'][2][1].format(getObjName(listener['id'])))
               del ge[e][i]
               debug("Removed listener for event {} -> {}".format(e, listener))   
   setGlobalVar('GameEvents', ge)

   
def getTargetofSourceEvent(source):
   targets = []
   ge = getGlobalVar('GameEvents')
   for e in ge:
      for listener in ge[e]:
         if listener['source'] == source:
            targets.append(Card(listener['id']))
   debug(">>> getTargetofSourceEvent({}) -> {}".format(source, targets)) #Debug
   return targets
   
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

def addGameEventListener(eventName, callback, card_id, restr=None, *args):
   ge = getGlobalVar('GameEvents')
   if not eventName in ge:
      ge[eventName] = []
   ge[eventName].append({
      'controller': me._id,
      'id'        : card_id,
      'callback'  : callback,
      'restr'     : restr,
      'args'      : args
   })
   setGlobalVar('GameEvents', ge)
   debug("Added listener to game event '{}' -> {}({})".format(eventName, callback, args))


def removeGameEventListener(card_id, eventName=None):
   ge = getGlobalVar('GameEvents')
   for e in ge:
      if not eventName or e == eventName:
         for i, listener in enumerate(ge[e]):
            if listener['id'] == card_id:
               del ge[e][i]
               debug("Removed listener for event {} {}".format(e, listener))            
   setGlobalVar('GameEvents', ge)


def triggerGameEvent(eventName, *args):
   debug(">>> triggerGameEvent({}, {})".format(eventName, args)) #Debug
   ge = getGlobalVar('GameEvents')
   if eventName in ge:
      for listener in ge[eventName]:
         params = args + listener['args']
         # Callback could be the ID of a card...
         if isinstance(listener['callback'], int):
            card = Card(listener['callback'])
            if card.controller == me:
               pcard = getParsedCard(card)
               pcard.rules.execAuto(None, eventName, *args)
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
   
   
def cleanupGameEvents(restr):
   debug(">>> cleanupGameEvents({})".format(restr)) #Debug
   ge = getGlobalVar('GameEvents')
   for e in ge:
      for i, listener in enumerate(ge[e]):
         if listener['restr'] == restr and listener['controller'] == me._id:
            del ge[e][i]
            debug("Removed listener for event {} {}".format(e, listener))   
   setGlobalVar('GameEvents', ge)
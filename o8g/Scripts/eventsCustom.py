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

def addGameEventListener(eventName, callback, source_id, *args):
   ge = getGlobalVar('GameEvents')
   if not eventName in ge:
      ge[eventName] = []
   ge[eventName].append({
      'id'      : source_id,
      'callback': callback,
      'args'    : args
   })
   setGlobalVar('GameEvents', ge)
   debug("Added listener to game event '{}' -> {}({})".format(eventName, callback, args))


def removeGameEventListener(card_id):
   ge = getGlobalVar('GameEvents')
   for eventName in ge:
      for i, listener in enumerate(ge[eventName]):
         if listener['id'] == card_id:
            del ge[eventName][i]
            debug("Removed listener {}".format(listener))            
   setGlobalVar('GameEvents', ge)


def triggerGameEvent(eventName, *args):
   debug(">>> triggerGameEvent({}, {})".format(eventName, args)) #Debug
   ge = getGlobalVar('GameEvents')
   if eventName in ge:
      for listener in ge[eventName]:
         try:
            func = eval(listener['callback'])  # eval is a necessary evil...
         except:
            debug("Callback function {} is not defined".format(listener['callback']))
            continue
         params = args + listener['args']
         if func(*params):
            return False
   return True
   
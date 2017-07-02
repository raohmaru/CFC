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
# Events class
#---------------------------------------------------------------------------

class RulesEvents():
   """ Class to handle the custom events that happens during the game """
   items = {}

   @staticmethod
   def register(name, func):
      RulesEvents.items[name.lower()] = func
      
   
   @staticmethod   
   def check(event, eventData, *args):
      debug("-- Checking event {}({}) against {}".format(event, args, eventData))
      prfx, eventName = RulesLexer.getPrefix(RS_PREFIX_EVENTS, event)
      if eventName != eventData[1] or prfx != eventData[0]:
         return None
      if eventName in RulesEvents.items:
         func = RulesEvents.items[eventName]
         # func = eval(RulesEvents.items[eventName])  # eval is a necessary evil...
         return func(eventData[2], *args)
      else:
         debug("-- event not found: {}".format(eventName))
         return None
      

#---------------------------------------------------------------------------
# Events functions
#---------------------------------------------------------------------------

def eventHandChanges(expr, actual=None):
   if actual == None:
      actual = len(me.hand)
   debug(">>> eventHandChanges({}, {})".format(expr, actual)) #Debug
   return evalExpression(expr, actual)
   

def eventGenericHandler(expr, *args):
   return True


RulesEvents.register(GameEvents.HandChanges, eventHandChanges)
RulesEvents.register(GameEvents.EndPhase,    eventGenericHandler)
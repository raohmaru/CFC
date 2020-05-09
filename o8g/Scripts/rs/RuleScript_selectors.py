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
# Filter class
#---------------------------------------------------------------------------

class RulesSelectors():
   """ Class to handle selectors that are applied to a set of targets """
   selectors = {}

   @staticmethod
   def registerSelector(name, selector):
      RulesSelectors.selectors[name] = selector
   
   
   @staticmethod
   def applySelector(selector, targets):
      cmd, expr = selector
      
      # Get the selector function
      if cmd in RulesSelectors.selectors:      
         debug("-- applying selector ::{}({}) to {}".format(cmd, expr, cardsNamesStr(targets)))
         func = RulesSelectors.selectors[cmd]
         res = evalExpression(expr, True, getLocals())
         targets = func(targets, res)
         debug("-- new selection: {}".format(cardsNamesStr(targets)))
         
      return targets


#---------------------------------------------------------------------------
# Selector functions
#---------------------------------------------------------------------------

def selectorNot(targets, args):
   debug(">>> selectorNot({}, {})".format(targets, args))
   return list(set(targets).difference(args))
   

RulesSelectors.registerSelector('not', selectorNot)
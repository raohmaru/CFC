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
# Unit tests
#---------------------------------------------------------------------------

from cardsRules import RulesDict
from RuleScript_lexer import RulesLexer
import pprint

pp = pprint.PrettyPrinter(indent=4)

if not 'debug' in globals():
   # Make debug accessible from any module
   import __builtin__
   def debug(str):
      print str
   __builtin__.debug = debug

   
rules = RulesDict['aa867ea1-89f8-4154-8e20-2263edd00002']
parsed = RulesLexer.parse(rules)
pp.pprint(parsed)
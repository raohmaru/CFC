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
from rs.RuleScript_lexer import RulesLexer
import pprint

pp = pprint.PrettyPrinter(indent=4)
   
# Rules to test
targets = [
   "target = character",
   "target = characters[attack]",
   "target = character@hand",
   "target = Captain[attack] @ oppRing",
   "target = robot[-block]@myhand",
   "target = character,action[bp>=800,frozen]@oppRing",
   "target = ^character[fresh&powerless]",
   "target = [fresh]",
   "target = character@invalidZone",
]
actions = [
   # "action = destroy()",
   # "action = draw(1)",
   # "action = destroy & draw(1)",
   # "action = discard(1) & draw(1)",
   # "action = destroy(); draw(1)",
   "action = {F}: destroy()",
   "action = {D}{F}: destroy()",
   "action = {D(2)}{F}: destroy()",
   # "action = {f}:destroy() & draw(1)",
   # "action = {S(character@myRing)}: destroy()",
   # "action = {D}: destroy() to(character[bp>=800]@oppRing)",
   # "action = {E(reaction@discard)}: may moveTo(hand)",
   # "action = {E(reaction@discard)}: may('Question?') moveTo(hand)",
   # "action = destroy() ueot",
   "action = {D(action)}: may('Question?') destroy() to(character) & freeze; draw(2) ueot",
   # "action = {F}:  to(character) ueot",
   "action = {D(2)}: +cantblock to(character@oppRing) ueot",
]
abilities = [
   "abilities = unblockable",
   "abilities = unblockable, rider",
   "abilities =      ",
]
autos = [
   "auto = destroy()",
   "auto = ~myHandChanges~ destroy()",
   "auto = ~HandChanges~ destroy() & draw(1)",
   "auto = ~oppHandChanges~ may destroy()",
   "auto = ~myHandChanges~ destroy() to(character@myRing)",
   "auto = ~myHandChanges~ destroy() ueot",
   "auto = ~handChanges:0~ +unblockable",
   "auto = ~myHandChanges : >0~ -unblockable",
   "auto = ~myHandChanges :>=0~ -unblockable",
   "auto = ~myHandChanges:0~ may('Question?') destroy() & +unblockable to(character@myRing) uynt",
   "auto = ~myEndPhase~ moveTo(ctrlHand) to(characters[bp>=800])"
]

if not 'debug' in globals():
   # Make debug accessible from any module
   import __builtin__
   def debug(str):
      print str
   __builtin__.debug = debug

def test(arr, title):
   print "Testing {} ".format(title) + ("=" * 80) + "\n"
   for item in arr:
      tokens = RulesLexer.tokenize(item)
      pp.pprint(tokens)
      print ""

# rules = RulesDict['aa867ea1-89f8-4154-8e20-2263edd00002']
# test(targets, 'targets')
# test(actions, 'actions')
# test(abilities, 'abilities')
test(autos, 'autos')

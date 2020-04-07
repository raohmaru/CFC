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
   "target = character,reactions",
   "target = characters[attack]",
   "target = character@hand",
   "target = @oppRing",
   "target = Captain[attack] @ oppRing",
   "target = robot[-block]@myhand",
   "target = character,action[bp>=800,frozen]@oppRing",
   "target = ^character[fresh&powerless]",
   "target = ^character[fresh & -powerless]",
   "target = [fresh]",
   "target = character@invalidZone",
   "target = *<2>@oppDeck",
   "target = <r>@hand",
   "target = <r2>action@hand[bp>300]",
   "target = <1>action@hand",
   "target = <1,2>action@hand",
   "target? = <,4>*<-2>@myDeck",
   "target? = <1?>*<2>@deck",
   "target = <**>characters@myRing",
   'target = "Juni"&"Juli"<1>@myDeck',
   "target = characters[bp:lowest]",
]
actions = [
   # "action = destroy()",
   # "action = draw(1)",
   # "action = destroy & draw(1)",
   # "action = discard(1) & draw(1)",
   # "action = destroy(); draw(1)",
   # "action = {F}: destroy()",
   # "action = {D}{F}: destroy()",
   # "action = {D(2)}{F}: destroy()",
   # "action = {f}:destroy() & draw(1)",
   # "action = {S(character@myRing)}: destroy()",
   # "action = {D}: destroy() to(character[bp>=800]@oppRing)",
   # "action = {E(reaction@discard)}: [[may]] moveTo(hand)",
   # "action = {E(reaction@discard)}: [[may 'Question?']] moveTo(hand)",
   # "action = destroy() ueot",
   # "action = destroy() oppueot",
   # "action = {D(action)}: [[if me.HP < 10]] destroy() to(character) & freeze; draw(2) ueot",
   # "action = {F}:  to(character) ueot",
   # "action = {D(2)}: +cantblock to(character@oppRing) ueot",
   # "action = [[may Destroy all humans?]] destroy()",
   "action = [[if me.hand == 0]] destroy() uynt",
   "action = [[if true]] discard(all) target(me) [[elif false]] damage(5) target(opp)",
   "action = [[if true]] discard(all) [[else]] damage(5) target(opp)",
   "action = [[if true]] discard(all) [[invalid]] damage(5) target(opp)",
   "action = [[invalid true]] discard(all) [[else]] damage(5)",
   # "action = moveTo(ctrlHand, -1, true) target?(characters[bp>=800]) uynt",
   # "action = {F}: moveTo(ctrlDeck) target(characters[-backup]) & shuffle(myDeck) & shuffle(oppDeck)",
   # "action = {F}: destroy() target(^character@myRing) & damage(5, character)",
   # "action = [[if  all myring: bp <= 3]] playExtraChar()",
   # "action = {F}: moveTo(@oppDeck) target(*@hand); moveTo(hand) target(*<-1>@oppDeck)",
   # "action = {F}: reveal(hand) & myHand.each(bp <= 3 { bp(+2) }) target(this)"
   # "action = swapChars() target(<2>character)\naction = moveToSlot() target(character)",
   # "action = rndDiscard()",
   # "action = reveal(hand) & each(action in me.hand => bp(+2)) target(this) & discard(actions)"
   # "action = discard(<,1>action@oppHand)",
]
abilities = [
   "abilities = unblockable",
   "abilities = unblockable, rider",
   "abilities =      ",
]
autos = [
   # "auto = destroy()",
   # "auto = ~my HandChanges~ destroy()",
   # "auto = ~HandChanges~ destroy() & draw(1)",
   # "auto = ~opp HandChanges~ [[if oppRing<2]] destroy()",
   # "auto = ~ myHandChanges ~ destroy() to(character@myRing)",
   # "auto = ~myHandChanges~ destroy() ueot",
   # "auto = ~handChanges~ +unblockable",
   # "auto = ~myHandChanges~ -unblockable",
   # "auto = ~myHandChanges,oppBlockPhase~ -unblockable",
   # "auto = [[may 'Question?']] destroy() & +unblockable to(character@myRing) uynt",
   # "auto = ~myEndPhase~ moveTo(ctrlHand) to(characters[bp>=800])",
   # "auto = ~anyBlockPhase~ +unblockable to(characters[bp<=300 & attack & -uattack]) ueot",
   # "auto = ~playerCombatDamaged fromThis~ +cantplayac to(opp) oppueot",
   # "auto = ~playerDamaged:fromThis~ draw() target?(opp)",
   "auto = oppCanBeBlocked:any? [[if blocker.bp > this.bp]]",
   # "auto = ~anyPlayerDamaged:action~ damage(1) to(damagedPlayer)",
   "auto = ~anyPlayerDamaged:action~ [[if me.hp < 10]] hp(+1)",
]
evals = [
   "action in me.hand => bp(+2)"
]
requisite = [
   "requisite = char<1>@oppRing && char<1>@myRing"
]
vars = [
   "vars = coin := rnd(2)",
   "vars = coin := flipCoin(); res := rnd(4)",
]
labels = [
   "label = KO this character",
   "label = 'KO this character'",
]
rules = [
   """
   label  = "KO this character"
   action = destroy()
   label  = "Discard a character card"
   action = discard(character)
   """
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
# test(autos, 'autos')
# test(requisite, 'requisite')
# test(vars, 'vars')
test(labels, 'labels')
test(rules, 'rules')

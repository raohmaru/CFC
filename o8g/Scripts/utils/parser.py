# Python Scripts for the Card Fighters' Clash definition for OCTGN
# Copyright (C) 2022 Raohmaru

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

import re

#---------------------------------------------------------------------------
# Parser/eval/evil functions
#---------------------------------------------------------------------------

def replaceVars(str):
   """
   Replaces variables of the card rules.
   """
   debug("-- replaceVars({})", str)
   # Order matters
   str = replaceIfRgx (str, "listIdx"   , r"\1[\2]", False)
   str = replaceIfRgx (str, ".bp"       , r"getGameCard(\1).BP")
   str = replaceIfRgx (str, ".sp"       , r"\1.SP")
   str = replaceIfRgx (str, ".lastbp"   , r"getGameCard(\1).getState('lastBP')")
   str = replaceIfRgx (str, ".ability"  , r"getGameCard(\1).ability.type")
   str = replaceIfRgx (str, "action"    , "isAction(getCardByContext(locals()))")
   str = replaceIfRgx (str, "reaction"  , "isReaction(getCardByContext(locals()))")
   str = replaceIfRgx (str, "char"      , "isCharacter(card)")
   str = replaceIfRgx (str, ".ring.size", r"getRingSize(\1)")
   str = replaceIfRgx (str, ".ring"     , r"getRing(\1)")
   str = replaceIfRgx (str, ".size"     , r"len(\1)")
   str = replaceIfRgx (str, ".ncdamaged", r"getState(\1, 'ncdamaged')")
   str = replaceIfRgx (str, ".lostsp"   , r"getState(\1, 'lostsp')")
   str = replaceIfRgx (str, "opp"       , r"getOpp()")
   str = replaceIf    (str, ".hp"       , ".HP")
   str = replaceIf    (str, "alone"     , "getRingSize() == 1")
   str = replaceIf    (str, "attacker"  , "attacker[0]")
   str = replaceIf    (str, "blocker"   , "blocker[0]")
   str = replaceIf    (str, "soloattack", "len(getAttackingCards()) == 1")
   str = replaceIf    (str, ".discards" , ".piles['Discard pile']")
   debug("---- {}", str)
   return str

   
def replaceIfRgx(str, name, repl, opt = True):
   if not opt or name in str:
      str = re.sub(Regexps[name], repl, str)
   return str
   
   
def replaceIf(str, name, repl, isRgx = True):
   if name in str:
      str = str.replace(name, repl)
   return str
   
   
def getCardByContext(obj):
   if "card" in obj:
      return obj["card"]
   elif "trigger" in obj:
      return obj["trigger"]


def evalExpression(expr, retValue = False, locals = None):
   debug("evalExpression({})\nLocals: {}", expr, locals)
   expr = replaceVars(expr)
   forexpr = "[{} for card in {}]"
   
   if " in " in expr:
      parts = expr.split(" in ")
      expr = forexpr.format(parts[0], parts[1])
   
   if "all " in expr:
      expr = expr.replace("all ", "")
      # https://docs.python.org/2.7/library/functions.html
      expr = "all(" + expr + ")"
   
   try:
      res = eval(expr, getEnvVars(), locals)
      if retValue:
         debug("-- Evaluated expr  %s  (%s)" % (expr, res))
         return res
      else:
         debug("-- Evaluated expr  %s  ?  (%s)" % (expr, bool(res)))
         return bool(res)
   except:
      debug("-- %s  is not a valid Python expression" % (expr))
      return None


def getTargets(str, source = None):
   """
   Parses a target strings and returns the targeted cards.
   """
   cardsTokens = RulesLexer.parseTarget(str.lower())
   return RulesUtils.getTargets(cardsTokens, source)

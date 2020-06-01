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
# Performance tests
#---------------------------------------------------------------------------
import sys
sys.path.append('..')
from time import time
import timeit
import re
from config import Regexps, Struct
   
def test(fun, args=[], r=1000):
   t = time()
   for x in range(r):
      fun(*args)
   print 'duration:', time()-t

#---------------------------------------------------------------------------

def replaceVars(str):
   str = re.sub(Regexps['bp']        , r'getParsedCard(\1).BP', str)
   str = re.sub(Regexps['lastbp']    , r'getParsedCard(\1).lastBP', str)
   str = re.sub(Regexps['action']    , 'isAction(card)', str)
   str = re.sub(Regexps['reaction']  , 'isReaction(card)', str)
   str = re.sub(Regexps['char']      , 'isCharacter(card)', str)
   str = re.sub(Regexps['size']      , r'len(\1)', str)
   str = re.sub(Regexps['ring']      , r'getRingSize(\1)', str)
   str = re.sub(Regexps['chars']     , r'getRing(\1)', str)
   str = re.sub(Regexps['damaged']   , r'getState(\1, "damaged")', str)
   str = re.sub(Regexps['lostsp']    , r'getState(\1, "lostsp")', str)
   str = re.sub(Regexps['opp']       , r'getOpp()', str)
   str = re.sub(Regexps['fromaction'], 'isAction(trigger)', str)
   str = str.replace('.sp'           , '.SP')
   str = str.replace('.hp'           , '.HP')
   str = str.replace('alone'         , 'getRingSize() == 1')
   str = str.replace('attacker'      , 'attacker[0]')
   str = str.replace('blocker'       , 'blocker[0]')
   str = str.replace('soloattack'    , 'len(getAttackingCards()) == 1')
   str = str.replace('.discards'     , '.piles["Discard pile"]')
   return str


def replaceVarsIf(str):
   # Order is important
   str = replaceCond(str, 'bp'        , r'getParsedCard(\1).BP')
   str = replaceCond(str, 'lastbp'    , r'getParsedCard(\1).lastBP')
   str = replaceCond(str, 'action'    , 'isAction(card)')
   str = replaceCond(str, 'reaction'  , 'isReaction(card)')
   str = replaceCond(str, 'char'      , 'isCharacter(card)')
   str = replaceCond(str, 'size'      , r'len(\1)')
   str = replaceCond(str, 'ring'      , r'getRingSize(\1)')
   str = replaceCond(str, 'chars'     , r'getRing(\1)')
   str = replaceCond(str, 'damaged'   , r'getState(\1, "damaged")')
   str = replaceCond(str, 'lostsp'    , r'getState(\1, "lostsp")')
   str = replaceCond(str, 'opp'       , r'getOpp()')
   str = replaceCond(str, 'fromaction', 'isAction(trigger)')
   str = replaceCond(str, '.sp'       , '.SP', False)
   str = replaceCond(str, '.hp'       , '.HP', False)
   str = replaceCond(str, 'alone'     , 'getRingSize() == 1', False)
   str = replaceCond(str, 'attacker'  , 'attacker[0]', False)
   str = replaceCond(str, 'blocker'   , 'blocker[0]', False)
   str = replaceCond(str, 'soloattack', 'len(getAttackingCards()) == 1', False)
   str = replaceCond(str, '.discards' , '.piles["Discard pile"]', False)
   return str

R = {
   'bp'     : r'getParsedCard(\1).BP',
   'lastbp' : r'getParsedCard(\1).lastBP',
   'size'   : r'len(\1)',
   'ring'   : r'getRingSize(\1)',
   'chars'  : r'getRing(\1)',
   'damaged': r'getState(\1, "damaged")',
   'lostsp' : r'getState(\1, "lostsp")',
   'opp'    : r'getOpp()',
}
   
def replaceVarsIf2(str):
   # Order is important
   str = replaceCond(str, 'bp'        , R['bp'])
   str = replaceCond(str, 'lastbp'    , R['lastbp'])
   str = replaceCond(str, 'action'    , 'isAction(card)')
   str = replaceCond(str, 'reaction'  , 'isReaction(card)')
   str = replaceCond(str, 'char'      , 'isCharacter(card)')
   str = replaceCond(str, 'size'      , R['size'])
   str = replaceCond(str, 'ring'      , R['ring'])
   str = replaceCond(str, 'chars'     , R['chars'])
   str = replaceCond(str, 'damaged'   , R['damaged'])
   str = replaceCond(str, 'lostsp'    , R['lostsp'])
   str = replaceCond(str, 'opp'       , R['opp'])
   str = replaceCond(str, 'fromaction', 'isAction(trigger)')
   str = replaceCond(str, '.sp'       , '.SP', False)
   str = replaceCond(str, '.hp'       , '.HP', False)
   str = replaceCond(str, 'alone'     , 'getRingSize() == 1', False)
   str = replaceCond(str, 'attacker'  , 'attacker[0]', False)
   str = replaceCond(str, 'blocker'   , 'blocker[0]', False)
   str = replaceCond(str, 'soloattack', 'len(getAttackingCards()) == 1', False)
   str = replaceCond(str, '.discards' , '.piles["Discard pile"]', False)
   return str

   
def replaceCond(str, name, repl, isRgx=True):
   if name in str:
      if isRgx:
         str = re.sub(Regexps[name], repl, str)
      else:
         str = str.replace(name, repl)
   return str

s = 'card.bp <= 300 and action and not opp.damaged and opp.hp > 1000'
# test(replaceVars, s)
# test(replaceVarsIf, s)

# test(replaceVarsIf, [s])
# test(replaceVarsIf2, [s])

#---------------------------------------------------------------------------

n = 0
d = {
   'a': 1,
   'b': 2
}
s = Struct(**{
   'a': 1,
   'b': 2
})

def testDict(n, d):
   d = {
      'a': 1,
      'b': 2
   }
   n += d['a'] + d['b']
   
def testStruct(n, s):
   s = Struct(**{
      'a': 1,
      'b': 2
   })
   n += s.a + s.b
   
print timeit.timeit('testDict(n, d)',    'from __main__ import testDict, n, d',    number=1000)
print timeit.timeit('testStruct(n, s)',  'from __main__ import testStruct, n, s',  number=1000)
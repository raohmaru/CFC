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

"""
***RuleScript***
Case Insensitive

---------------------------------------------------
target = type[filters] @ zone

Only one target is allowed.

type:
   Operators:
      , (or)
   Values:
      Any Type: Character, Action, Reaction
      Any Subtype: Warrior, Pilot, Captain...
   Keywords:
      player
      me
      opp
      this
      *
   Prefixes:
      ^ (other)
   Sufixes:
      s (plural) (valid on Type, Subtype, player or *)

filters:
   Operators:
      , (or)
      & (and)
   Values:
      Any Type: Character, Action, Reaction
      Any Subtype: Warrior, Pilot, Captain...
   Keywords:
      bp [=|>=|<=] number
      sp [=|>=|<=] number
      backedup
      backup
      attack
      uattack
      block
      frozen
      fresh
      powerless
   Prefixes:
      - (not)

zone:
   Keywords:
      arena (default)
      ring
      hand
      deck
      discard
      kill
   Prefixes:
      my (default)
      opp

---------------------------------------------------
action = [{cost}:] [cond] effect [& effect] [to(target)] [restr]; ...

Only one action is allowed.
Several effects can be joined with ';'.

cost:
   Keywords:
      F
      S | S(target)
      D | D(target)
      E | E(target)

cond:
   Keywords:
      may
      may('Question')
      
effect:
   Values:
      Effect command (followed by () with 0 or more parameters):
         damage(#)
      Ability:
         Prefixes:
            +
            -
   Operators:
      & (and)
      
=>:
   Parameters:
      A valid target
      
restr:
   Keywords:
      ueot
      uynt
      
---------------------------------------------------
auto = [<event:expr>] [cond] effect [& effect] [to(target)] [restr]

A card can have one or more `auto` keys

event:
   Keywords:
      blocked

cond:
   Keywords:
      may
      may('Question')
      
---------------------------------------------------
abilities = ability [, ability]

ability:
   Keywords:
      unblockable

---------------------------------------------------
"""

RulesDict = {}

# Nina's WINGS
RulesDict['55b0c9ff-4b3a-4b08-adc1-f1b5e03adef9'] = """
abilities = unblockable
auto = <myHandChanges> if myHand == 0 then +unblockable
auto = <myHandChanges:0> +unblockable
"""

# Ryu no Senshi's DRAGON TRANSFORM
RulesDict['48a07b48-7415-42e7-a3cd-6bae37c56489'] = """
action = {F}: damage(1) to(characters@oppRing)
"""

# Blodia's ENERGY COST
RulesDict['b8a8653c-0286-4b05-a255-c436fd23132d'] = """
target = me
action = damage(3)
"""

# Jill's BERETTA
RulesDict['0b2c9e8a-5f9b-4ab5-a9b3-414f1154ce24'] = """
action = {F}: damage(1) to(opp,character@oppRing)
"""
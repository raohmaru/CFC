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
target=type[filters]|zone

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
action={cost}: [cond] effect [& effect] [->(target)] [restr]; ...

cost:
   Keywords:
      F, S(target), D(target), E(target)

cond:
   Keywords:
      may
      may('Question')
      
effect:
   Values:
      Valid effect followed by () with 0 or more parameters
   Operators:
      & (and)
      
->:
   Parameters:
      A valid target
      
restr:
   Keywords:
      ueot, uynt

---------------------------------------------------
"""

RulesDict = {}

# Ryu no Senshi's DRAGON TRANSFORM
RulesDict['aa867ea1-89f8-4154-8e20-2263edd00002'] = """
target = character[-block]|oppRing
action = {F(action|kill)}: may('Question?') freeze() & damage(1)->(characters[-backup]|oppRing) ueot; draw(1, me)
"""

# Jin Saotome's SAOTOME DYNAMITE
RulesDict['aa867ea1-89f8-4154-8e20-2263edd00009'] = """
target = character[block]
target = character|oppRing
"""

# Damn D's WHISTLE
RulesDict['aa867ea1-89f8-4154-8e20-2263edd00014'] = """
target = ^character[-frozen]|arena
target = character[bp<=5]|myDeck
"""

# Strider Hiryu's CYPHER
RulesDict['aa867ea1-89f8-4154-8e20-2263edd00135'] = """
target = character[fresh]
target = character[backedup]
"""

# Kyo Kusanagi's 182 WAYS
RulesDict['aa867ea1-89f8-4154-8e20-2263edd00240'] = """
target = ^character[powerless]
target = opp,character|oppRing
"""

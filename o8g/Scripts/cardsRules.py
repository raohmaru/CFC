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
Whitespace Insensitive

target=type[restr]|zone

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
   Example:
      Character,player

restr:
   Operators:
      , (or)
      & (and)
   Values:
      Any Type: Character, Action, Reaction
      Any Subtype: Warrior, Pilot, Captain...
   Keywords:
      bp [=|>=|<=] number
      sp [=|>=|<=] number
      backed
      backup
      attack
      uattack
      block
      freezed
      fresh
      powerless
   Prefixes:
      - (not)

zone:
   Keywords:
      arena
      ring
      hand
      deck
      discard
      kill
      *
   Prefixes:
      my
      opp

"""

RulesDict = {}

RulesDict['dragon transform'] = """
target = ME
target = * # A comment
# target = *
target = player,Character
target = [-backup]|oppRing
target = character[-backup]
target = Warrior,*[attack,-backup]|arena
target = this|wrongZone
target = me,opp[  attack  &  bp >= 4, -  backup  ]|  oppRing  ,  hand  
"""

# Jin Saotome's SAOTOME DYNAMITE
RulesDict['aa867ea1-89f8-4154-8e20-2263edd00009'] = """
target = character|oppRing
"""

# Damn D's WHISTLE
RulesDict['aa867ea1-89f8-4154-8e20-2263edd00014'] = """
target = character[bp<=500]|myDeck
"""

# Strider Hiryu's CYPHER
RulesDict['aa867ea1-89f8-4154-8e20-2263edd00135'] = """
target = character[backed]
"""

# Kyo Kusanagi's 182 WAYS
RulesDict['aa867ea1-89f8-4154-8e20-2263edd00240'] = """
target = opp,character|oppRing
"""
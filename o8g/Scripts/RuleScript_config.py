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

import re

#---------------------------------------------------------------------------
# RULESCRIPT CONST LANGUAGE DEFINITION
#---------------------------------------------------------------------------

# Regular expressions
AS_RGX_CMD_TARGET   = re.compile(r'^target\s*=\s*')
AS_RGX_TARGET_TYPE  = re.compile(r'\||\[')
AS_RGX_TARGET_RESTR = re.compile(r'\[(.+)\]')
AS_RGX_TARGET_PARAM = re.compile(r'(\w+)\s*([=><]+)\s*(\w+)')
AS_RGX_TARGET_ZONE  = re.compile(r'\|\s*([\w*]+).*$')

# Comments
AS_COMMENT_CHAR = '#'

# Operators
AS_OP_OR    = ','
AS_OP_AND   = '&'
AS_OP_EQUAL = '='
AS_OP_LTE   = '<='
AS_OP_GTE   = '>='

# Prefixes
AS_PREFIX_NOT   = '-'
AS_PREFIX_MY    = 'my'
AS_PREFIX_OPP   = 'opp'
AS_PREFIX_OTHER = '^'

AS_PREFIX_TYPES = [
   AS_PREFIX_OTHER
]

AS_PREFIX_ZONES = [
   AS_PREFIX_MY,
   AS_PREFIX_OPP
]

AS_PREFIX_FILTERS = [
   AS_PREFIX_NOT
]

# Sufixes
AS_SUFFIX_PLURAL = 's'

AS_SUFFIX_TYPES = [
   AS_SUFFIX_PLURAL
]

# Keywords
AS_KW_ALL = '*'

# Target keywords
AS_KW_TARGET_PLAYER   = 'player'
AS_KW_TARGET_PLAYERS  = 'players'
AS_KW_TARGET_ME       = 'me'
AS_KW_TARGET_OPP      = 'opp'
AS_KW_TARGET_THIS     = 'this'
AS_KW_TARGET_CHAR     = 'character'
AS_KW_TARGET_ACTION   = 'action'
AS_KW_TARGET_REACTION = 'reaction'
AS_KW_TARGETS = [
   AS_KW_TARGET_THIS,
   AS_KW_TARGET_PLAYER,
   AS_KW_TARGET_ME,
   AS_KW_TARGET_OPP,
   AS_KW_TARGET_CHAR,
   AS_KW_TARGET_ACTION,
   AS_KW_TARGET_REACTION,
   AS_KW_ALL
]
AS_KW_TARGET_IS_PLAYER = [
   AS_KW_TARGET_PLAYER,
   AS_KW_TARGET_PLAYERS,
   AS_KW_TARGET_ME,
   AS_KW_TARGET_OPP
]
AS_KW_PLAYERS = [
   AS_KW_TARGET_ME,
   AS_KW_TARGET_OPP
]
AS_KW_CARD_TYPES = [
   AS_KW_TARGET_CHAR,
   AS_KW_TARGET_ACTION,
   AS_KW_TARGET_REACTION
]

# Zone keywords
AS_KW_ZONE_ARENA   = 'arena'
AS_KW_ZONE_RING    = 'ring'
AS_KW_ZONE_HAND    = 'hand'
AS_KW_ZONE_DECK    = 'deck'
AS_KW_ZONE_DISCARD = 'discard'
AS_KW_ZONE_KILL    = 'kill'
AS_KW_ZONES = [
   AS_KW_ZONE_ARENA,
   AS_KW_ZONE_RING,
   AS_KW_ZONE_HAND,
   AS_KW_ZONE_DECK,
   AS_KW_ZONE_DISCARD,
   AS_KW_ZONE_KILL
]

AS_KW_TARGET_ZONES = [
   AS_KW_ZONE_ARENA,
   AS_KW_ZONE_RING
]

AS_KW_ZONES_PILES = [
   AS_KW_ZONE_HAND,
   AS_KW_ZONE_DECK,
   AS_KW_ZONE_DISCARD,
   AS_KW_ZONE_KILL
]

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

RS_VERSION = '0.1.0'

# Available keys
RS_KEY_TARGET    = 'target'
RS_KEY_ACTION    = 'action'
RS_KEY_ABILITIES = 'abilities'
RS_KEY_AUTO      = 'auto'

# Regular expressions
RS_RGX_KEY_TARGET   = re.compile(r'^target\s*=\s*')
RS_RGX_TARGET_TYPE  = re.compile(r'@|\[')
RS_RGX_TARGET_RESTR = re.compile(r'\[(.+)\]')
RS_RGX_TARGET_PARAM = re.compile(r'(\w+)\s*([=><]+)\s*(\w+)')
RS_RGX_TARGET_ZONE  = re.compile(r'@\s*([\w*]+).*$')
RS_RGX_TARGET_PICK  = re.compile(r'<\s*((?:\+|\-)?\s*[0-9]+)\s*>')
RS_RGX_TARGET_QTY   = re.compile(r'^<\s*((?:r\d*)|(?:,?[0-9]+){1,2})\s*>')

RS_RGX_KEY_ACTION   = re.compile(r'^action\s*=\s*')
RS_RGX_AC_COST      = re.compile(r'(\{.+\}\s*)\s*:\s*')
RS_RGX_AC_EVENT     = re.compile(r'~\s*([\w,]+)\s*?~')
RS_RGX_AC_TARGET    = re.compile(r'\b(?:to|target)\s*\(([^)]+)\)')
RS_RGX_AC_EFFECT    = re.compile(r'([\w.]+)\s*\((.*?)\)$')

RS_RGX_KEY_ABILITY  = re.compile(r'^abilities\s*=\s*')
RS_RGX_KEY_AUTO     = re.compile(r'^auto\s*=\s*')

RS_RGX_PARAM        = re.compile(r'\(([^)]*)\)')
RS_RGX_COND         = re.compile(r'\[\[([^\]]+)\]\]\s')

# Comments
RS_COMMENT_CHAR = '#'

# Operators
RS_OP_OR    = ','
RS_OP_AND   = '&'
RS_OP_SEP   = ';'
RS_OP_EQUAL = '='
RS_OP_LTE   = '<='
RS_OP_GTE   = '>='

# Prefixes
RS_PREFIX_PLUS  = '+'
RS_PREFIX_NOT   = '-'
RS_PREFIX_MY    = 'my'
RS_PREFIX_OPP   = 'opp'
RS_PREFIX_CTRL  = 'ctrl'
RS_PREFIX_ANY   = 'any'
RS_PREFIX_OTHER = '^'

RS_PREFIX_TYPES = [
   RS_PREFIX_OTHER
]

RS_PREFIX_ZONES = [
   RS_PREFIX_MY,
   RS_PREFIX_OPP,
   RS_PREFIX_CTRL
]

RS_PREFIX_EVENTS = [
   RS_PREFIX_MY,
   RS_PREFIX_OPP,
   RS_PREFIX_ANY
]

RS_PREFIX_FILTERS = [
   RS_PREFIX_NOT
]

RS_PREFIX_BONUS = [
   RS_PREFIX_PLUS,
   RS_PREFIX_NOT
]

# Sufixes
RS_SUFFIX_PLURAL = 's'

RS_SUFFIX_TYPES = [
   RS_SUFFIX_PLURAL
]

# Keywords
RS_KW_ANY = '*'
RS_KW_ALL = 'all'

# Target keywords
RS_KW_TARGET_PLAYER   = 'player'
RS_KW_TARGET_PLAYERS  = 'players'
RS_KW_TARGET_ME       = 'me'
RS_KW_TARGET_OPP      = 'opp'
RS_KW_TARGET_THIS     = 'this'
RS_KW_TARGET_CHAR     = 'character'
RS_KW_TARGET_ACTION   = 'action'
RS_KW_TARGET_REACTION = 'reaction'
RS_KW_TARGETS = [
   RS_KW_TARGET_THIS,
   RS_KW_TARGET_PLAYER,
   RS_KW_TARGET_ME,
   RS_KW_TARGET_OPP,
   RS_KW_TARGET_CHAR,
   RS_KW_TARGET_ACTION,
   RS_KW_TARGET_REACTION,
   RS_KW_ANY
]
RS_KW_TARGET_IS_PLAYER = [
   RS_KW_TARGET_PLAYER,
   RS_KW_TARGET_PLAYERS,
   RS_KW_TARGET_ME,
   RS_KW_TARGET_OPP
]
RS_KW_PLAYERS = [
   RS_KW_TARGET_ME,
   RS_KW_TARGET_OPP
]
RS_KW_PLAYERS_LABELS = [
   'Me',
   'Opponent'
]
RS_KW_CARD_TYPES = [
   RS_KW_TARGET_CHAR,
   RS_KW_TARGET_ACTION,
   RS_KW_TARGET_REACTION
]

# Zone keywords
RS_KW_ZONE_ARENA    = 'arena'
RS_KW_ZONE_RING     = 'ring'
RS_KW_ZONE_HAND     = 'hand'
RS_KW_ZONE_DECK     = 'deck'
RS_KW_ZONE_DISCARDS = 'discards'
RS_KW_ZONE_KILL     = 'kill'
RS_KW_ZONES = [
   RS_KW_ZONE_ARENA,
   RS_KW_ZONE_RING,
   RS_KW_ZONE_HAND,
   RS_KW_ZONE_DECK,
   RS_KW_ZONE_DISCARDS,
   RS_KW_ZONE_KILL
]

RS_KW_TARGET_ZONES = [
   RS_KW_ZONE_ARENA,
   RS_KW_ZONE_RING,
   RS_KW_ZONE_HAND
]

RS_KW_ZONES_PILES = [
   RS_KW_ZONE_HAND,
   RS_KW_ZONE_DECK,
   RS_KW_ZONE_DISCARDS,
   RS_KW_ZONE_KILL
]

# Cost keywords
RS_KW_COST_FREEZE    = 'f'
RS_KW_COST_SACRIFICE = 's'
RS_KW_COST_DISCARD   = 'd'
RS_KW_COST_EXILE     = 'e'

# Effect conditions
RS_KW_COND_MAY = 'may'
RS_KW_COND_IF  = 'if'
RS_KW_CMD_COND = [
   RS_KW_COND_MAY,
   RS_KW_COND_IF
]

# Effect restrictions
RS_KW_RESTR_UEOT = 'ueot'
RS_KW_RESTR_UYNT = 'uynt'
RS_KW_CMD_RESTRS = [
   RS_KW_RESTR_UEOT,
   RS_KW_RESTR_UYNT
]
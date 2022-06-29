# Python Scripts for the Card Fighters" Clash definition for OCTGN
# Copyright (C) 2013 Raohmaru

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
# RULESCRIPT CONST LANGUAGE DEFINITION
#---------------------------------------------------------------------------

RS_VERSION = "0.9.9"

# Available keys
RS_KEY_TARGET    = "target"
RS_KEY_ACTION    = "action"
RS_KEY_ABILITIES = "abilities"
RS_KEY_AUTO      = "auto"
RS_KEY_REQ       = "requisite"
RS_KEY_VARS      = "vars"
RS_KEY_LABEL     = "label"

# Regular expressions
RS_RGX_KEY_TARGET     = re.compile(r"^target\??\s*=\s*")
RS_RGX_TARGET_TYPE    = re.compile(r"@|\[")
RS_RGX_TARGET_FILTERS = re.compile(r"\[(.+)\]")
RS_RGX_TARGET_FPARAM  = re.compile(r"(\w+)\s*([=><:]+)\s*([\w\-]+)")
RS_RGX_TARGET_ZONE    = re.compile(r"@\s*([\w*]+).*$")
RS_RGX_TARGET_PICK    = re.compile(r"<\s*((?:\+|\-)?\s*[0-9]+)\s*>")
RS_RGX_TARGET_QTY     = re.compile(r"^<\s*((?:\*\*)|(?:r\d*)|(?:,?[0-9]+){1,2})\s*>")
RS_RGX_KEY_SELECTOR   = re.compile(r"::(\w+)\((.+)\)?$")

RS_RGX_KEY_ACTION     = re.compile(r"^action\s*=\s*")
RS_RGX_AC_COST        = re.compile(r"(\{.+\}\s*)\s*:\s*")
RS_RGX_AC_EVENT       = re.compile(r"^(?:\?|~)\s*([\w, :]+)\s*(?:\?|~)")
RS_RGX_AC_TARGET      = re.compile(r"\b(?:to|target|from)(\??)\s*\(([^)]+)\)")
RS_RGX_AC_EFFECT      = re.compile(r"([\w]+\??)\s*\((.*?)\)$")
RS_RGX_AC_ARGS_SEP    = re.compile(r"(?<!<\d),(?!\d>)")

RS_RGX_KEY_ABILITY    = re.compile(r"^abilities\s*=\s*")
RS_RGX_KEY_AUTO       = re.compile(r"^auto\s*=\s*")
RS_RGX_KEY_REQ        = re.compile(r"^requisite\s*=\s*")
RS_RGX_KEY_VARS       = re.compile(r"^vars\s*=\s*")
RS_RGX_KEY_LABEL      = re.compile(r"^label\s*=\s*")

RS_RGX_PARAM          = re.compile(r"\(([^)]*)\)")
RS_RGX_COND           = re.compile(r"\[\[([^\]]+)\]\]\s*")
RS_RGX_UUID           = re.compile(r"[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12}")

# Comments
RS_COMMENT_CHAR = "#"

# Keywords
RS_KW_ANY    = "*"
RS_KW_ANYNUM = "**"
RS_KW_ALL    = "all"
RS_KW_NAME   = '"'
RS_KW_RANDOM = "r"
RS_KW_ARROW  = "=>"

# Operators
RS_OP_OR       = ","
RS_OP_AND      = "&"
RS_OP_SEP      = ";"
RS_OP_EQUAL    = "="
RS_OP_LTE      = "<="
RS_OP_GTE      = ">="
RS_OP_BOOL_AND = "&&"
RS_OP_BOOL_OR  = "||"
RS_OP_OPT      = "?"
RS_OP_SELECTOR = ":"
RS_OP_ASSIGN   = ":="

RS_TARGET_OPS = [
   RS_OP_AND,
   RS_OP_OR
]

# Prefixes
RS_PREFIX_PLUS  = "+"
RS_PREFIX_MINUS = "-"
RS_PREFIX_MY    = "my"
RS_PREFIX_ME    = "me."
RS_PREFIX_OPP   = "opp"
RS_PREFIX_OPPE  = "opp."
RS_PREFIX_CTRL  = "ctrl"
RS_PREFIX_ANY   = "any"
RS_PREFIX_OTHER = "^"
RS_PREFIX_NOT   = "!"
RS_PREFIX_SAME  = "same"

RS_PREFIX_TYPES = [
   RS_PREFIX_OTHER,
   RS_PREFIX_NOT
]

RS_PREFIX_ZONES = [
   RS_PREFIX_MY,
   RS_PREFIX_OPP,
   RS_PREFIX_CTRL,
   RS_PREFIX_SAME,
   RS_PREFIX_ANY
]

RS_PREFIX_EVENTS = [
   RS_PREFIX_MY,
   RS_PREFIX_ME,
   RS_PREFIX_OPP,
   RS_PREFIX_OPPE,
   RS_PREFIX_ANY
]

RS_PREFIX_FILTERS = [
   RS_PREFIX_PLUS,
   RS_PREFIX_MINUS,
   RS_PREFIX_OTHER
]

RS_PREFIX_BONUS = [
   RS_PREFIX_PLUS,
   RS_PREFIX_MINUS
]

RS_PREFIX_RESTR = [
   RS_PREFIX_MY,
   RS_PREFIX_OPP
]

# Suffixes
RS_SUFFIX_PLURAL    = "s"
RS_SUFFIX_FROM_THIS = "fromthis"
RS_SUFFIX_THIS      = "this"
RS_SUFFIX_ANY       = "any"
RS_SUFFIX_ONCE      = "once"

RS_SUFFIX_TYPES = [
   RS_SUFFIX_PLURAL
]

RS_SUFFIX_EVENTS = [
   RS_SUFFIX_FROM_THIS,
   RS_SUFFIX_THIS,
   RS_SUFFIX_ANY,
   RS_SUFFIX_ONCE
]

# Target keywords
RS_KW_TARGET_PLAYER    = "player"
RS_KW_TARGET_PLAYERS   = "players"
RS_KW_TARGET_ME        = "me"
RS_KW_TARGET_OPP       = "opp"
RS_KW_TARGET_THIS      = "this"
RS_KW_TARGET_CHARACTER = "character"
RS_KW_TARGET_ACTION    = "action"
RS_KW_TARGET_REACTION  = "reaction"
RS_KW_TARGETS = [
   RS_KW_TARGET_THIS,
   RS_KW_TARGET_PLAYER,
   RS_KW_TARGET_ME,
   RS_KW_TARGET_OPP,
   RS_KW_TARGET_CHARACTER,
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
   "Me",
   "Enemy"
]
RS_KW_CARD_TYPES = [
   RS_KW_TARGET_CHARACTER,
   RS_KW_TARGET_ACTION,
   RS_KW_TARGET_REACTION
]

# Zone keywords
RS_KW_ZONE_ARENA    = "arena"
RS_KW_ZONE_RING     = "ring"
RS_KW_ZONE_INFRONT  = "infront"
RS_KW_ZONE_HAND     = "hand"
RS_KW_ZONE_DECK     = "deck"
RS_KW_ZONE_DISCARDS = "discards"
RS_KW_ZONE_REMOVED  = "removed"
RS_KW_ZONES = [
   RS_KW_ZONE_ARENA,
   RS_KW_ZONE_RING,
   RS_KW_ZONE_INFRONT,
   RS_KW_ZONE_HAND,
   RS_KW_ZONE_DECK,
   RS_KW_ZONE_DISCARDS,
   RS_KW_ZONE_REMOVED
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
   RS_KW_ZONE_REMOVED
]

# Cost keywords
RS_KW_COST_FREEZE    = "f"
RS_KW_COST_SACRIFICE = "s"
RS_KW_COST_DISCARD   = "d"
RS_KW_COST_EXILE     = "e"

# Effect conditions
RS_KW_COND_MAY   = "may"
RS_KW_COND_IF    = "if"
RS_KW_COND_ELIF  = "elif"
RS_KW_COND_ELSE  = "else"
RS_KW_CMD_COND = [
   RS_KW_COND_MAY,
   RS_KW_COND_IF
]

RS_KW_CMD_COND_SUB = [
   RS_KW_COND_ELIF,
   RS_KW_COND_ELSE
]

# Effect restrictions
RS_KW_RESTR_UEOT = "ueot"
RS_KW_RESTR_UYNT = "uynt"
RS_KW_RESTR_UNAC = "unac"  # Until Next Action Card
RS_KW_CMD_RESTRS = [
   RS_KW_RESTR_UEOT,
   RS_KW_RESTR_UYNT,
   RS_KW_RESTR_UNAC
]

RS_KW_RESTRS_CLEANUP = [
   RS_KW_RESTR_UEOT,
   RS_KW_RESTR_UNAC
]

# Effect modes
RS_MODE_EQUAL = "="
RS_MODE_MULT = "x"
RS_MODES = [
   RS_MODE_EQUAL,
   RS_MODE_MULT
]
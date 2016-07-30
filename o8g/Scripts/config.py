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


# Helper class to convert a dict to an object (to be accesed with dot notation)
# http://stackoverflow.com/questions/1305532/convert-python-dict-to-object
class Struct:
   def __init__(self, **entries): 
      self.__dict__.update(entries)

#---------------------------------------------------------------------------
# Constants
#---------------------------------------------------------------------------
import re

# Phases
Phases = [
   '\n=== PRE-GAME SETUP Phase: {} ==='.format(me),
   "\n=== ACTIVATE Phase: {} ===",
   "\n=== DRAW Phase: {} ===",
   "\n=== MAIN Phase: {} ===",
   "\n=== ATTACK Phase: {} ===",
   "\n=== COUNTERATTACK Phase: {} ===",
   "\n=== END Phase: {} ===",
   "\n=== CLEANUP Phase: {} ==="
]
SetupPhase    = 0
ActivatePhase = 1
DrawPhase     = 2
MainPhase     = 3
AttackPhase   = 4
BlockPhase    = 5
EndPhase      = 6
CleanupPhase  = 7

# Highlight Colours
AttackColor         = "#ff0000"
AttackNoFreezeColor = "#ff8000"
UnitedAttackColor   = "#ff42de"
BlockColor          = "#ffff00"
ActivatedColor      = "#0000ff"
DoesntUnfreezeColor = "#000000"

# Dictionaries which hold all the hard coded markers and tokens (in the markers & tokens set)
MarkersDict = {
   'BP'            : ("BP",               "b86fc644-d084-43d3-99d2-5b11457321cc"),
   'JustEntered'   : ("Just entered",     "9a52c42c-543f-48bb-9a48-d7599d6c8fae"),
   'Attack'        : ("Attack",           "023406a3-417c-473d-bc23-481290755a4a"),
   'UnitedAttack'  : ("United Attack",    "88036e2b-6a1f-40be-a941-988b27c405ba"),
   'CounterAttack' : ("Counter-attack",   "2fd7dc74-4149-469d-9bde-53e94b99b934"),
   'DoesntUnfreeze': ("Doesn't Unfreeze", "5231f83b-b78e-48b3-8bce-62031c022bf4"),
   'NoFreeze'      : ("No Freeze",        "fec1976b-9ce5-4b32-8c07-76eadc5607f6"),
   'Backup'        : ("Backup",           "efd3208d-2ec3-44ca-be1d-858e91628da4")
}
TokensDict = {}

# A table holding tuples with the location for the cards according its states
CardsCoords = dict(
   #                x     y
   Slot0         = (-311, 198),
   Slot1         = (-134, 198),
   Slot2         = ( 44,  198),
   Slot3         = ( 221, 198),
   Attack0       = (-311, 29),
   Attack1       = (-134, 29),
   Attack2       = ( 44,  29),
   Attack3       = ( 221, 29),
   BackupOffset  = ( 0,   13),
   UAttackOffset = ( 38,  0)
)

# Card types
CharType     = 'Character'
ActionType   = 'Action'
ReactionType = 'Reaction'

# Card abilities
InstantAbility   = u'\xa2'
ActivatedAbility = u'\xa3'
AutoAbility      = u'\xa4'

InstantUniChar   = u'\u25B2'
ActivatedUniChar = u'\u25A0'
AutoUniChar      = u'\u25CF'

# A dictionary which holds the regex used in other scripts
Regexps = dict(
   Ability = re.compile(r'(.)\s+([^\r]+)')
)

# Rules
NumSlots        = 4
CharsPerTurn    = 1
BackupsPerTurn  = 1
BackupRaiseBP   = 3
MaxCharsUAttack = 2
UAttackCost     = 5
MaxCardCopies   = 3
HandSize        = 5

# Debug
DebugLevel = Struct(**{
   'Off'    : -1,
   'Info'   : 0,
   'Debug'  : 1,
   'Warning': 2,
   'Error'  : 3,
   'All'    : 4
})
DebugLevelPrefixes = [
   '[i]',
   '[#]=>',
   '[!]==>',
   '[?]===>',
   '[x]====>'
]

# Errors
ERR_CANT_PAY_SP         = '400'
ERR_NO_CARDS            = '401'
ERR_NO_FILTERED_CARDS   = '402'
ERR_NO_FILTERED_PLAYERS = '403'
ERR_NO_CARD_TARGETED    = '404'
ERR_TARGET_OTHER        = '405'
ERR_MULTIPLE_TARGET     = '406'
ERR_EXTAPI_DISABLED     = '407'

ErrStrings = {}
ErrStrings[ERR_NO_CARDS] = "There are no cards to select."
ErrStrings[ERR_NO_FILTERED_CARDS] = "Selected cards don't match the requeriments of this card's effect."
ErrStrings[ERR_NO_FILTERED_PLAYERS] = "No player match the requeriments of this card's effect."
ErrStrings[ERR_NO_CARD_TARGETED] = "Please select a card."
ErrStrings[ERR_TARGET_OTHER] = "Please select a card other than the card you're activating its effect."
ErrStrings[ERR_MULTIPLE_TARGET] = "Please select only one card."

# Messages
MSG_SEL_CHAR_RING = "Please select a character in your ring.\n(Shift key + Left click on a character)."

# Misc
CardWidth    = 90
CardHeight   = 126
Xaxis        = 'x'
Yaxis        = 'y'
PlayAction   = 'play'
BackupAction = 'backup'
Author       = 'raohmaru'

#---------------------------------------------------------------------------
# Global variables (fo the current user)
#---------------------------------------------------------------------------

playerSide     = None  # Variable to keep track on which side each player is
playerAxis     = None  # Variable to keep track on which axis the player is
handSize       = HandSize
charsPlayed    = 0  # Num of chars played this turn
backupsPlayed  = 0  # Num of chars backed-up this turn
debugVerbosity = -1 # -1..4 (At -1 means no debugging messages display)
parsedCards    = {} # Dictionary holding all parsed cards
transfCards    = {} # Dictionary holding all transformed cards

automations = {
   'Play'     : True, # Automatically trigger game effetcs and card effects when playing cards
   'Phase'    : True, # Automatically trigger phase related events, and effects from cards in play
   'WinForms' : True, # Game will use the custom Windows Forms for displaying info pop-ups
   'AttackDmg': True, # Applies attack damage automatically
   'ExtAPI'   : True  # Make use of the extended API to access the C# API
}

# Default values used in dialogs that can be overriden by the user to remember his last input
defProphecyCount = 1
defTrashCount    = 1
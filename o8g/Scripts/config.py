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
   # Called when the attribute does not exist
   def __getattr__(self, name):
      # debug(name)
      return None
   # Because of the previous method, all of the following are needed or errors will raise
   def __repr__(self):
      return str(self.__dict__)
   def __str__(self):
      return str(self.__dict__)
   def __format__(self, format_spec):
      return format(str(self), format_spec)
   def __eq__(self, other):
      return self.__dict__ == other
   def __nonzero__(self):
      return True

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
CannotUnfreeze = "#000000"
InfoColor           = "#00ff00"

# Dictionaries which hold all the hard coded markers and tokens (in the markers & tokens set)
MarkersDict = {
   "BP"             : ("BP",             "b86fc644-d084-43d3-99d2-5b11457321cc"),
   "Just Entered"   : ("Just Entered",   "9a52c42c-543f-48bb-9a48-d7599d6c8fae"),
   "Attack"         : ("Attack",         "023406a3-417c-473d-bc23-481290755a4a"),
   "United Attack"  : ("United Attack",  "88036e2b-6a1f-40be-a941-988b27c405ba"),
   "Counter-attack" : ("Counter-attack", "2fd7dc74-4149-469d-9bde-53e94b99b934"),
   "Cannot Unfreeze"    : ("Cannot Unfreeze",    "5231f83b-b78e-48b3-8bce-62031c022bf4"),
   "Unfreezable"    : ("Unfreezable",    "fec1976b-9ce5-4b32-8c07-76eadc5607f6"),
   "Backup"         : ("Backup",         "efd3208d-2ec3-44ca-be1d-858e91628da4"),
   "Pierce"         : ("Pierce",         "3131facc-3fe4-4dd5-95ff-afc08570d869"),
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
InstantAbility = u'\xa2'
TriggerAbility = u'\xa3'
AutoAbility    = u'\xa4'

InstantUniChar   = u'\u25B2'
TriggerUniChar = u'\u2588'
AutoUniChar      = u'\u25CF'

# A dictionary which holds the regex used in other scripts
Regexps = dict(
   Ability  = re.compile(r'(.)\s+([^\r]+)'),
   LeftCond = re.compile(r'^[\w.]+'),
   BP       = re.compile(r'(\w+)\.bp'),
   Action   = re.compile(r'\baction\b'),
   HandSize = re.compile(r'(\w+)\.hand\.size'),
   Ring     = re.compile(r'(\w+)\.ring'),
   Chars    = re.compile(r'(\w+)\.chars')
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

GameRulesDefaults = {
   'ab_trigger_fresh': False, # Activate [] abilities of fresh characters
   'ab_trigger_act'  : True,  # Activate [] abilities
   'ab_instant_act'  : True,  # Activate /\ abilities
   'piercing'        : True
}

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

# Hooks
Hooks = Struct(**{
   'CanBeBlocked' : 'canbeblocked',
   'BeforeBlock'  : 'beforeblock',
   'BeforePlayAC' : 'beforeplayac',
   'BeforePlayRE' : 'beforeplayre',
   'BackupLimit'  : 'backuplimit',
   'PreventPierce': 'preventpierce'
})

# Game Events
GameEvents = Struct(**{
   'ActivatePhase': 'activatephase',
   'DrawPhase'    : 'drawphase',
   'BlockPhase'   : 'blockphase',
   'EndPhase'     : 'endphase',
   'CleanupPhase' : 'cleanupphase',
   'HandChanges'  : 'handchanges',
   'RingChanges'  : 'ringchanges',
   'Removed'      : 'removed',
   'Powerless'    : 'powerless',
   'CombatDamaged': 'combatdamaged',
   'Blocked'      : 'blocked',
   'Attacks'      : 'attacks'
})
# When a listener to these events is added, trigger it automatically
GameEventsExecOnAdded = [
   GameEvents.HandChanges
]
# Maps variables to events
GameEventsFromVars = {
   'hand.size': GameEvents.HandChanges
}

# Events that should not trigger for chars in a UA
GameEventsDisabledUA = [
   GameEvents.EndPhase,
   GameEvents.CleanupPhase,
   GameEvents.CombatDamaged
]

# Messages
MSG_SEL_CHAR_RING           = "Please select a character in your ring.\n(Shift key + Left click on a character)."
MSG_SEL_CARD                = "Select {} card(s) from {} {}"
MSG_SEL_CARD_EFFECT         = MSG_SEL_CARD + " ({}'s effect)"
MSG_SEL_CARD_DISCARD        = "Select a card from your {} to discard"
MSG_SEL_CARD_SACRIFICE      = "Select a card from your {} to KO"
MSG_PLAYER_LOOKS            = "{} is looking into {} {}..."
MSG_PLAYER_SELECTS          = "{} has selected {} card(s)"
MSG_COST_NOT_PAYED          = "{} did not pay the activation cost of {}'s {}"
MSG_AB_NO_EFFECT            = "{}'s ability {} (may) have had no effect."
MSG_AB_AUTO_ACTIVATION      = "{} has activated {}'s auto ability {}."
MSG_AB_AUTO_UATTACK         = "Cannot activate {}'s auto ability {} because it joined an United Attack."
MSG_AB_MISS_REQ             = u"\u2192 There aren't enough targets to activate {}'s ability."
MSG_DISCARD_RANDOM          = "{} randomly discards {} from its {}."
MSG_ERR_NO_CARDS            = "There are no targets available, hence the ability has no effect."
MSG_ERR_NO_CARDS_HAND       = "You don't have enough cards in your hand to pay the cost of the ability."
MSG_ERR_NO_FILTERED_CARDS   = "Selected cards don't match the requirements of this card's effect."
MSG_ERR_NO_FILTERED_PLAYERS = "No player match the requirements of this card's effect."
MSG_ERR_NO_CARD_TARGETED    = "Please select a card before activating the ability."
MSG_ERR_TARGET_OTHER        = "{}'s ability cannot select itself, therefore it has been removed from selection."
MSG_MAY_DEF                 = "Do you want to apply the effect of the card?"
MSG_ABILITIES = {
   'cantblock': [
      "{} cannot block due to {}'s {} ability{}.",
      "{} can block again."
   ],
   'unblockable': [
      "{} cannot be blocked due to {}'s {} ability{}.",
      "{} can be blocked as normal."
   ],
   'cantplayac': [
      "{} cannot play action cards due to {}'s {} ability{}.",
      "{} can play action cards again."
   ],
   'cantplayre': [
      "{} cannot play reaction cards due to {}'s {} ability{}.",
      "{} can play reaction cards again."
   ],
   'unlimitedbackup': [
      "{0} can receive any number of back-ups {3}."
   ],
   'preventpierce': [
      "Piercing damage was prevented by {0}'s {2} ability."
   ]
}
MSG_RULES = {
   'ab_trigger_fresh': (
      'Characters cannot use {} abilities the turn they enter the ring.'.format(TriggerUniChar),  # Disabled
      'Characters can use {} abilities the turn they enter the ring.'.format(TriggerUniChar)  # Enabled
   ),
   'ab_trigger_act': (
      TriggerUniChar + " abilites cannot be activated.",
      TriggerUniChar + " abilites can be activated again."
   ),
   'ab_instant_act': (
      InstantUniChar + " abilites cannot be activated.",
      InstantUniChar + " abilites can be activated again."
   ),
   'card_cost': '{} cards now cost {} SP {} to play.',
   'piercing': (
      'Whenever a character counter-attacks a United Attack, piercing damage is prevented.',  # Disabled
      'United-Attacks deals piercing damage as normal.'  # Enabled
   ),
}
ERR_NO_EFFECT = 'err001'
CMD_LABELS = {
   'swapchars' : 'Swap the positions of two characters in the same ring',
   'movetoslot': 'Move a character to an empty slot in the same ring'
}

# Misc
CardWidth    = 90
CardHeight   = 126
Xaxis        = 'x'
Yaxis        = 'y'
PlayAction   = 'play'
BackupAction = 'backup'
Author       = 'raohmaru'
BPMultiplier = 100  # Model.BP = markers.BP * BPMultiplier

#---------------------------------------------------------------------------
# Global variables (for the current user)
#---------------------------------------------------------------------------

playerSide     = None  # Variable to keep track on which side each player is
playerAxis     = None  # Variable to keep track on which axis the player is
handSize       = HandSize
charsPlayed    = 0  # Number of chars played this turn
backupsPlayed  = 0  # Number of chars backed-up this turn
debugVerbosity = DebugLevel.Off # -1..4 (At -1 means no debugging messages display)
debugging      = False
# If I am alone debugging I want to know everything
if me.name == Author and len(players) == 1:
   debugVerbosity = DebugLevel.All
parsedCards    = {} # Dictionary holding all parsed cards
cleanedUpRing  = False  # Tracks if the user has run the Clean-up phase
commander      = None  # RulesCommands instance
actionLocals   = dict()  # Variables used during action execution

automations = {
   'Play'     : True, # Automatically trigger game effects and card effects when playing cards
   'Phase'    : True, # Automatically trigger phase related events, and effects from cards in play
   'WinForms' : True, # Game will use the custom Windows Forms for displaying info pop-ups
   'AttackDmg': True, # Applies attack damage automatically
   'ExtAPI'   : True  # Make use of the extended API to access the C# API
}

# Default values used in dialogs that can be overridden by the user to remember his last input
defProphecyCount = 3
defTrashCount    = 1

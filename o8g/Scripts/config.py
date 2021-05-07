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
# Helpers
#---------------------------------------------------------------------------

# Helper class to convert a dict to an object (to be accessed with dot notation)
# http://stackoverflow.com/questions/1305532/convert-python-dict-to-object
class Struct:
   def __init__(self, **entries): 
      self.__dict__.update(entries)
   # Called when the attribute does not exist
   def __getattr__(self, name):
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
   'Setup',
   'Activate',
   'Draw',
   'Main',
   'Attack',
   'Counter-attack',
   'End',
   'Cleanup'
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
BlockColor          = "#3ec61a"
ActivatedColor      = "#0000ff"

# Filter colours
CannotUnfreezeFilter = '#6699d9ff'
JustEnteredFilter    = '#55dddd00'
KOedFilter           = '#55ff0000'

FiltersDict = {
   'Just Entered'   : JustEnteredFilter,
   'Cannot Unfreeze': CannotUnfreezeFilter
}

# Dictionary which hold all the hard coded markers and tokens (in the markers & tokens set)
MarkersDict = {
   "BP"             : ("BP",              "b86fc644-d084-43d3-99d2-5b11457321cc"),
   "Just Entered"   : ("Just Entered",    "9a52c42c-543f-48bb-9a48-d7599d6c8fae"),
   "Attack"         : ("Attack",          "023406a3-417c-473d-bc23-481290755a4a"),
   "United Attack"  : ("United Attack",   "88036e2b-6a1f-40be-a941-988b27c405ba"),
   "Counter-attack" : ("Counter-attack",  "2fd7dc74-4149-469d-9bde-53e94b99b934"),
   "Cannot Unfreeze": ("Cannot Unfreeze", "5231f83b-b78e-48b3-8bce-62031c022bf4"),
   "Unfreezable"    : ("Unfreezable",     "fec1976b-9ce5-4b32-8c07-76eadc5607f6"),
   "Backup"         : ("Backup",          "efd3208d-2ec3-44ca-be1d-858e91628da4"),
   "Pierce"         : ("Pierce",          "3131facc-3fe4-4dd5-95ff-afc08570d869")
}

Buttons = {
   "StartButton": "81918f9c-83cc-4589-8b86-19a238a0623b",
   "NextButton": "1d0c798b-b785-4bb6-b160-14c71db6af47"
}

# A table holding tuples with the location for the cards according its states
CardsCoords = dict(
   #                x      y
   Slot0         = (-311,  209),
   Slot1         = (-134,  209),
   Slot2         = ( 44,   209),
   Slot3         = ( 221,  209),
   Attack0       = (-311,  39),
   Attack1       = (-134,  39),
   Attack2       = ( 44,   39),
   Attack3       = ( 221,  39),
   BackupOffset  = ( 0,    13),
   UAttackOffset = ( 43,   0),
   Action        = ( 0,    -49),
   StartButton   = ( -385, 30),
   NextButton    = ( 387,  244),
   Avatar        = ( 0,    375),
)

# Card types
CharType     = 'Character'
ActionType   = 'Action'
ReactionType = 'Reaction'
ButtonType   = 'Button'
AvatarType   = 'Avatar'

# Card abilities
InstantAbility = u'\xa2'
TriggerAbility = u'\xa3'
AutoAbility    = u'\xa4'

InstantUniChar = u'\u25B2'
TriggerUniChar = u'\u2588'
AutoUniChar    = u'\u26AB'

# A dictionary that holds the regex used in other scripts
Regexps = {
   'ability'   : re.compile(r'(.)\s+([^\r]+)'),
   'leftcond'  : re.compile(r'^[\w.]+'),
   '.bp'       : re.compile(r'([\w\d\[\]]+)\.bp'),
   '.sp'       : re.compile(r'([\w\d\[\]]+)\.sp'),
   '.lastbp'   : re.compile(r'([\w\d\[\]]+)\.lastbp'),
   'action'    : re.compile(r'\baction\b'),
   'reaction'  : re.compile(r'\breaction\b'),
   'char'      : re.compile(r'\bchar\b'),
   '.size'     : re.compile(r'([\w.]+)\.size'),
   '.ring'     : re.compile(r'(\w+)\.ring'),
   '.ring.size': re.compile(r'(\w+)\.ring\.size'),
   '.chars'    : re.compile(r'(\w+)\.chars'),
   '.damaged'  : re.compile(r'(\w+)\.damaged'),
   '.lostsp'   : re.compile(r'(\w+)\.lostsp'),
   'opp'       : re.compile(r'\bopp\b'),
   'listIdx'   : re.compile(r'([\w\d])\.(\d)\b'),
   'cardid'    : re.compile(r'\{#(\d+)\}')
}

# Misc
CardWidth    = 90
CardHeight   = 126
Xaxis        = 'x'
Yaxis        = 'y'
PlayAction   = 'play'
BackupAction = 'backup'
Author       = 'raohmaru'
GameId       = 'e3d56d9e-900d-49c6-b6ae-22cbb51be153'
Website      = 'https://cardfightersclash.wordpress.com'
# _extapi is not ready yet
# ButtonSize = _extapi.game.CardSizes["button"].Width
ButtonSize   = 58
AvatarWidth  = 292
AvatarHeight = 40

# Rules
NumSlots        = 4
CharsPerTurn    = 1
BackupsPerTurn  = 1
BackupRaiseBP   = 300
MaxCharsUAttack = 2
UAttackCost     = 5
MaxCardCopies   = 3
HandSize        = 5
StartingHP      = 3000
DeckSize        = 50

GameRulesDefaults = {
   'ab_trigger_fresh'  : False, # Activate [] abilities of fresh characters
   'ab_trigger_act'    : True,  # Activate [] abilities
   'ab_instant_act'    : True,  # Activate /\ abilities
   'piercing'          : True,  # Allow piercing damage
   'backup_fresh'      : False, # Backup fresh characters
   'play_char_bp_limit': None,  # BP limit to play chars
   'dmg_combat_deal'   : True,  # Deal combat damage
   'attack_freeze'     : True,  # Characters freeze after a attack
   'attack'            : True,  # Characters can attack
   'backup_limit'      : True,  # Limit the number of backups per turn
   'play_removed'      : False  # Play cards from removed pile
}

# Debug
DebugLevel = {
   'Off'    : 0,
   'Debug'  : 1
}

# Hooks
Hooks = Struct(**{
   'BeforeAttack'      : 'beforeattack',
   'BeforeBlock'       : 'beforeblock',
   'BeforePlayAC'      : 'beforeplayac',
   'BeforePlayRE'      : 'beforeplayre',
   'BackupLimit'       : 'backuplimit',
   'PreventPierce'     : 'preventpierce',
   'CallOnRemove'      : 'callonremove',
   'PlayAsFresh'       : 'playasfresh',
   'CanBeBlocked'      : 'canblock',
   'CancelCombatDamage': 'cancelcombatdamage'
})

# Game Events
GameEvents = Struct(**{
   'ActivatePhase'      : 'activatephase',
   'DrawPhase'          : 'drawphase',
   'BlockPhase'         : 'blockphase',
   'EndPhase'           : 'endphase',
   'CleanupPhase'       : 'cleanupphase',
   'HandChanges'        : 'handchanges',
   'RingChanges'        : 'ringchanges',
   'Removed'            : 'removed',
   'Powerless'          : 'powerless',
   'BeforeDamage'       : 'beforedamage',
   'PlayerCombatDamaged': 'playercombatdamaged',
   'Attacks'            : 'attacks',
   'Blocks'             : 'blocks',
   'Blocked'            : 'blocked',
   'BackedUp'           : 'backedup',
   'BeforePayCost'      : 'beforepaycost'  # Used with suffixes 'action' or 'reaction'
})

# Maps variables to events
GameEventsFromVars = {
   'hand.size': GameEvents.HandChanges
}

#---------------------------------------------------------------------------
# Global variables (for the current user)
#---------------------------------------------------------------------------

playerSide     = None  # The side of the player (top: -1, bottom: 1)
handSize       = HandSize
parsedCards    = {} # Dictionary holding all parsed cards
cleanedUpRing  = False  # Tracks if the user has run the Clean-up phase
commander      = None  # RulesCommands instance
turns          = 1  # The number of consecutive turns a player can play
envVars        = None  # Global variables to be used in eval() expression
buttons        = {}  # Holds the UI buttons created
transformed    = {}  # Transformed cards
phaseOngoing   = False  # True while running phase automation tasks
Globals        = {}  # Replaces OCTGN global variables
PlayerGlobals  = {}  # Replaces OCTGN player global variables
debugVerbosity = DebugLevel['Off']
debugging      = False
# If I am alone debugging I want to know EVERYTHING
# if me.name == Author and len(players) == 1:
   # debugVerbosity = DebugLevel['Debug']

settings = {
   'Play'         : True, # Trigger game, event and card effects
   'Phase'        : True, # Automatic phase advancement
   'Activate'     : True, # Automatic activate /\ abilites and Action and Reaction
   'WinForms'     : True, # Use custom Windows Forms for displaying info pop-ups
   'Sounds'       : True, # Play sound effect
   'WelcomeScreen': True, # Show welcome screen
   'ExtAPI'       : True, # Make use of the extended API to access the C# API
   'GameVersion'  : '0.0.0', # Last version shown in the changelog window
   'Avatar'       : None  # Player's avatar
}

# Default values used in dialogs that can be overridden by the user to remember his last input
defProphecyCount = 3
defTrashCount    = 1

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

ERR_NO_EFFECT = "err001"

MSG_PHASES = [
   u"\u2E3B Setup Phase: {} \u2E3B"
]

MSG_SEL_HOW_TO              = "Shift key + Left click on a character card to select it"
MSG_SEL_CHAR_RING           = "Please select a character in your ring.\n({}).".format(MSG_SEL_HOW_TO)
MSG_SEL_CARD                = "Select {} card{} from {} {}"
MSG_SEL_CARD_EFFECT         = MSG_SEL_CARD + " ({}'s effect)"
MSG_SEL_CARD_DISCARD        = MSG_SEL_CARD + " to discard"
MSG_SEL_CARD_SACRIFICE      = MSG_SEL_CARD + " to KO"

MSG_PLAYER_LOOKS            = "{} is looking into {} {}..."
MSG_PLAYER_SELECTS          = "{} has selected {} card(s)"
MSG_PLAYER_SELECTS_NAMED    = "{} selects {}"
MSG_PLAYER_SELECTS_NONE     = "{} did not selected any card from {} {}."

MSG_COST_NOT_PAYED          = "{} did not pay the activation cost of {}'s {}"

MSG_AB_AUTO_TRIGGER         = "Event \"{}\" triggered. Now trying to activate {}'s effect."
MSG_AB_AUTO_TRIGGER_CHAR    = "Event \"{}\" triggered. Now trying to activate {}'s auto ability from {}'s {}."
MSG_AB_AUTO_ACT             = "{} has activated {}'s effect"
MSG_AB_AUTO_ACT_CHAR        = "{} has activated {}'s auto ability {}."
MSG_AB_AUTO_UATTACK         = "Cannot activate {}'s auto ability {} because it joined an United Attack."
MSG_AB_MISS_REQ             = "There aren't enough targets to activate {}'s ability."

MSG_DISCARD_RANDOM          = "{} randomly discards {} from their {}."

MSG_HINT_KOED               = "{} has been KOed. You should put it into your Discard pile. In any case, KOed characters will be removed from the ring on phase change."
MSG_HINT_ACTIVATE           = "Now you must activate the card's effect by double-click on it."
MSG_HINT_ATTACK             = "You can attack with your characters or finish your turn."
MSG_HINT_WIN                = "{} wins the game!"
MSG_HINT_BLOCK1             = "Now {} can play Reaction cards and then {} may choose if block attackers with their characters."
MSG_HINT_BLOCK2             = "When done, press TAB key or click in the \"Next\" button to return priority to attacking player."

MSG_UA_MAX                  = "Cannot be more than {} characters in a United Attack."

MSG_PHASE_DONE              = "{} has finalized the {} phase. {} can go to the next phase."
MSG_PHASE_LOCK              = "You cannot go to the next phase until {} is done."

MSG_ACTION_LOAD_DECK        = "Please load a deck first."
MSG_ACTION_ATTACK           = "{} attacks with {}"
MSG_ACTION_ATTACK_NOFREEZE  = MSG_ACTION_ATTACK + " (character will not freeze)."
MSG_ACTION_MOVE_ALL_CARDS   = "{} moves all cards from their {} to {}."
MSG_ACTION_FACE_DOWN        = "{} puts a card face down in the Arena {}"

MSG_Q_MAY                   = "Do you want to apply the effect of the card?"
MSG_Q_HEAD_TAILS            = "Call heads or tails"

MSG_ERR_NO_CARDS            = "There are no targets available, hence the ability has no effect."
MSG_ERR_NO_CARDS_HAND       = "You don't have enough cards in your hand to pay the cost of the ability."
MSG_ERR_NO_CARDS_DISCARD    = "There are no cards to discard in {}'s hand."
MSG_ERR_NO_CARDS_DISCARD_F  = "There are no cards to discard (of the chosen type) in {}'s hand."
MSG_ERR_NO_FILTERED_CARDS   = "Selected cards don't match the requirements of this card's effect."
MSG_ERR_NO_FILTERED_PLAYERS = "No player match the requirements of this card's effect."
MSG_ERR_TARGET_OTHER        = "{}'s ability cannot select itself, therefore it has been removed from selection."
MSG_ERR_ATTACK_CHAR_RING    = "Please attack with a character in your ring."
MSG_ERR_ATTACK_FRESH        = "Characters that just entered the ring can't attack this turn."
MSG_ERR_CANNOT_ATTACK       = "{} cannot attack due to an ability or effect."
MSG_ERR_BLOCK_ONE           = "An attacking character can only be blocked by exactly one character."
MSG_ERR_DRAW_EMPTY_PILE     = "You can't draw cards from an empty {}."
MSG_ERR_NO_EMPTY_SLOTS      = "There aren't empty slots in your ring where to play a character card."
MSG_ERR_NO_SP               = "You do not have enough SP to {}.\n(Cost is {} SP.)"
MSG_ERR_PLAY_CHARLIMIT      = "Only {} character card{} per turn can be played.\n(You have played {} character{} this turn.)"
MSG_ERR_PLAY_SLOTNOTEMPTY   = "Character card can't be played, slot {} is not empty (it's taken up by {}).\nIf you want to do a backup, please first target a character in your ring."
MSG_ERR_PLAY_ACNOTMAIN      = "Action cards can only be played in your Main Phase."
MSG_ERR_PLAY_RENOTENEMYCA   = "Reaction cards can only be played in enemy's Counter-attack Phase."
MSG_HOOKS_ERR = {
   Hooks.BeforeAttack: "{} cannot attack due to {}'s {} ability{}.",
   Hooks.BeforeBlock : "{} cannot counter-attack due to {}'s {} ability{}.",
   Hooks.CanBeBlocked: "{} cannot be counter-attacked due to {}'s {} ability{}.",
   Hooks.BeforePlayAC: "{} cannot play action cards due to {}'s {} ability{}.",
   Hooks.BeforePlayRE: "{} cannot play reaction cards due to {}'s {} ability{}."
}

MSG_AB = {
   "cantattack": [
      MSG_HOOKS_ERR[Hooks.BeforeAttack],
      "{} can attack again."
   ],
   "cantblock": [
      MSG_HOOKS_ERR[Hooks.BeforeBlock],
      "{} can counter-attack again."
   ],
   "unblockable": [
      MSG_HOOKS_ERR[Hooks.CanBeBlocked],
      "{} can be counter-attacked as normal."
   ],
   "cantplayac": [
      MSG_HOOKS_ERR[Hooks.BeforePlayAC],
      "{} can play action cards again."
   ],
   "cantplayre": [
      MSG_HOOKS_ERR[Hooks.BeforePlayRE],
      "{} can play reaction cards again."
   ],
   "unlimitedbackup": [
      "{0} can receive any number of back-ups {3}."
   ],
   "preventpierce": [
      "Piercing damage was prevented by {0}'s {2} ability."
   ],
   "unfreezable": [
      "{0} will not freeze after attacking{3}."
   ],
   "rush": [
      "{} can attack this turn due to {}'s {} ability."
   ]
}

MSG_RULES = {
   "ab_trigger_fresh": (
      "Characters cannot use {} abilities the turn they enter the ring.".format(TriggerUniChar),  # Disabled
      "Characters can use {} abilities the turn they enter the ring.".format(TriggerUniChar)  # Enabled
   ),
   "ab_trigger_act": (
      TriggerUniChar + " abilites cannot be activated.",
      TriggerUniChar + " abilites can be activated again."
   ),
   "ab_instant_act": (
      InstantUniChar + " abilites cannot be activated.",
      InstantUniChar + " abilites can be activated again."
   ),
   "card_cost": "{} cards cost {} SP {}to play{}.",
   "cost_ua2": "Double united attacks now cost {1} SP{3}.",
   "cost_ua3": "Triple united attacks now cost {1} SP{3}.",
   "piercing": (
      "Whenever a character counter-attacks a United Attack, piercing damage is prevented.",  # Disabled
      "United-Attacks deals piercing damage as normal."  # Enabled
   ),
   "backup_fresh": (
      "Characters cannot receive back-up the turn they enter the ring.",
      "Characters can receive back-up the turn they enter the ring."
   ),
   "play_char_bp_limit": (
      "Character cards of any BP can be played as normal.",
      "Character cards with BP {} or greater cannot be played."
   ),
   "dmg_combat_deal": (
      "Characters deal no combat damage{1}.",
      "Characters deal combat damage as normal."
   ),
   "attack_freeze": (
      "Characters don\'t freeze after a solo or united attack{1}.",
      "Characters will freeze after a solo or united attack."
   ),
   "attack": (
      "Characters cannot attack{1}.",
      "Characters can attack as normal."
   ),
   # Same as 'attack' but specific for a player
   "attack_player": (
      "{2}\'s characters cannot attack{1}.",
      "{2}\'s characters can attack as normal."
   ),
   "backup_limit": (
      "Players can do any number of back-ups{1}.",
      "Players can only do {} back-up per turn.".format(BackupsPerTurn)
   ),
   "play_removed": (
      "{2} cannot play cards from its Removed pile.",
      "{2} may play any card from its Removed pile{1}."
   )
}

MSG_HELP_AB = {
   InstantAbility: "It is activated when the character enters the ring.",
   TriggerAbility: "It can be activated only in your Main phase. When it is activated the character enters the freeze state.\nIt cannot be activated on frozen characters or characters that just entered the ring.",
   AutoAbility   : "It is always active as long as that character is on the ring. If the character takes part in a United Attack, the ability is nullified until the end of the turn."
}

MSG_RESTR_LABELS = {
   RS_KW_RESTR_UEOT: "until end of {}'s turn",
   RS_KW_RESTR_UYNT: "until {}'s next turn",
   RS_KW_RESTR_UNAC: "until {} plays an action card this turn"
}

CMD_LABELS = {
   "swapchars" : "Swap the positions of two characters in the same ring",
   "movetoslot": "Move a character to an empty slot in the same ring",
   "damage"    : "Deal damage",
   "hp"        : "Gain HP",
   "bp"        : "Raise the BP of characters",
   "discard"   : "Discard card(s)",
   "destroy"   : "KO character(s)",
   "shuffle"   : "Shuffle the deck"
}

ABBR = {
   "opp": "opponent"
}
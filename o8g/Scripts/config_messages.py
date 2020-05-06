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

MSG_PHASES = [
   u'\u2E3B Pre-game setup phase: {} \u2E3B'
]

MSG_SEL_CHAR_RING           = "Please select a character in your ring.\n(Shift key + Left click on a character)."
MSG_SEL_CARD                = "Select {} card{} from {} {}"
MSG_SEL_CARD_EFFECT         = MSG_SEL_CARD + " ({}'s effect)"
MSG_SEL_CARD_DISCARD        = MSG_SEL_CARD + " to discard"
MSG_SEL_CARD_SACRIFICE      = MSG_SEL_CARD + " to KO"
MSG_PLAYER_LOOKS            = "{} is looking into {} {}..."
MSG_PLAYER_SELECTS          = "{} has selected {} card(s)"
MSG_PLAYER_SELECTS_NAMED    = "{} selects {}"
MSG_COST_NOT_PAYED          = "{} did not pay the activation cost of {}'s {}"
MSG_AB_NO_EFFECT            = "{}'s ability {} (may) have had no effect."
MSG_AB_AUTO_TRIGGER         = "Event \"{}\" triggered. Now trying to activate {}'s effect."
MSG_AB_AUTO_TRIGGER_CHAR    = "Event \"{}\" triggered. Now trying to activate {}'s auto ability from {}'s {}."
MSG_AB_AUTO_ACT             = "{} has activated {}'s effect"
MSG_AB_AUTO_ACT_CHAR        = "{} has activated {}'s auto ability {}."
MSG_AB_AUTO_UATTACK         = "Cannot activate {}'s auto ability {} because it joined an United Attack."
MSG_AB_MISS_REQ             = u" \u2192 There aren't enough targets to activate {}'s ability."
MSG_DISCARD_RANDOM          = "{} randomly discards {} from their {}."
MSG_MAY_DEF                 = "Do you want to apply the effect of the card?"
MSG_HINT_KOED               = "({} has been KOed. You should put it into your discard pile. In any case, KOed characters will be removed from the ring on phase change.)"
MSG_HINT_ACTIVATE           = "(Now you must activate the card's effect by double-click on it.)"
MSG_HINT_WIN                = "{} wins the game!"
MSG_HINT_BLOCK              = "(Now {} can play Reaction cards and then {} may choose if block attackers)"
MSG_UA_MAX                  = "Can't be more than {} characters in a United Attack."

MSG_ERR_NO_CARDS            = "There are no targets available, hence the ability has no effect."
MSG_ERR_NO_CARDS_HAND       = "You don't have enough cards in your hand to pay the cost of the ability."
MSG_ERR_NO_CARDS_DISCARD    = "There are no cards to discard [of the chosen type] in {}'s hand."
MSG_ERR_NO_FILTERED_CARDS   = "Selected cards don't match the requirements of this card's effect."
MSG_ERR_NO_FILTERED_PLAYERS = "No player match the requirements of this card's effect."
MSG_ERR_TARGET_OTHER        = "{}'s ability cannot select itself, therefore it has been removed from selection."
MSG_ERR_ATTACK_CHAR_RING    = "Please attack with a character in your ring."
MSG_HOOKS_ERR = {
   Hooks.BeforeAttack: "{} cannot attack due to {}'s {} ability{}.",
   Hooks.BeforeBlock : "{} cannot counter-attack due to {}'s {} ability{}.",
   Hooks.CanBlock: "{} cannot be blocked due to {}'s {} ability{}.",
   Hooks.BeforePlayAC: "{} cannot play action cards due to {}'s {} ability{}.",
   Hooks.BeforePlayRE: "{} cannot play reaction cards due to {}'s {} ability{}."
}

MSG_AB = {
   'cantattack': [
      MSG_HOOKS_ERR[Hooks.BeforeAttack],
      "{} can attack again."
   ],
   'cantblock': [
      MSG_HOOKS_ERR[Hooks.BeforeBlock],
      "{} can counter-attack again."
   ],
   'unblockable': [
      MSG_HOOKS_ERR[Hooks.CanBlock],
      "{} can be blocked as normal."
   ],
   'cantplayac': [
      MSG_HOOKS_ERR[Hooks.BeforePlayAC],
      "{} can play action cards again."
   ],
   'cantplayre': [
      MSG_HOOKS_ERR[Hooks.BeforePlayRE],
      "{} can play reaction cards again."
   ],
   'unlimitedbackup': [
      "{0} can receive any number of back-ups {3}."
   ],
   'preventpierce': [
      "Piercing damage was prevented by {0}'s {2} ability."
   ],
   'unfreezable': [
      "{0} will not freeze after attacking{3}."
   ],
   'rush': [
      "{} can attack this turn due to {}'s {} ability."
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
   'card_cost': '{} cards now cost {} SP {}to play{}.',
   'cost_ua2': 'Double united attacks now cost {1} SP{3}.',
   'cost_ua3': 'Triple united attacks now cost {1} SP{3}.',
   'piercing': (
      'Whenever a character counter-attacks a United Attack, piercing damage is prevented.',  # Disabled
      'United-Attacks deals piercing damage as normal.'  # Enabled
   ),
   'backup_fresh': (
      'Characters cannot receive back-up the turn they enter the ring.',
      'Characters can receive back-up the turn they enter the ring.'
   ),
   'play_char_bp_limit': (
      'Character cards of any BP can be played as normal.',
      'Character cards with BP {} or greater cannot be played.'
   ),
   'dmg_combat_deal': (
      'Characters deal no combat damage{1}',
      'Characters deal combat damage as normal'
   )
}

CMD_LABELS = {
   'swapchars' : 'Swap the positions of two characters in the same ring',
   'movetoslot': 'Move a character to an empty slot in the same ring',
   'damage'    : 'Deal damage',
   'hp'        : 'Gain HP',
   'bp'        : 'Raise the BP of characters',
   'discard'   : 'Discard card(s)',
   'destroy'   : 'KO character(s)',
   'shuffle'   : 'Shuffle the deck'
}

ERR_NO_EFFECT = 'err001'
# Python Scripts for the Card Fighters' Clash definition for OCTGN
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
# Markers functions
#---------------------------------------------------------------------------

def hasMarker(card, marker, include = True):
   if not isCard(card):
      return False
      
   res = MarkersDict[marker] in card.markers
   if include:
      return res
   else:
      return not res
      
      
def getMarker(card, mkname):
   return card.markers[MarkersDict[mkname]]

      
def changeMarker(cards, marker, question = None, count = None):
# Changes the number of markers in one or more cards
   n = 0
   if not count:
      for c in cards:
         if c.markers[marker] > n:
           n = c.markers[marker]
      count = askInteger(question, n)
   if count == None:
      return
   if marker == MarkersDict['BP']:
      count = fixBP(count)
   for c in cards:
      n = c.markers[marker]
      c.markers[marker] = count
      diff = count-n
      if diff >= 0:
         diff = "+" + str(diff)
      notify("{} sets {}'s {} to {} ({}).".format(getSourcePlayer(), c, marker[0], count, diff))


def setMarker(card, mkname, qty = 1):
   card.markers[MarkersDict[mkname]] = qty


def addMarker(card, mkname, qty = 1):
   card.markers[MarkersDict[mkname]] += qty


def removeMarker(card, mkname):
   if MarkersDict[mkname] in card.markers:
      setMarker(card, mkname, 0)


def toggleMarker(card, mkname):
   if MarkersDict[mkname] in card.markers:
      removeMarker(card, mkname)
   else:
      setMarker(card, mkname, 1)
      
      
def modBP(card, qty, mode = None):
   if mode == RS_MODE_EQUAL:
      changeMarker([card], MarkersDict['BP'], count = qty)
   elif qty >= 0:
      plusBP([card], count = qty)
   else:
      minusBP([card], count = -qty)


def fixBP(n):
   # if n < 100:
      # return 100
   # else:
   return int(round(n / 100.0)) * 100


#---------------------------------------------------------------------------
# Counter Manipulation
#---------------------------------------------------------------------------

def dealDamage(dmg, target, source, combatDmg = True, isPiercing = False):
   if not getRule('dmg_combat_deal') and isCharacter(source) and (hasMarker(source, 'Attack') or hasMarker(source, 'Counter-attack')):
      notify("{} deals no combat damage due to an ability or effect.".format(source))
      return
   if isinstance(target, Card):
      oldBP = getMarker(target, 'BP')
      minDmg = min(dmg, getMarker(target, 'BP'))
      addMarker(target, 'BP', -minDmg)
      newBP = getMarker(target, 'BP')
      notify("{} deals {} {}damage to {}. New BP is {} (before was {}).".format(source, dmg, "combat " if combatDmg else "", target, newBP, oldBP))
      if isCharacter(source):
         playSnd('damage-char-1')
         if combatDmg:
            source.arrow(target)
      else:
         playSnd('damage-char-2')
      if newBP <= 0:
         funcCall(target.controller, whisper, [MSG_HINT_KOED.format(target)])
   # Damage to a player
   else:
      if not isCharacter(source):
         dispatchEvent(GameEvents.BeforeDamage, args = [source._id])
      dmg += getTempVar('damageMod', 0)
      oldHP = getState(target, 'HP')
      newHP = oldHP - dmg
      target.HP = newHP
      setState(target, 'HP', newHP)  # Update game state
      typeOfDmg = ""
      if isPiercing:
         typeOfDmg = "piercing "
      elif combatDmg:
         typeOfDmg = "combat "
      notify("{} deals {} {}damage to {}. New HP is {} (before was {}).".format(source, dmg, typeOfDmg, target, target.HP, oldHP))
      if newHP <= 0:
         notifyWinner(getOpp(target))
      # Change game state: non-combat damage
      if not isCharacter(source) or not hasMarker(source, 'Attack'):
         setState(target, 'damaged', True)
         playSnd('damage-player-2')
      else:
         playSnd('damage-player-1')
      if combatDmg:
         avatar = getAvatar(target)
         if avatar:
            source.arrow(avatar)
      update()


def loseLife(qty, target, source):
   oldHP = getState(target, 'HP')
   newHP = oldHP - qty
   target.HP = newHP
   setState(target, 'HP', newHP)  # Update game state
   effect = "ability".format(source) if isCharacter(source) else "effect"
   notify("{} loses {} HP due to {}'s {}. New HP is {} (before was {}).".format(target, qty, source, effect, target.HP, oldHP))
   if newHP <= 0:
      notifyWinner(getOpp(target))
   playSnd('lose-life')


def modSP(count = 1, mode = None, silent = False, player = me, silentSnd = False):
# A function to modify the players SP counter. Can also notify.
   initialSP = player.SP
   if mode == RS_MODE_EQUAL:
      player.SP = count
      count = player.SP - initialSP
   else:
      if player.SP + count < 0:
         count = -initialSP  # SP can't be less than 0
      player.SP += count # Now increase the SP by the amount passed to us.
   if not silent and count != 0:
      action = "gains" if count >= 0 else "loses"
      if count < 0:
         setState(player, 'lostSP', -count)
         playSnd('lose-sp')
      elif not silentSnd:
         playSnd('gain-sp')
      notify("{} {} {} SP. New total is {} SP (before was {}).".format(player, action, count, player.SP, initialSP))


def payCostSP(amount = 1, obj = None, msg = 'play this card', type = None):
# Pay an SP cost. However we also check if the cost can actually be paid.
   debug(">>> payCostSP({}, {})", amount, type)
   costModMsg = None
   
   # Cost modifiers
   if type:
      newAmount = getCostMod(amount, type, obj)
      if amount != newAmount:
         costModMsg = u"The SP cost of {} has been modified by an ability ({}  \u2192  {}).".format(obj, amount, newAmount)
         amount = newAmount
   
   if amount >= 0 and type == CharType:
      modSP(amount, silentSnd = True)
   else:
      initialSP = me.SP
      if me.SP + amount < 0: # If we don't have enough SP, notify the player that they need to do things manually
         warning("You do not have enough SP to {}.\n(Cost is {} SP.)".format(msg, amount))
         return False
      me.SP += amount
      if costModMsg:
         notify(costModMsg)
      notify("{} has spent {} SP. New total is {} SP (before was {}).".format(me, amount, me.SP, initialSP))
   return True
   
   
def getCostMod(initialAmount, type, obj = None):
   debug(">>> getCostMod({}, {})", obj, type)
   newAmount = initialAmount
   costMod = 0
   type = type.lower()
   Modifiers = getGlobalVar('Modifiers')
   if 'cost' in Modifiers:
      # [source_id, type, value, mode]
      for mod in Modifiers['cost']:
         if mod[1] == type:
            debug("-- Found cost modifier: {}", mod)
            if mod[3] == RS_MODE_EQUAL:  # mode
               newAmount = mod[2]
               initialAmount = mod[2]
            else:
               costMod += mod[2]
   # Cost modified by events
   dispatchEvent(GameEvents.BeforePayCost + type, args = [obj._id] if isCard(obj) else None)
   costMod += getTempVar('costMod'+type, 0)
   # Fix final value
   if costMod != 0:
      newAmount += costMod
      # If initial cost is less than 0, then new cost cannot be less than -1 (Kyosuke rule)
      if newAmount >= 0 and isCard(obj):
         newAmount = max(initialAmount, -1)
   return newAmount


#------------------------------------------------------------------------------
# Card Attachments
#------------------------------------------------------------------------------

def attach(card, target):
   debug(">>> attachCard()")
   target.target(False)
   backups = getGlobalVar('Backups')
   backups[card._id] = target._id
   setGlobalVar('Backups', backups)
   debugBackups()
   debug("<<< attachCard()")
   

def dettach(card):
   debug(">>> dettach()")
   mute()
   card.target(False)
   card_id = card._id
   backups = getGlobalVar('Backups')
   # Delete links of cards that were attached to the card
   if card_id in backups.values():
      for id in backups:
         if backups[id] == card_id:
            del backups[id]
            notify("{} unattaches {} from {}.".format(me, Card(id), card))
   # Or, if the card was an attachment, delete the link
   elif card_id in backups:
      del backups[card_id]
      notify("Unattaching {} from {}".format(card, Card(backups[card_id])))
   else:
      return
   setGlobalVar('Backups', backups)
   debugBackups()
   debug("<<< dettach()")


def clearAttachLinks(card):
# This function takes care to discard any attachments of a card that left play.
# It also clear the card from the attach dictionary, if it was itself attached to another card.
   debug(">>> clearAttachLinks({})", card)
   
   backups = getGlobalVar('Backups')
   card_id = card._id
   # Dettach cards that were attached to the card
   if card_id in backups.values():
      notify("{} clears all backups of {}.".format(me, card))
      for id in backups:
         if backups[id] == card_id:
            attcard = Card(id)
            debug("Unattaching {} from {}.", attcard, card)
            if attcard in table:
               discard(attcard)
            del backups[id]
   # If the card was an attachment, delete the link
   elif backups.has_key(card_id):
      debug("{} is attached to {}. Unattaching.", card, Card(backups[card_id]))
      del backups[card_id] # If the card was an attachment, delete the link
   setGlobalVar('Backups', backups)
   
   debugBackups()   
   debug("<<< clearAttachLinks()")
   

def getAttachmets(card):
   debug(">>> getAttachmets({})", card)
   
   # Returns a list with all the cards attached to this card
   backups = getGlobalVar('Backups')
   card_id = card._id
   attachs = []
   for id in backups:
      if backups[id] == card_id:
         attachs.append(Card(id))
         
   debug("{} has {} cards attached", card, len(attachs))
   return attachs
   

def getAcceptedBackups(card):
   return filter(None, [card.properties['Backup 1'], card.properties['Backup 2'], card.properties['Backup 3']])


#---------------------------------------------------------------------------
# Helpers
#---------------------------------------------------------------------------

def isNumber(s):
   if not s or isinstance(s, bool):
      return False
   try:
      float(s)
      return True
   except ValueError:
      return False
        

def isPlayer(obj):
   return isinstance(obj, Player)


def isCard(obj):
   return isinstance(obj, Card)


def isCharacter(card):
   return card.Type == CharType


def isAction(card):
   return card.Type == ActionType


def isReaction(card):
   return card.Type == ReactionType


def isButton(card):
   return card.Type == ButtonType


def isAvatar(card):
   return card.Type == AvatarType


def isUI(card):
   return card.Type in [ButtonType, AvatarType]


def isAttached(card):
   backups = getGlobalVar('Backups')
   return bool(backups.get(card._id))
   
   
def isFrozen(card):
   return card.orientation & Rot90 == Rot90


def isAttacking(card, inUA = True):
   return hasMarker(card, 'Attack') or inUA and hasMarker(card, 'United Attack')


def isBlocking(card):
   return hasMarker(card, 'Counter-attack')


def inUAttack(card):
   uattack = getGlobalVar('UnitedAttack')
   if len(uattack) > 0 and card._id in uattack:
      return True
   return False


def isVisible(card):
   if not card.isFaceUp:
      return False
   if card.group.name == 'Hand':
      return False
   return True


def hasFilter(card, filter):
   return card.filter and card.filter[1:] == filter[3:]


def canBackup(card):
   # Char just entered the ring?
   if hasMarker(card, "Just Entered") and not getRule('backup_fresh'):
      warning("Characters that just entered the ring this turn can't be backed-up.")
      return
   # Backup limit
   backupsPlayed = getState(me, 'backupsPlayed')
   if backupsPlayed >= BackupsPerTurn:
      if getRule('backup_limit') and triggerHook(Hooks.BackupLimit, card._id) != False:
         warning("You can't backup more than {} character per turn.".format(BackupsPerTurn))
         return
   return True
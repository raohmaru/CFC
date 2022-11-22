# Python Scripts for the Card Fighters" Clash definition for OCTGN
# Copyright (C) 2022 Raohmaru

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

#---------------------------------------------------------------------------
# Counter manipulation
#---------------------------------------------------------------------------

def dealDamage(dmg, target, source, combatDmg = True, isPiercing = False):
   """
   Applies damage from a source to a target, either a card or a player.
   """
   if not getRule("dmg_combat_deal") and isCharacter(source) and (hasMarker(source, "Attack") or hasMarker(source, "Counter-attack")):
      notify("{} deals no combat damage due to an ability or effect.", source)
      return
   # Damage to a card
   if isinstance(target, Card):
      oldBP = getMarker(target, "BP")
      realDmg = min(dmg, getMarker(target, "BP"))  # Damage cannot be greater than target's BP
      addMarker(target, "BP", -realDmg)
      newBP = getMarker(target, "BP")
      notify("{} deals {} {}damage to {}. New BP is {} (before was {}).", source, dmg, "combat " if combatDmg else "", target, newBP, oldBP)
      if isCharacter(source):
         playSnd("damage-char-1")
         if combatDmg:
            source.arrow(target)
      else:
         playSnd("damage-char-2")
      if newBP <= 0:
         funcCall(target.controller, whisper, [MSG_HINT_KOED.format(target)])
   # Damage to a player
   else:
      # Non-combat damage modifications
      if not isCharacter(source):
         dispatchEvent(GameEvents.BeforeDamage, args = [source._id])
      modDmg = getTempVar("damageMod", 0)
      if modDmg != 0:
         notify(u"Damage has been {} by {} ({}  \u2192  {}).", ["decreased", "increased"][modDmg > 0], modDmg, dmg, dmg + modDmg)
         dmg += modDmg
      oldHP = getState(target, "HP")
      newHP = oldHP - dmg
      newHP = max(0, newHP)
      target.HP = newHP
      # Update game state in case several attacks are done at once
      setState(target, "HP", newHP)
      typeOfDmg = ""
      if isPiercing:
         typeOfDmg = "piercing "
      elif combatDmg:
         typeOfDmg = "combat "
      notify("{} deals {} {}damage to {}. New HP is {} (before was {}).", source, dmg, typeOfDmg, target, target.HP, oldHP)
      if newHP <= 0:
         notifyWinner(getOpp(target))
      # Change game state: non-combat damage
      if not isCharacter(source) or not hasMarker(source, "Attack"):
         setState(target, "ncDamaged", True)
         playSnd("damage-player-2")
      else:
         playSnd("damage-player-1")
      if combatDmg:
         avatar = getAvatar(target)
         if avatar:
            source.arrow(avatar)
      update()


def loseLife(qty, target, source):
   oldHP = getState(target, "HP")
   newHP = oldHP - qty
   newHP = max(0, newHP)
   target.HP = newHP
   effect = "ability".format(source) if isCharacter(source) else "effect"
   notify("{} loses {} HP due to {}'s {}. New HP is {} (before was {}).", target, qty, source, effect, target.HP, oldHP)
   if newHP <= 0:
      notifyWinner(getOpp(target))
   playSnd("lose-life")


def modSP(amount = 1, mode = None, silent = False, player = me, silentSnd = False):
   initialSP = player.SP
   if mode == RS_MODE_EQUAL:
      player.SP = amount
      amount = player.SP - initialSP
   else:
      if player.SP + amount < 0:
         amount = -initialSP  # SP can"t be less than 0
      player.SP += amount
   if not silent and amount != 0:
      action = "gains" if amount >= 0 else "loses"
      if amount < 0:
         setState(player, "lostSP", -amount)
         playSnd("lose-sp")
      elif not silentSnd:
         playSnd("gain-sp")
      notify("{} {} {} SP. New total is {} SP (before was {}).", player, action, amount, player.SP, initialSP)


def payCostSP(amount = 1, obj = None, reason = "play this card", type = None):
   """
   Pays a SP cost. However it also check if the cost can actually be paid.
   """
   debug(">>> payCostSP({}, {})", amount, type)
   costModMsg = None
   # Cost modifiers
   if type:
      newAmount = getCostMod(amount, type, obj)
      if amount != newAmount:
         costModMsg = u"The SP cost of {} has been modified by an ability ({}  \u2192  {}).".format(obj, amount, newAmount)
         amount = newAmount
   # Get the SP from playing a char
   if amount >= 0 and type == CharType:
      modSP(amount, silentSnd = True)
   else:
      initialSP = me.SP
      # Cancel if player doesn't have enough SP
      if me.SP + amount < 0:
         msg = MSG_ERR_NO_SP.format(reason, amount)
         warning(msg)
         notify(msg)
         return False
      me.SP += amount
      if costModMsg:
         notify(costModMsg)
      notify("{} has spent {} SP. New total is {} SP (before was {}).", me, amount, me.SP, initialSP)
   return True
   
   
def getCostMod(initialAmount, type, obj = None):
   """
   Gets all the modifications applied to a cost for the given type.
   :param str type: A card type, ua2, ua3.
   """
   debug(">>> getCostMod({}, {})", obj, type)
   newAmount = initialAmount
   costMod = 0
   type = type.lower()
   Modifiers = getGlobalVar("Modifiers")
   if "cost" in Modifiers:
      # [source_id, type, value, mode]
      for mod in Modifiers["cost"]:
         if mod[1] == type:
            debug("-- Found cost modifier: {}", mod)
            if mod[3] == RS_MODE_EQUAL:  # mode
               newAmount = mod[2]
               initialAmount = mod[2]
            else:
               costMod += mod[2]
   # Cost modified by events
   dispatchEvent(GameEvents.BeforePayCost + type, args = [obj._id] if isCard(obj) else None)
   costMod += getTempVar("costMod" + type, 0)
   # Fix final value
   if costMod != 0:
      newAmount += costMod
      # If initial cost is less than 0, then new cost cannot be greater than -1 (Kyosuke rule)
      if newAmount >= 0 and isCard(obj):
         newAmount = max(initialAmount, -1)
   return newAmount
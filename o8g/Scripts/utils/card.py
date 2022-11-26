# Python Scripts for the Card Fighters' Clash definition for OCTGN
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
# Card functions
#---------------------------------------------------------------------------

def fixCardY(y, height = CardHeight, inverted = False):
   """
   Variable to move the cards played by player 2 on a 2-sided table, more towards their own side. 
   Player's 2 axis will fall one extra card length towards their side.
   https://github.com/kellyelton/OCTGN/issues/146
   """
   offsetY = 0
   if me.isInverted or inverted:
      offsetY = height
   side = me.side
   if inverted:
      side = -1
   return (y + offsetY) * side
   
   
def invertSlotIdx(slotIdx, player = me, inverted = False):
   """
   Fixes the slot index for players playing with the inverted table.
   """
   if player.isInverted or inverted:
      slotIdx = abs(slotIdx - (NumSlots - 1))
   return slotIdx

   
def placeCard(card, type = None, action = None, target = None, faceDown = False):
   """
   Automatically places a card on the table according to the type of card.
   """
   debug(">>> placeCard()")
   if settings["PlayAuto"]:
      if type == CharType and action != None:
         coords = (0, fixCardY(0))
         if action == "play":
            coords = CardsCoords["Slot" + `invertSlotIdx(target)`]
            coords = (coords[0], fixCardY(coords[1]))
         elif action == "backup":
            cx, cy = target.position
            backups = getGlobalVar("Backups")
            numBkps = len([id for id in backups if backups[id] == target._id])
            coords = (cx + CardsCoords["BackupOffset"][0] * numBkps, cy + CardsCoords["BackupOffset"][1] * numBkps)
         card.moveToTable(coords[0], coords[1], faceDown)
      # Place action and reaction cards in ordered fashion
      elif type != CharType:
         cards = [c for c in table
            if c.controller == me
            and isAction(c) or isReaction(c)]
         posX = -((len(cards) + 1) * CardWidth) / 2 * me.side
         if me.side == -1:
            posX -= CardWidth
         posY = fixCardY(CardsCoords["Action"][1])
         for i, c in enumerate(cards):
            c.moveToTable(posX + CardWidth * i * me.side, posY)
         card.moveToTable(posX + CardWidth * len(cards) * me.side, posY, faceDown)
      else:
         card.moveToTable(-CardWidth / 2, fixCardY(0), faceDown)
   else:
      card.moveToTable(0, fixCardY(0), faceDown)

   debug("<<< placeCard()")

  
def getSlotIdx(card, player = me):
   """
   Gets the slot index of a card in the given player's ring.
   """
   debug(">>> getSlotIdx({})", card)
   ring = getGlobalVar("Ring", player)
   for i, id in enumerate(ring):
      if id == card._id:
         # Invert slot if card is in the inverted side or controlled by the tutorial bot
         if card.controller != me or (tutorial and card.position[1] < 0):
            i = invertSlotIdx(i, player)
         debug("Slot idx: {}", i)
         return i
   debug("Card isn't in a slot")
   return -1


def getDropSlotIndex(x):
   """
   Returns the slot closest to the given X coordinate, or None.
   """
   idx = None
   ox = 200
   cx = x + CardWidth/2
   for j in range(NumSlots):
      slotX = CardsCoords["Slot" + `invertSlotIdx(j)`][0] + CardWidth / 2
      diff = abs(slotX - cx)
      if diff < ox:
         idx = j
         ox = diff
   return idx


def getCardAtSlot(idx, player = me):
   debug(">>> getCardAtSlot({}, {})", idx, player)
   ring = getGlobalVar("Ring", player)
   if player != me:
      ring.reverse()
   card = Card(ring[idx]) if ring[idx] else None
   debug("Card at slot {} is: {}", idx, card)
   return card
   
  
def putAtSlot(card, idx, player = me, move = False):
   """
   Puts or move a card into a slot in the ring.
   """
   debug(">>> putAtSlot({}, {}, move = {})", card, idx, move)
   if idx < NumSlots:
      ring = getGlobalVar("Ring", player)
      if move:
         oldIdx = getSlotIdx(card, player)
         if oldIdx != -1:
            ring[oldIdx] = None         
      ring[idx] = card._id
      setGlobalVar("Ring", ring, player)
      debug("{}'s ring: {}", me, ring)


def alignCard(card, x = None, y = None, slotIdx = None):
   """
   Aligns a card in the table according to its state.
   """
   debug(">>> alignCard({}, {}, {}, {})", card, x, y, slotIdx)
   z = None
   if x == None or y == None:
      if slotIdx == None:
         slotIdx = getSlotIdx(card)
      if slotIdx == -1:
         return
      slotIdx = invertSlotIdx(slotIdx)
      # Align attacking chars
      if hasMarker(card, "Attack"):
         x, y = CardsCoords["Attack" + `slotIdx`]
         y = fixCardY(y)
      # Align chars in a uattack
      elif hasMarker(card, "United Attack"):
         uattack = getGlobalVar("UnitedAttack")
         if len(uattack) <= 1 or card._id not in uattack:
            return
         idx = uattack.index(card._id)
         ox, oy = CardsCoords["UAttackOffset"]
         lead = Card(uattack[0])
         lead.index = MaxCharsUAttack + 1
         x, y = lead.position
         x += ox * idx * me.side
         y += oy * idx
         z = lead.index - 1 * idx
      # Align blockers
      elif isBlocking(card):
         blockers = getGlobalVar("Blockers")         
         for i in blockers:
            if blockers[i] == card._id:
               atkIdx = getSlotIdx(Card(i), players[1])
               x, y = CardsCoords["Attack" + `atkIdx`]
               y = fixCardY(y)
               break
      # Move char to its assigned slot
      else:
         x, y = CardsCoords["Slot" + `slotIdx`]
         y = fixCardY(y)
   if x != None and y != None:
      card.moveToTable(x, y)
   if z != None:
      card.index = max(z, 0)


def alignBackups(card, x = 0, y = 0):
   """
   Aligns the cards attached to the given card.
   """
   debug(">>> alignBackups({}, {}, {})", card, x, y)
   attachs = getAttachments(card)
   if len(attachs) > 0:
      ox, oy = CardsCoords["BackupOffset"]
      # Card on top
      card.index = len(attachs)
      for i, c in enumerate(attachs):
         nx = x + ox * (i + 1)
         ny = y + oy * (i + 1)
         cx, cy = c.position
         if nx != cx or ny != cy:
            c.moveToTable(nx, ny)
         # Backups below main card
         c.index = 0

   
def revealCard(card, type = None):
   cardname = card.Name
   if not isVisible(card):
      if confirm("Reveal card to all players?"):
         card.isFaceUp = True
         waitForAnimation()
         cardname = card.Name
      else:
         type = type + " " if type != None else ""
         cardname = "a {}card".format(type)
   return cardname
   
   
def transformCard(card, cardModel):
   """
   Transform a card into another card. Actually it creates a new card and removes the original.
   """
   debug(">>> transformCard({}, {})", card, cardModel)
   group = card.group
   cx, cy = card.position
   if group == table:
      newCard = group.create(cardModel, cx, cy, quantity = 1, persist = True)
      clearAttachLinks(card)
      slotIdx = getSlotIdx(card)
      if slotIdx != -1:
         setMarker(newCard, "BP", newCard.BP)
         putAtSlot(newCard, slotIdx)
         newCard.orientation = card.orientation
         if settings["PlayAuto"]:
            createGameCard(newCard, forceActivateAuto = True)
         if isFresh(card):
            setMarker(newCard, "Just Entered", 1)
      for m in card.markers:
         if m[0] != "BP":
            setMarker(newCard, m[0], card.markers[m])
   else:
      newCard = group.create(cardModel, quantity = 1)
   if group == table and card.isFaceUp:
      notify("{} transforms {} into {}.", me, card, newCard)
   else:
      notify("{} transformed a card {}.", me, fromWhereStr(group))
   model = card.model
   update()
   # Store the original card model in the transformed list to restore it back if needed
   if card._id in transformed:
      model = transformed[card._id]
      del transformed[card._id]
   transformed[newCard._id] = model
   debug("{}", transformed)
   dispatchEvent(GameEvents.Removed, card._id)
   removeGameEventListener(card._id)
   deleteGameCard(card)
   card.delete()
   playSnd("transform")
   
   
def copyAlternateRules(card, target):
   """
   Copies the rules of the target card into another card as an alternate form.
   """
   debug(">>> copyAlternateRules({}, {})", card, target)
   if not settings["ExtAPI"]:
      return False
   if isinstance(target, dict):
      # Converts the dict into a Card-like object
      target = Struct(**target)
   rules = target.Rules
   ability = target.Ability
   if rules:
      debug("Found rule '{} {}'", ability, rules)
      return addAlternateRules(card, ability, rules)
   return False
   

def addAlternateRules(card, ability, rules, altname = None):
   """
   Adds an alternate form to the card (a different set of properties to the same card).
   https://github.com/octgn/OCTGN/wiki/set.xml#alternate
   """
   debug(">>> addAlternateRules({}, {}, {})", card, ability, altname)
   if not settings["ExtAPI"]:
      return None
   ability = Ability(ability, rules)
   if not altname:
      altname = sanitizeStr(ability.name)
   cardData = _extapi.getCardDataById(card._id)
   # Creates a new alternate (Octgn.DataNew.Entities.CardPropertySet)
   cardData.PropertySets[altname] = cardData.PropertySets[""].Clone()
   _extapi.setCardProperty(cardData, "Rules", rules, altname)
   _extapi.setCardProperty(cardData, "Ability Type", ability.type, altname)
   _extapi.setCardProperty(cardData, "Ability Name", ability.name, altname)
   _extapi.setCardProperty(cardData, "Ability", (ability.type + " " + ability.name).strip(), altname)
   debug("Adding new alternate '{}' and generating proxy", altname)
   _extapi.generateProxy(cardData, altname)
   # Switch alternate after data is created, otherwise if network tasks are not done, the card won't switch at all
   card.alternate = altname
   return altname
   
  
def passControlTo(player, cards, cb = None, cbArgs = None):
   debug(">>> passControlTo({}, {}, {}, {})", player, cards, cb, cbArgs)
   for card in cards:
      if card.group != table:
         card.moveToTable(0, 0, True)
      card.controller = player
   if cb is not None:
      update()
      remoteCall(player, cb, cbArgs)
   

def getAttackingCards(player = me, getUA = False):
   if tutorial and player._id == 0:  # Fake player
      player = me
   return [card for card in table
      if card.controller == player
      and hasMarker(card, "Attack")
      or (getUA and hasMarker(card, "United Attack"))]


def getTargetedCardsFrom(card = None, targetedByMe = True, controlledByMe = True, type = CharType, group = table):
   """
   Returns a list with all cards from the given group targeted by the given player.
   """
   targetedBy   = me if targetedByMe   or len(players) == 1 else players[1]
   controlledBy = me if controlledByMe or len(players) == 1 else players[1]
   targets = [c for c in group
      if  c != card
      and c.targetedBy == targetedBy
      and c.controller == controlledBy
      and (type == None or c.Type == type)]
   return targets


def getAllTargetedCards(player = me):
   """
   Get all cards in the game targeted by a player.
   """
   targets =  [c for c in table if c.targetedBy == player]
   targets += [c for c in player.hand if c.targetedBy == player]
   targets += [c for c in player.piles["Discard pile"] if c.targetedBy == player]
   if len(players) > 1:
      targets += [c for c in getOpp().piles["Discard pile"] if c.targetedBy == player]
   return targets
   
   
def getCards(group = table, player = me, includeUI = False):
   return [card for card in group
      if card.controller == me
      and (not isUI(card) or includeUI)]


def copyCard(card):
   """
   Creates a shallow copy of the card which is not a Card entity.
   Returns: Struct
   """
   CharsAbilities = getGlobalVar("CharsAbilities")
   # Shallow copy of the card
   card_copy = Struct(**{
      "Rules"  : card.Rules,
      "Ability": card.Ability,
      "model"  : CharsAbilities[card._id] if card._id in CharsAbilities else card.model
   })
   return card_copy


def discardKOedChars():
   """
   Destroy characters with 0 BP.
   """
   for card in getRing():
      if getMarker(card, "BP") == 0:
         notify("{}'s {} BP is 0. Taking it out from the arena.", card.controller, card)
         if card.controller == me:
            destroy(card)
            update()  # Syncs the game state along players. Also delays animations.
         else:
            remoteCall(card.controller, "destroy", [card, card.controller])
            remoteCall(card.controller, "update", [])
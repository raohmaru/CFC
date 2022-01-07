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

#---------------------------------------------------------------------------
# Event Overrides
#---------------------------------------------------------------------------

def overrideCardsMoved(args):
   """
   Triggers when one or more cards are simultaneously moved from one location to another via drag-drop.
   """
   cards     = args.cards
   toGroups  = args.toGroups
   indexs    = args.indexs
   xs        = args.xs
   ys        = args.ys
   faceups   = args.faceups
   phaseIdx  = getCurrentPhase()
   
   for i in range(len(cards)):
      card      = args.cards[i]
      fromGroup = card.group
      toGroup   = toGroups[i]
      index     = indexs[i]
      x         = xs[i]
      y         = ys[i]
      faceup    = faceups[i]
      # debug("overrideCardsMoved: {}: {} -> {}, [{}, {}] ({}) {}", card, fromGroup.name, toGroup.name, x, y, index, faceup)
      
      if isUI(card):
         continue
      
      if toGroup == table:
         if settings["PlayAuto"]:
            # Play from hand or any other allowed group
            if fromGroup == me.hand or (getRule("play_removed") and fromGroup.name == "Removed pile"):
               # It may have been played faced down
               if not faceup:
                  mute()  # Or OCTGN will tell which card it is
                  notify(MSG_ACTION_FACE_DOWN.format(me, fromWhereStr(fromGroup)))
                  card.moveToTable(x, y, True)
                  continue
               # Play a character card
               if isCharacter(card):
                  slotIdx = getDropSlotIndex(x)
                  if slotIdx == None:
                     continue
                  myRing = getGlobalVar("Ring", me)
                  if myRing[slotIdx] == None:
                     play(card, slotIdx = slotIdx)
                  else:
                     backup(card, target = Card(myRing[slotIdx]))
               # Play other type of card
               else:
                  play(card)
               continue
            # Move cards in the table
            elif fromGroup == table:
               cy = card.position[1]
               # Attack
               if me.isActive and phaseIdx == AttackPhase and charIsInRing(card):
                  if (y > cy - DragOffsetY, y < cy + DragOffsetY)[bool(playerSide + 1)]:
                     slotIdx = getDropSlotIndex(x)
                     if slotIdx == None:
                        continue
                     myRing = getGlobalVar("Ring", me)
                     # United Attack
                     if myRing[slotIdx] != None:
                        atkCard = Card(myRing[slotIdx])
                        if isAttacking(atkCard, False):
                           if isAttacking(card):
                              cancelAttack(card, True)
                           unitedAttack(card, targets = [atkCard])
                           continue
                     if hasMarker(card, "Attack"):
                        alignCard(card)
                     else:
                        if hasMarker(card, "United Attack"):
                           cancelAttack(card, True)
                        attack(card)
                     continue
                  # Cancel attack
                  elif isAttacking(card):
                     cancelAttack(card)
                     continue
               # Block
               elif (not me.isActive or tutorial) and phaseIdx == BlockPhase and charIsInRing(card):
                  if (y > cy - DragOffsetY, y < cy + DragOffsetY)[bool(playerSide + 1)]:
                     slotIdx = getDropSlotIndex(x)
                     if slotIdx == None:
                        continue
                     slotIdx = fixSlotIdx(slotIdx, fix = True)
                     targets = None
                     oppRing = getGlobalVar("Ring", getOpp())
                     if oppRing[slotIdx] != None:
                        targets = [Card(oppRing[slotIdx])]
                     if isBlocking(card):
                        cancelBlock(card, True)
                     block(card, targets = targets)
                     continue
                  # Cancel block
                  elif isBlocking(card):
                     cancelBlock(card)
                     continue
         card.moveToTable(x, y, not faceup)
         card.index = index
      # Move cards to a pile
      else:
         card.moveTo(toGroup, index)
         
         
def overrideTurnPassed(args):
   """
   Triggers when the player clicks the green "Pass Turn" button on the player tabs.
   """
   if tutorial:
      tutorial.goNext()
      return
   
   player = args.player  # The player the turn is being passed to
   setState(None, "activePlayer", player._id)
   nextTurn(player)


#---------------------------------------------------------------------------
# Related functions
#---------------------------------------------------------------------------

def getDropSlotIndex(x):
   """
   Returns the slot closest to the given X coordinate, or None.
   """
   idx = None
   ox = 200
   cx = x + CardWidth/2
   for j in range(NumSlots):
      slotX = CardsCoords["Slot" + `fixSlotIdx(j)`][0] + CardWidth / 2
      diff = abs(slotX - cx)
      if diff < ox:
         idx = j
         ox = diff
   return idx
   
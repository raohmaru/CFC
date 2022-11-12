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

#------------------------------------------------------------------------------
# Start/End of Turn/Phase triggers
#------------------------------------------------------------------------------

def triggerPhaseEvent(phase, oldPhase = 0):
   """
   Function which triggers effects at the start or end of the phase.
   """
   debug(">>> triggerPhaseEvent({})", phase)
   mute()
   if not settings["PlayAuto"]:
      return
   
   backwards = phase < oldPhase
   # Going backwards?
   # if backwards:
      # return
   
   skipPhases = getState(me, "skip")
   if phase in skipPhases:
      notify("{} skips their {} phase due to an ability.".format(me, PhaseNames[phase]))
      skipPhases.remove(phase)  # remove by value
      setState(me, "skip", skipPhases)
      nextPhase(False)
      return

   if   phase == ActivatePhase: activatePhaseStart()
   elif phase == DrawPhase:
      if turnNumber() == 1:
         notify("{} skips their {} phase (the first player must skip it during their first turn).".format(me, PhaseNames[phase]))
         nextPhase(False)
         return
      else:
         drawPhaseStart()
   elif phase == MainPhase:   mainPhaseStart()
   elif phase == AttackPhase: attackPhaseStart()
   elif phase == BlockPhase:
      if len(getAttackingCards(me, True)) == 0:
         notify("{} skips their {} phase because there are no attacking characters.".format(me, PhaseNames[phase]))
         if backwards:
            prevPhase()
         else:
            nextPhase(False)
         return
      else:
         blockPhaseStart()
   elif phase == EndPhase:      endPhaseStart()
   elif phase == CleanupPhase:  cleanupPhaseStart()
   
   global phaseOngoing
   phaseOngoing = False
   
   # Automatic phase change
   if settings["PhaseAuto"] and not backwards:
      if not getStop(phase) and (
            phase not in [MainPhase, AttackPhase, BlockPhase, EndPhase]
            or phase == EndPhase and len(getAttackingCards()) == 0
      ):
         # time.sleep(0.1)  # Blocks main thread
         # Waiting for opponent's ping does not seems a good idea. Eitherway, in online games
         # there is a delay before moving to next phase.
         # waitForAnimation()
         # update()
         nextPhase(False)
      elif getStop(phase):
         addButton(NextButton)


def activatePhaseStart():
   """
   Unfreeze characters in the player's ring, clear colors and remove scripted markers.
   """
   myCards = getCards()
   frosted = []
   for card in myCards:
      if isCharacter(card):
         if not hasMarker(card, "Cannot Unfreeze"):
            freeze(card, unfreeze = True, silent = True)
         else:
            frosted.append(card)
         removeMarker(card, "Just Entered")
         removeMarker(card, "Counter-attack")
         clear(card)
         alignCard(card)
      # Discard any Action or Reaction card left in the table (just in case player forgot to remove them)
      else:
         discard(card)
   frostedChars = ""
   if frosted:
      frostedChars = " but {}".format(cardsAsNamesListStr(frosted))
   notify("{} unfreezes all characters in their ring{}.".format(me, frostedChars))
   # Trigger event
   dispatchEvent(GameEvents.ActivatePhase)
   cleanupGameEvents(RS_KW_RESTR_UYNT)
   # Add buttons
   if not settings["PhaseAuto"]:
      addButton(NextButton)


def drawPhaseStart():
   if settings["PlayAuto"]:
      if len(me.Deck) == 0 and len(players) > 1 and not tutorial:
         notify("{} has no cards in their deck and therefore can't draw.".format(me))
         notifyWinner(getOpp())
      else:
         draw()
   # Trigger event
   dispatchEvent(GameEvents.DrawPhase)
   alignCards()


def mainPhaseStart():
   alignCards()
   # Restore default game board
   table.board = ""
   if settings["PhaseAuto"]:
      addButton(NextButton)
   for card in table:
      card.target(False)


def attackPhaseStart():
   syncGlobalVars()
   discardKOedChars()
   if playerSide == 1:
      table.board = "attack1"
   else:
      table.board = "attack2"
   # In case going backwards and button was hence removed
   if settings["PhaseAuto"]:
      addButton(NextButton)
   for card in table:
      if card.controller == me:
         # Discard action cards I have played
         if isAction(card):
            discard(card)
         elif isCharacter(card):
            card.target(False)
            alignCard(card)


def blockPhaseStart():
   if tutorial or playerSide == -1:
      table.board = "block1"
   else:
      table.board = "block2"
   uattack = getGlobalVar("UnitedAttack")
   if settings["PlayAuto"]:
      # Pay the cost of the UA
      if len(uattack) > 0:
         # UA are made up of 1 lead and the followers, and the lead doesn't count for the size
         uaSize = len(uattack) - 1
         uaType = ["", "Double", "Triple"][uaSize] + " United Attack"
         uaTypeKw = "ua{}".format(len(uattack))
         if not payCostSP(uaSize * UAttackCost, uaType, "do a {}".format(uaType), uaTypeKw):
            notify("{} does not have enough SP to pay the {}.".format(me, uaType))
            prevPhase()
            return
         notify("{} has paid the cost of the {}.".format(me, uaType))
   dispatchEvent(GameEvents.BlockPhase)
   for card in getAttackingCards(me, True):
      dispatchEvent(GameEvents.Attacks, card._id, [card._id])
   alignCards()
   # Pass priority to opponent
   setState(None, "priority", getOpp()._id)


def endPhaseStart():
   syncGlobalVars()
   discardKOedChars()
   # Restore default game board
   table.board = ""

   # Freeze attacking characters
   freezeAtk = getRule("attack_freeze")
   myCards = getCards()
   for card in myCards:
      if isCharacter(card):
         alignCard(card)
         if freezeAtk and isAttacking(card) and not hasMarker(card, "Unfreezable"):
            freeze(card, unfreeze = False, silent = True)
      else:
         discard(card)

   # Calculates and applies attack damage
   blockers = getGlobalVar("Blockers")
   uattack = getGlobalVar("UnitedAttack")
   atkCards = getAttackingCards()
   for card in atkCards:
      dmg = getMarker(card, "BP")
      pdmg = 0  # Piercing damage
      isUA = len(uattack) > 0 and uattack[0] == card._id
      if isUA:
         # Adds the BP of the other chars that joined the UA
         for x in range(1, len(uattack)):
            pdmg += getMarker(Card(uattack[x]), "BP")
      # Attacker is blocked
      if card._id in blockers:
         blocker = Card(blockers[card._id])
         # Add attacking cards to action local variables & trigger a game event
         addTempVar("attacker", [card])
         addTempVar("uaBP", dmg + pdmg)
         dispatchEvent(GameEvents.Blocks, blocker._id, [blocker._id])
         # Wait until syncs among players is done
         update()
         # Trigger blocked event
         dispatchEvent(GameEvents.Blocked, card._id, [card._id])
         blockerBP = getMarker(blocker, "BP")
         dealDamage(dmg + pdmg, blocker, card)
         dealDamage(blockerBP, card, blocker)
         # Blocker damages to chars in the United Attack
         if isUA and blockerBP > dmg:
            newBP = blockerBP - dmg
            for x in range(1, len(uattack)):
               uacard = Card(uattack[x])
               restBP = getMarker(uacard, "BP") - newBP
               dealDamage(newBP, uacard, blocker)
               if restBP < 0:
                  newBP = abs(restBP)
               else:
                  break
         # Piercing damage of the United Attack
         uadmg = dmg + pdmg - blockerBP
         if (
               len(players) > 1 and
               getRule("piercing") and
               uadmg > 0 and
               (
                  # If the blocker has the ability preventpierce, the hook will return True
                  (isUA and triggerHook(Hooks.PreventPierce, blocker._id, [blocker._id]) != True)
                  # One does not simply stop Haohmaru
                  or hasMarker(card, "Pierce")
               )
            ):               
            dealDamage(uadmg, players[1], card, isPiercing = True)
         elif pdmg > 0 and uadmg > 0:
            notify("{} points of piercing damage were prevented.".format(uadmg))
      # Unblocked attacker
      elif len(players) > 1:
         doDamage = True
         if triggerHook(Hooks.CancelCombatDamage, card._id, [card._id]) == True:
            doDamage = False
         if doDamage:
            dealDamage(dmg + pdmg, players[1], card)
         dispatchEvent(GameEvents.PlayerCombatDamaged, card._id, [card._id])
      update() # Syncs the game state along players. Also delays animations.

   # Trigger event
   dispatchEvent(GameEvents.EndPhase)
      
   # Discard opponent reaction cards
   for card in table:
      if card.controller != me and isReaction(card):
         remoteCall(card.controller, "discard", [card])
   
   # Remove buttons?
   if settings["PhaseAuto"] and not atkCards:
      removeButton(NextButton)
   else:
      addButton(NextButton)


def cleanupPhaseStart():
   if settings["PhaseAuto"]:
      removeButton(NextButton)
   syncGlobalVars()
   discardKOedChars()
   waitForAnimation()
   clearAll()
   dispatchEvent(GameEvents.CleanupPhase)
   waitForAnimation()
   # Clean up my ring
   myCards = getCards()
   for card in myCards:
      if isCharacter(card):
         # Remove scripted makers
         removeMarker(card, "Attack")
         removeMarker(card, "United Attack")
         removeMarker(card, "Counter-attack")
         removeMarker(card, "Unfreezable")
         removeMarker(card, "Pierce")
         # Reset position
         alignCard(card)
      # Discard any Action or Reaction card left in the table (just in case player forgot to remove them)
      else:
         discard(card)
   # Remove events that should end when the turns finishes
   for restr in RS_KW_RESTRS_CLEANUP:
      cleanupGameEvents(restr)


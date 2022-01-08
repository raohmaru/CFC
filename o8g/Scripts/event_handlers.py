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

#---------------------------------------------------------------------------
# Event handlers
# https://github.com/octgn/OCTGN/wiki/OCTGN-Python-3.1.0.2-API-Reference#events
#---------------------------------------------------------------------------

def onTableLoaded():
   """
   Happens when the table first loads, and never again."""
   
   global settings
   try:
      strSettings = getSetting("settings", str(settings))
      settings.update(eval(strSettings))  # Merges other dict overwriting existing keys
      debug("Settings loaded: {}", settings)
   except:
      debug("Error loading settings}")
   checkTwoSidedTable()
   showWelcomeScreen()


def onGameStarted():
   """
   Triggers when the table initially loads, and after each game restart.
   """
   resetAll()
   chooseSide()
   if debugging:
      debugScenario()
   elif tutorial == True:
      startTutorial()
   elif settings["PlayAuto"]:
      addButton("StartButton")
   setAvatar()
   playSnd("new-game", True)


def onDeckLoaded(args):
   """
 	Triggers when a player loads a deck
   """
   mute()
   player = args.player
   groups = args.groups
   # We only want the owner of the deck to run this script
   if player != me:
      return
   debug(">>> onDeckLoaded({})", player)
   if len(player.Deck) != DeckSize:
      msg = "INVALID DECK: {}'s deck has {} cards (it must have exactly {} cards).".format(player, len(player.Deck), DeckSize)
      _extapi.notify(msg, Colors.Red)
      # Big notification for all players
      notification(msg, Colors.Red, True)
   cards = {}
   # Validate deck 
   for card in player.Deck:
      if card.model in cards:
         cards[card.model] += 1
      else:
         cards[card.model] = 1
      if cards[card.model] > MaxCardCopies:
         msg = "INVALID DECK: {0}'s deck has more than {1} copies of a card (only {1} copies are allowed).".format(player, MaxCardCopies)
         _extapi.notify(msg, Colors.Red)
         notification(msg, Colors.Red, True)  # Big notification for all players
   if settings["PlayAuto"]:
      setup()
   playSnd("load-deck")

      
def onCardsMoved(args):
   """
   Triggers when one or more cards are simultaneously moved from one location to another manually.
   """
   mute()
   cards = args.cards
   hand  = me.hand
   piles = me.piles
   CharsAbilities = getGlobalVar("CharsAbilities")
   MyRing = getGlobalVar("Ring", me)
   handChanged = False
   ringChanged = False
   abilitiesChanged = False
   
   for i in range(len(cards)):
      # Because Python is dynamic, accessing variables is faster than attribute lookup
      card      = cards[i]
      card_id   = card._id
      fromGroup = args.fromGroups[i]
      toGroup   = args.toGroups[i]
      markers   = args.markers[i]  # markers it's a string equivalent of the Marker object
      
      if card.controller != me:
         continue
      
      # debug("onCardsMoved: {} ({}) from {} to {}", card, card_id, fromGroup._name, toGroup._name)
      if isCharacter(card):
         # From the table to anywhere else
         if fromGroup == table and toGroup != table:
            clearAttachLinks(card)
            if charIsInRing(card):
               # Frees a slot of the ring
               MyRing[MyRing.index(card_id)] = None
               setGlobalVar("Ring", MyRing, me)
               ringChanged = True
               card.filter = None
            dispatchEvent(GameEvents.Removed, card_id)
            removeGameEventListener(card_id)
            # If it was attacking
            if "Attack" in markers:
               phaseIdx = getCurrentPhase()
               if phaseIdx == AttackPhase or phaseIdx == BlockPhase:
                  rearrangeUAttack(card)
            # Removes char from the modified abilities dict
            if card_id in CharsAbilities:
               del CharsAbilities[card_id]
               abilitiesChanged = True
         # Moved cards in the table
         elif fromGroup == table and toGroup == table:
            if card.position != (args.xs[i], args.ys[i]):
               if not hasMarker(card, "Backup"):
                  alignBackups(card, *card.position)
            playSnd("move-card-2")
         # From anywhere else to the table
         elif fromGroup != table and toGroup == table:
            if not ringChanged and charIsInRing(card):
               ringChanged = True
            if not card.isFaceUp:
               playSnd("move-card-1", True)
         # Movements in the same pile
         elif fromGroup == toGroup:
            playSnd("move-card-3", True)
            continue
      
      # Play some nice sounds
      if toGroup._name == "Hand":
         playSnd("to-hand")
      elif toGroup != table:
         # Movements in the same pile?
         if fromGroup == toGroup:
            playSnd("move-card-3", True)
         else:
            playSnd("move-card-1")
      
      # From the table to anywhere else
      if fromGroup == table and toGroup != table:
         deleteGameCard(card)
      
      # If card goes to a pile (not the table)
      if toGroup._name in piles:
         # Restore transformed card if it goes to a pile
         if card_id in transformed:
            newCard = toGroup.create(transformed[card_id], quantity = 1)
            newCard.moveTo(toGroup, card.index)
            notify("transformed card {} is restored into {}".format(card, newCard))
            del transformed[card_id]
            card.delete()
      if (
         (fromGroup == hand and toGroup != hand) or
         (fromGroup != hand and toGroup == hand)
      ):
         handChanged = True
         
   if abilitiesChanged:
      setGlobalVar("CharsAbilities", CharsAbilities)
   # Trigger events
   if handChanged:
      dispatchEvent(GameEvents.HandChanges, args = [len(me.hand)])
   if ringChanged:
      dispatchEvent(GameEvents.RingChanges, args = [getRingSize(ring = MyRing)])

   
def onTurnPassed(args):
   """
   Triggers when the player passes the turn to another player.
   """
   debug(">>> onTurnPassed: #{}, {} -> {}".format(turnNumber(), args.player, getActivePlayer()))
   global cleanedUpRing, turnsRemaining
   resetState()
   # That was my old turn
   if args.player == me:
      clearGlobalVar("UnitedAttack")
      clearGlobalVar("Blockers")
      # Force cleanup
      if not cleanedUpRing:
         triggerPhaseEvent(CleanupPhase)
      # Not repeating turn
      if not me.isActive:
         removeAllButtons()
   # I start my turn
   if me.isActive:
      cleanedUpRing = False
      turnsRemaining = 1
      # First turn of the game, I start
      if turnNumber() == 1:
         setState(None, "activePlayer", me._id)
      # Jump to the first phase
      if not debugging and getCurrentPhase() < ActivatePhase:
         nextPhase(False)
      playSnd("turn-change")
   if turnNumber() == 1:
      removeButton("StartButton")
   debug("<<< onTurnPassed()")


def onPhasePassed(args):
   """
   Triggers when the current game phase changes.
   """
   phaseIdx = getCurrentPhase()
   debug(">>> onPhasePassed: {} => {}", args.id, phaseIdx)
   if args.id == phaseIdx:
      return
   
   # Any player
   if phaseIdx == AttackPhase:
      if me.isActive:
         _extapi.whisper(MSG_HINT_ATTACK, Colors.Blue)
   if phaseIdx == BlockPhase:
      if me.isActive and len(getAttackingCards()) > 0:
         _extapi.whisper(MSG_HINT_BLOCK1.format("defending player", "he or she"), Colors.Blue)
      elif not me.isActive and len(getAttackingCards(getOpp())) > 0:
         setStop(BlockPhase, True)
         addButton("NextButton")
         msg1 = MSG_HINT_BLOCK1.format("you", "you")
         _extapi.whisper(msg1, Colors.Blue)
         _extapi.whisper(MSG_HINT_BLOCK2, Colors.Blue)
         notification(msg1 + " " + MSG_HINT_BLOCK2)
   elif phaseIdx == CleanupPhase:
      if me.isActive:
         if not settings["PhaseAuto"]:
            _extapi.whisper("This is the last phase of your turn.", Colors.Blue)
         global cleanedUpRing
         cleanedUpRing = True
   # Active player
   if me.isActive:
      if phaseIdx != ActivatePhase:
         playSnd("phase-change")
      elif turnNumber() == 1:
         playSnd("turn-change")
      gotoPhase(phaseIdx, args.id)


def onMarkerChanged(args):
   """
   Triggers when a card's markers change, for all players.
   """
   card = args.card
   if card.controller != me:
      return
   marker = args.marker
   oldValue = args.value
   debug(">>> onMarkerChanged: {}, {}, {}, {}", card, marker, oldValue, args.scripted)
   if marker == "BP":
      bp = getMarker(card, "BP")
      # scripted is true if the marker was changed via Python
      if args.scripted and settings["PlayAuto"]:
         # last BP before being KOed
         getGameCard(card).setState("lastBP", bp if bp > 0 else oldValue)
      if args.scripted or not settings["PlayAuto"]:
         if card.controller == me and isCharacter(card):
            if bp == 0:
               card.filter = KOedFilter
            elif hasFilter(card, KOedFilter):
               card.filter = None
   # Tint cards according to the markers
   elif marker in MarkerFilters:
      if args.scripted or not settings["PlayAuto"]:
         if card.controller == me and isCharacter(card):
            removeFilter = True
            for m, f in MarkerFilters.iteritems():
               if hasMarker(card, m):
                  card.filter = f
                  removeFilter = False
                  break
            if removeFilter:
               card.filter = None
   
   # Don't allow movement of markers
   if settings["PlayAuto"]:
      if not args.scripted and card.controller == me:
         if marker == "BP":
            bp = getMarker(card, "BP")
            fixedBP = fixBP(bp)
            if bp != fixedBP:
               setMarker(card, "BP", fixedBP)
         else:
            setMarker(card, marker, oldValue)


def OnCounterChanged(args):
   """
   Triggers when a player's counter value is adjusted.
   """
   debug(">>> OnCounterChanged: {}, {}, {}, {}", args.counter._player, args.counter._name, args.value, args.scripted)
   player = args.counter._player
   counterName = args.counter._name
   # Syncs with the custom GameState
   setState(player, counterName, player.counters[counterName].value)


def OnCardClicked(args):
   """
   Triggers when a player clicks a card.
   """
   card = args.card
   mouseButton = args.mouseButton
   if card and card.controller == me:
      if isButton(card) and mouseButton == 0:  # Left button
         debug(">>> OnCardClicked: {}, {}, {}", card, mouseButton, args.keysDown)
         buttonAction(card)
         

def onCardTargeted(args):
   """
   Triggers when a card is targeted, or de-targeted.
   """
   card = args.card
   targeted = args.targeted
   debug(">>> onCardTargeted: {} by {} ({})", card, args.player, targeted)
   # Disallow targeting UI cards
   if isUI(card) and targeted:
      card.target(False)

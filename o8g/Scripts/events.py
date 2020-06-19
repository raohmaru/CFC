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
# Event handlers
#---------------------------------------------------------------------------

def onTableLoaded():
# Happens when the table first loads, and never again.
   global settings
   try:
      strSettings = getSetting('settings', str(settings))
      settings.update(eval(strSettings))
      debug("Settings loaded: {}".format(settings))
   except:
      debug("Error loading settings}")
   checkTwoSidedTable()
   showWelcomeScreen()


def onGameStarted():
# Triggers when the table initially loads, and after each game restart.
   resetAll()
   chooseSide()
   if debugging:
      debugScenario()
   elif settings['Play']:
      addButton('StartButton')
      addAvatar()


def onDeckLoaded(args):
   mute()
   player = args.player
   groups = args.groups
   if player != me:  # We only want the owner of the deck to run this script
      return
   debug(">>> onDeckLoaded({})".format(player))
   notify("{} has loaded a deck.")
   if len(player.Deck) != DeckSize:
      msg = "INVALID DECK: {}'s deck has {} cards (it must have exactly {} cards).".format(player, len(player.Deck), DeckSize)
      _extapi.notify(msg, Colors.Red)
      notification(msg, Colors.Red, True)  # Big notification for all players
      # return
   cards = {}
   for card in player.Deck:
      if card.Name in cards:
         cards[card.Name] += 1
      else:
         cards[card.Name] = 1
      if cards[card.Name] > MaxCardCopies:
         msg = "INVALID DECK: {0}'s deck has more than {1} copies of a card (only {1} copies are allowed).".format(player, MaxCardCopies)
         _extapi.notify(msg, Colors.Red)
         notification(msg, Colors.Red, True)  # Big notification for all players
         # return
   if settings['Play']:
      setup(silent=True)
   playSnd('load-deck')

      
def onCardsMoved(args):
   mute()
   cards = args.cards
   hand  = me.hand
   piles = me.piles
   CharsAbilities = getGlobalVar('CharsAbilities')
   MyRing = getGlobalVar('Ring', me)
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
      
      # debug("onCardsMoved: {} ({}) from {} to {}".format(card, card_id, fromGroup._name, toGroup._name))
      
      if isCharacter(card):
         # From the table to anywhere else
         if fromGroup == table and toGroup != table:
            clearAttachLinks(card)
            if charIsInRing(card):
               # Frees a slot of the ring
               MyRing[MyRing.index(card_id)] = None
               setGlobalVar('Ring', MyRing, me)
               ringChanged = True
               card.filter = None
            triggerGameEvent([GameEvents.Removed, card_id])
            removeGameEventListener(card_id)
            if 'Attack' in markers:
               phaseIdx = currentPhase()[1]
               if phaseIdx == AttackPhase or phaseIdx == BlockPhase:
                  rearrangeUAttack(card)
            if card_id in CharsAbilities:
               del CharsAbilities[card_id]
               abilitiesChanged = True
         # Moved cards in the table
         elif fromGroup == table and toGroup == table:
            if card.position != (args.xs[i], args.ys[i]):
               if not hasMarker(card, 'Backup'):
                  alignBackups(card, *card.position)
         # From anywhere else to the table
         elif fromGroup != table and toGroup == table:
            if not ringChanged and charIsInRing(card):
               ringChanged = True
         # Movements in the same pile
         elif fromGroup == toGroup:
            continue
      
      if toGroup._name == 'Hand':
         playSnd('to-hand')
      elif toGroup != table:
         playSnd('move-card')
      
      # Restore transformed card if it goes to a pile
      if toGroup._name in piles:
         if card_id in transformed:
            newCard = toGroup.create(transformed[card_id], quantity = 1)
            newCard.moveTo(toGroup, card.index)
            notify("transformed card {} is restored into {}".format(card, newCard))
            del transformed[card_id]
            card.delete()
      if (
         not handChanged
         and (
            (fromGroup == hand and toGroup != hand) or
            (fromGroup != hand and toGroup == hand)
         )
      ):
         handChanged = True
         
   if abilitiesChanged:
      setGlobalVar('CharsAbilities', CharsAbilities)
   # Trigger events
   if handChanged:
      triggerGameEvent(GameEvents.HandChanges, len(me.hand))
   if ringChanged:
      triggerGameEvent(GameEvents.RingChanges, getRingSize(ring=MyRing))

   
def onTurnPassed(args):
# Triggers when the player passes the turn to another player.
   debug(">>> onTurnPassed: #{}, {} -> {}".format(turnNumber(), args.player, getActivePlayer()))
   global cleanedUpRing, turns
   resetState()
   # That was my old turn
   if args.player == me:
      clearGlobalVar('UnitedAttack')
      clearGlobalVar('Blockers')
      if not cleanedUpRing:
         triggerPhaseEvent(CleanupPhase)  # Force cleanup
      if not me.isActive:  # Not repeating turn
         removeButtons()
   # I start my turn
   if me.isActive:
      cleanedUpRing = False
      turns = 1
      # Jump to first phase
      if turnNumber() == 1:
         setState(None, 'activePlayer', me._id)
      if not debugging and currentPhase()[1] <= ActivatePhase or turnNumber() > 1:
         nextPhase(False)
      playSnd('turn-change')
   if turnNumber() == 1:
      removeButton('StartButton')
   debug("<<< onTurnPassed()")


def onPhasePassed(args):
   name, idx = currentPhase()
   debug(">>> onPhasePassed: {} => {}".format(args.id, idx))
   if args.id == idx:
      return
   
   # if idx == ActivatePhase:
   # elif idx == DrawPhase:
      # if turnNumber() == 1:
         # _extapi.whisper("(The player who goes first must skip his Draw phase during their first turn.)", Colors.Blue)
   # elif idx == MainPhase:
   # elif idx == AttackPhase:
   if idx == BlockPhase:
      if me.isActive and len(getAttackingCards()) > 0:
         _extapi.whisper(MSG_HINT_BLOCK.format('defending player', 'he or she'), Colors.Blue)
      elif not me.isActive and len(getAttackingCards(getOpp())) > 0:
         setStop(BlockPhase, True)
         addButton('NextButton')
         _extapi.whisper(MSG_HINT_BLOCK.format('you', 'you'), Colors.Blue)
         whisper("When done, press TAB key or click in the \"Block Done\" button to return priority to attacking player.")
   # elif idx == EndPhase:
   elif idx == CleanupPhase:
      if me.isActive:
         if not settings['Phase']:
            _extapi.whisper("(This is the last phase of your turn)", Colors.Blue)
         global cleanedUpRing
         cleanedUpRing = True
      
   if me.isActive:
      if idx != ActivatePhase:
         playSnd('phase-change')
      elif turnNumber() == 1:
         playSnd('turn-change')
      gotoPhase(idx, args.id)


def onMarkerChanged(args):
# Invoked on all players
   card = args.card
   if card.controller != me:
      return
   marker = args.marker
   oldValue = args.value
   debug(">>> onMarkerChanged: {}, {}, {}, {}".format(card, marker, oldValue, args.scripted))
   if marker == 'BP':
      qty = getMarker(card, 'BP')
      if args.scripted and settings['Play']:
         getParsedCard(card).lastBP = qty if qty > 0 else oldValue  # last BP before being KOed
      if args.scripted or not settings['Play']:
         if card.controller == me and isCharacter(card):
            if qty == 0:
               card.filter = KOedFilter
            elif hasFilter(card, KOedFilter):
               card.filter = None
   # Tint cards according to the markers
   elif marker in FiltersDict:
      if args.scripted or not settings['Play']:
         if card.controller == me and isCharacter(card):
            removeFilter = True
            for m,f in FiltersDict.iteritems():
               if hasMarker(card, m):
                  card.filter = f
                  removeFilter = False
                  break
            if removeFilter:
               card.filter = None
   
   # Don't allow movement of markers
   if settings['Play']:
      if not args.scripted and card.controller == me:
         if marker == 'BP':
            bp = getMarker(card, 'BP')
            fixedBP = fixBP(bp)
            if bp != fixedBP:
               setMarker(card, 'BP', fixedBP)
         else:
            setMarker(card, marker, oldValue)


def OnCounterChanged(args):
   debug(">>> OnCounterChanged: {}, {}, {}, {}".format(args.counter._player, args.counter._name, args.value, args.scripted))
   player = args.counter._player
   counterName = args.counter._name
   setState(player, counterName, player.counters[counterName].value)


def OnCardClicked(args):
   card = args.card
   mouseButton = args.mouseButton
   if card and card.controller == me:
      if isButton(card) and mouseButton == 0:  # Left button
         debug(">>> OnCardClicked: {}, {}, {}".format(card, mouseButton, args.keysDown))
         buttonAction(card)
         

def onCardTargeted(args):
   card = args.card
   targeted = args.targeted
   debug(">>> onCardTargeted: {} by {} ({})".format(card, args.player, targeted))
   if isUI(card) and targeted:
      card.target(False)


#---------------------------------------------------------------------------
# Overrides
#---------------------------------------------------------------------------

def overrideCardsMoved(args):
   cards     = args.cards
   toGroups  = args.toGroups
   indexs    = args.indexs
   xs        = args.xs
   ys        = args.ys
   faceups   = args.faceups
   phaseIdx  = currentPhase()[1]
   
   for i in range(len(cards)):
      card      = args.cards[i]
      fromGroup = card.group
      toGroup   = toGroups[i]
      index     = indexs[i]
      x         = xs[i]
      y         = ys[i]
      faceup    = faceups[i]
      # debug("overrideCardsMoved: {}: {} -> {}, [{}, {}] ({}) {}".format(card, fromGroup.name, toGroup.name, x, y, index, faceup))
      
      if isUI(card):
         continue
      
      if toGroup == table:
         if settings['Play']:
            # Play from hand
            if fromGroup == me.hand or (getRule('play_removed') and fromGroup.name == 'Removed pile'):
               # Play a character card
               if isCharacter(card):
                  slotIdx = getDropSlotIndex(x)
                  myRing = getGlobalVar('Ring', me)
                  if myRing[slotIdx] == None:
                     play(card, slotIdx=slotIdx)
                  else:
                     backup(card, target=Card(myRing[slotIdx]))
               # Play other type of card
               else:
                  play(card)
               continue
            # Move cards in table
            elif fromGroup == table:
               cy = card.position[1]
               # Attack
               if me.isActive and phaseIdx == AttackPhase and charIsInRing(card):
                  if (y>cy-60, y<cy+60)[bool(playerSide+1)]:
                     slotIdx = getDropSlotIndex(x)
                     if slotIdx == None:
                        continue
                     myRing = getGlobalVar('Ring', me)
                     # United Attack
                     if myRing[slotIdx] != None:
                        atkCard = Card(myRing[slotIdx])
                        if isAttacking(atkCard, False):
                           if isAttacking(card):
                              cancelAttack(card, True)
                           unitedAttack(card, targets=[atkCard])
                           continue
                     if hasMarker(card, 'Attack'):
                        alignCard(card)
                     else:
                        if hasMarker(card, 'United Attack'):
                           cancelAttack(card, True)
                        attack(card)
                     continue
                  # Cancel attack
                  elif isAttacking(card):
                     cancelAttack(card)
                     continue
               # Block
               elif (not me.isActive or tutorial) and phaseIdx == BlockPhase and charIsInRing(card):
                  if (y>cy-60, y<cy+60)[bool(playerSide+1)]:
                     slotIdx = getDropSlotIndex(x)
                     if slotIdx == None:
                        continue
                     slotIdx = fixSlotIdx(slotIdx, fix=True)
                     targets = None
                     oppRing = getGlobalVar('Ring', getOpp())
                     if oppRing[slotIdx] != None:
                        targets = [Card(oppRing[slotIdx])]
                     if hasMarker(card, 'Counter-attack'):
                        cancelBlock(card, True)
                     block(card, targets=targets)
                     continue
                  # Cancel block
                  elif hasMarker(card, 'Counter-attack'):
                     cancelBlock(card)
                     continue
         card.moveToTable(x, y, not faceup)
         card.index = index
      # Move cards to piles
      else:
         card.moveTo(toGroup, index)
         
         
def overrideTurnPassed(args):
# Triggers when the player clicks the green "Pass Turn" button on the player tabs.
   player = args.player  # The player the turn is being passed to
   setState(None, 'activePlayer', player._id)
   nextTurn(player)


#---------------------------------------------------------------------------
# Related functions
#---------------------------------------------------------------------------

def getDropSlotIndex(x):
   idx = None
   ox = 200
   cx = x + CardWidth/2
   for j in range(NumSlots):
      coordsX = CardsCoords['Slot'+`fixSlotIdx(j)`][0] + CardWidth/2
      diff = abs(coordsX - cx)
      if diff < ox:
         idx = j
         ox = diff
   return idx
   
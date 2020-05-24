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
   if debugging:
      debugScenario()


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
      card      = args.cards[i]
      card_id   = card._id
      fromGroup = args.fromGroups[i]
      toGroup   = args.toGroups[i]
      markers   = args.markers[i]  # markers it's a string equivalent of the Marker object
      
      if card.controller != me:
         continue
      
      debug("onCardsMoved: {} ({}) from {} to {}".format(card, card_id, fromGroup._name, toGroup._name))
      
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
            if not hasMarker(card, 'Backup'):
               alignBackups(card, *card.position)
         # From anywhere else to the table
         elif fromGroup != table and toGroup == table:
            if charIsInRing(card):
               ringChanged = True
      
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
# Reset some player variables at the start of each turn
   debug(">>> onTurnPassed({}, {})".format(args.player, turnNumber()))
   global cleanedUpRing, turns
   # That was my old turn
   if args.player == me:
      resetState()
      clearGlobalVar('UnitedAttack')
      clearGlobalVar('Blockers')
      if not cleanedUpRing:
         triggerPhaseEvent(CleanupPhase)  # Force cleanup
   # I start my turn
   elif args.player is not None:
      cleanedUpRing = False
      turns = 1
      playSnd('turn-change')
   debug("<<< onTurnPassed()")


def onPhasePassed(args):
   name, idx = currentPhase()
   debug(">>> onPhasePassed: {} => {}".format(args.id, idx))
   
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
         addButton('BlockDone')
         _extapi.whisper(MSG_HINT_BLOCK.format('you', 'you'), Colors.Blue)
         whisper("When done, press TAB key or click in the \"Done\" button to return priority to attacking player.")
   # elif idx == EndPhase:
   elif idx == CleanupPhase:
      if me.isActive:
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
         qty = oldValue - getMarker(card, marker)
         if qty < 100 and qty > -100:
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
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
# Utility class
#---------------------------------------------------------------------------

class RulesUtils():
   """ Class to handle the custom events that happens during the game """

   @staticmethod
   def getObjFromPrefix(prefix, target=None):
   # Returns an object of the game from the given prefix
      if prefix == RS_PREFIX_MY:
         return me
      if prefix == RS_PREFIX_OPP:
         return getOpp()
      if prefix == RS_PREFIX_CTRL and target:
         return target.controller
      if isPlayer(target):
         return target
      return None

   
   @staticmethod
   def getObjIdFromSuffix(suffix, rs):
   # Returns an object ID of the game from the given suffix
      if suffix == RS_SUFFIX_FROM_THIS or suffix == RS_SUFFIX_THIS:
         return str(rs.card_id)
      return ''


   @staticmethod
   def getZoneByName(name, target=None):
      prefix, name = RulesLexer.getPrefix(RS_PREFIX_ZONES, name)
      player = RulesUtils.getObjFromPrefix(prefix, target) or me
      zone = None

      if name in [RS_KW_ZONE_ARENA, RS_KW_ZONE_RING, RS_KW_ZONE_INFRONT]:
         zone = table

      elif name == RS_KW_ZONE_HAND:
         zone = player.hand

      elif name == RS_KW_ZONE_DECK:
         zone = player.Deck

      elif name == RS_KW_ZONE_DISCARDS:
         zone = player.piles['Discard pile']

      elif name == RS_KW_ZONE_REMOVED:
         zone = player.piles['Removed pile']

      debug("getZoneByName({}) => {}", name, zone)

      return zone


   @staticmethod
   def getCardsFromZone(zone, source=None):
   # Get all the cards from the given zone
      if isinstance(zone, basestring):
         prefix = ''
      else:
         prefix = zone[0]
         zone   = zone[1]
      player = RulesUtils.getObjFromPrefix(prefix) or me
      cards = []

      if zone == RS_KW_ZONE_ARENA or prefix == RS_PREFIX_SAME:
         cards = getRing()

      elif zone == RS_KW_ZONE_RING:
         cards = getRing(player)

      elif zone == RS_KW_ZONE_INFRONT:
         idx = getSlotIdx(source)
         if idx > -1:
            card = getCardAtSlot(idx, getOpp())
            if card:
               cards = [card]

      elif zone == RS_KW_ZONE_HAND:
         cards = [c for c in player.hand]

      elif zone == RS_KW_ZONE_DECK:
         cards = [c for c in player.Deck]

      elif zone == RS_KW_ZONE_DISCARDS:
         cards = [c for c in player.piles['Discard pile']]

      elif zone == RS_KW_ZONE_REMOVED:
         cards = [c for c in player.piles['Removed pile']]

      return cards


   @staticmethod
   def getTargetQty(str = None):
      if str is None:
         return
      if isNumber(str):
         return Struct(**{
            'min': int(str),
            'max': int(str)
         })
      if str == RS_KW_ANYNUM:
         return Struct(**{
            'min': 1,
            'max': RS_KW_ANYNUM
         })
      if str[:1] == RS_KW_RANDOM:
         samples = num(str[1:])
         if samples == 0:
            samples = 1
         return Struct(**{
            'random': True,
            'samples': samples
         })
         return
      arr = str.split(',')
      if len(arr) == 2:
         return Struct(**{
            'min': int(arr[0]),
            'max': int(arr[1])
         })


   @staticmethod
   def getTargets(target, source=None, msg=None, reveal=True):
      debug("Getting targets ({})", reveal)

      types    = target['types']
      zone     = target['zone']
      filters  = target['filters']
      pick     = target['pick']
      qty      = RulesUtils.getTargetQty(target['qty'])
      selector = target['selector']

      # If two or more targets, ask for a single target
      if len(types) > 1 and target['typeop'] == RS_OP_OR:
         # Check if there is any keyword in the target types
         kw_types = set(RS_KW_TARGETS) & set(types)
         if len(kw_types) > 0:
            debug("-- found %s types, player must choose one. (%s)" % (len(kw_types), list(kw_types)))
            options = [ABBR[t].title() if t in ABBR else t.title() for t in types]
            t = askChoice("Select a target:", options)
            if t == 0:
               return False
            types = [types[t-1]]
            debug("-- type selected: %s" % types)
            
      # Ask for a zone if there are multiple choices
      if zone[0] == RS_PREFIX_ANY:
         pile = askChoice("Choose a {}:".format(zone[1]), ["My {}".format(zone[1]), "Enemy's {}".format(zone[1])])
         if pile == 0:
            return False
         zone = list(zone)  # Make a copy of the list
         zone[0] = [RS_PREFIX_MY, RS_PREFIX_OPP][pile-1]

      # Get all the cards from the given zone
      debug("-- Getting all cards from zone %s" % ''.join(zone))
      cards = RulesUtils.getCardsFromZone(zone, source)
      debug("-- Retrieved %s cards" % len(cards))

      # Filter targets
      targets = []
      for type in types:
         # If kw is 'player' then must choose between himself or enemy
         if type == RS_KW_TARGET_PLAYER:
            if qty is not None and qty.random:
               type = random.choice(RS_KW_PLAYERS)
            else:
               t = askChoice("Select a player:", RS_KW_PLAYERS_LABELS)
               if t == 0:
                  return False
               type = RS_KW_PLAYERS[t-1]
         ftargets = RulesUtils.filterTargets(type, filters, zone, cards, source, msg, pick, qty, reveal)
         if ftargets:
            targets += ftargets
      
      if not targets and not pick:
         debug("-- maybe it's an expression?")
         res = evalExpression(types[0], True, getLocals())
         if res:
            return [res]
         return False

      # Select random cards
      if qty is not None and qty.random:
         samples = qty.samples
         if samples > len(targets):
            samples = len(targets)
         targets = random.sample(targets, samples)
         debug("-- Randomly selected {} card(s)", samples)
         
      # Apply a final selector
      if selector and targets:
         targets = RulesSelectors.applySelector(selector, targets)
         
      if not targets:
         whisper(MSG_ERR_NO_FILTERED_CARDS)
      # Draw an arrow between the source card and the targets
      elif reveal and source and isCard(source):
         for c in targets:
            # if isCard(c):
               # source.arrow(c)
               # update()
            if isPlayer(c):
               c = getAvatar(c)
            if c:
               source.arrow(c)
               update()

      return targets


   @staticmethod
   def filterTargets(type, filters, zone, cards, source=None, msg=None, pick=None, qty=None, reveal=True):
      debug("-- filter targets by type '%s' in zone %s" % (type, zone))
      targets = None
      if type == RS_KW_TARGET_THIS and source:
         targets = RulesFilters.applyFiltersTo([source], filters)
         if len(targets) == 0:
            targets = False
      # If target is a player
      elif type in RS_KW_TARGET_IS_PLAYER:
         targets = RulesUtils.filterPlayers(type, filters)
      else:
         # Filter cards with a target
         targets = RulesUtils.filterCards(type, filters, zone, cards, source, msg, pick, qty, reveal)

      if isinstance(targets, list):
         debug("-- {} target(s) retrieved:", len(targets))
         for i, t in enumerate(targets):
            if i < 10:
               debug("        {}", t)
            else:
               debug("        ...")
               break
      return targets


   @staticmethod
   def filterPlayers(type, filters):
      if isinstance(type, basestring):
         if type == RS_KW_TARGET_ME:
            arr = [me]
         elif type == RS_KW_TARGET_OPP:
            arr = [getOpp()]
         elif type == RS_KW_TARGET_PLAYERS:
            arr = [me]
            if len(players) > 1:
               arr.append(players[1])

      debug("-- applying {} filters to player {}", len(filters), arr)

      # Apply filters
      arr = RulesFilters.applyFiltersTo(arr, filters)

      if len(arr) == 0:
         whisper(MSG_ERR_NO_FILTERED_PLAYERS)
         return False

      return arr


   @staticmethod
   def filterCards(type, filters, zone, cards, source=None, msg=None, pick=None, qty=None, reveal=True):
      debug("-- applying %s filters to %s cards" % (len(filters), len(cards)))

      cards_f1 = cards
      choose = True
      minQty = 1
      maxQty = 1
      isCardName = False
      if qty is not None:
         if qty.max:
            minQty = qty.min
            maxQty = qty.max
         elif qty.random:
            choose = False

      # Check for type suffixes
      typeSuffix, type = RulesLexer.getSuffix(RS_SUFFIX_TYPES, type)
      if typeSuffix:
         debug("-- found suffix '%s' in '%s'" % (typeSuffix, type+typeSuffix))
         if typeSuffix == RS_SUFFIX_PLURAL:
            choose = False

      # Check for type prefixes
      typePrefix, type = RulesLexer.getPrefix(RS_PREFIX_TYPES, type)
      if typePrefix:
         debug("-- found prefix '%s' in '%s'" % (typePrefix, typePrefix+type))
         # Targeting other cards?
         if typePrefix == RS_PREFIX_OTHER:
            # Current card can't be selected
            card = source
            if card in cards_f1:
               debug(MSG_ERR_TARGET_OTHER, card)
               cards_f1.remove(card)
            
      # Type is a card name?
      if type[0] == RS_KW_NAME:
         isCardName = True
         type = type.strip(RS_KW_NAME)

      if type != RS_KW_ANY:
         attr = 'Subtype'
         if isCardName:
            attr = 'Name'
         elif type in RS_KW_CARD_TYPES:
            attr = 'Type'
         cardsByType = []
         exclude = typePrefix == RS_PREFIX_NOT
         debug("-- checking if any card %s %s '%s'" % ('does not match' if exclude else 'matches', attr, type))
         for c in cards_f1:
            cattr = getattr(c, attr).lower()
            if (exclude and cattr != type) or (not exclude and cattr == type):
               cardsByType.append(c)
         cards_f1 = cardsByType
         if len(cards_f1) > 0:
            debug( "      " + cardsAsNamesListStr(cards_f1))
         else:
            debug("      Nope")

      # Look for targeted cards
      if choose:
         cards_f2 = [c for c in cards_f1
            if c.targetedBy == me]
         if len(cards_f2) == 0:
            if len(cards_f1) == 0 and not reveal:
               return False
         else:
            if len(cards_f2) >= minQty and len(cards_f2) <= maxQty:
               cards_f1 = cards_f2
               choose = False
               debug("-- %s card(s) targeted" % len(cards_f1))

      # Apply filters
      cards_f1 = RulesFilters.applyFiltersTo(cards_f1, filters)

      # Force to pick cards
      if pick:
         if pick > 0:
            cards_f1 = cards_f1[:pick]
            debug("-- Picked {} card(s)", len(cards_f1))
         else:
            cards_f1 = cards_f1[pick:]
            debug("-- Picked {} card(s) from the bottom of {}", len(cards_f1), ''.join(zone))
         if qty is None:
            choose = False
      
      # Don't look for cards in this zone, there is only one card
      if zone[1] == RS_KW_ZONE_INFRONT:
         choose = False

      if choose:
         if len(cards_f1) == 0 and reveal != 'all':
            return False
         if not msg:
            msg = MSG_SEL_CARD_EFFECT if source else MSG_SEL_CARD
         sourceName = source.Name if source else ''
         # Quantity message
         qtyMsg = min(minQty, len(cards_f1))
         qtyPlural = pluralize(minQty)
         if qty is not None and qty.max == RS_KW_ANYNUM:
            maxQty = len(cards_f1)
         if minQty < maxQty:
            if minQty == 0:
               qtyMsg = "up to {}".format(maxQty)
            else:
               qtyMsg = "from {} to {}".format(minQty, maxQty)
            qtyPlural = 's'
         if type != RS_KW_ANY:
            qtyMsg = "{} {}".format(qtyMsg, type)
            
         # Last chance to select a card
         if len(cards_f1) > 1 or minQty == 0 or reveal:
            article = 'the'
            if zone[1] != RS_KW_ZONE_ARENA:
               article = "{}'s".format(getOpp()) if zone[0] == RS_PREFIX_OPP else 'your' 
            # Choose a ring if we need cards from the same ring
            if zone[0] == RS_PREFIX_SAME and len(players) > 1:
               ctrl = selectRing()
               if not ctrl:
                  return False
               cards_f1 = [c for c in cards_f1 if c.controller == ctrl]
               if ctrl != me:
                  article = "{}'s".format(getOpp())
            # Info message
            owner = article.replace('your', 'their')
            if pick:
               pickMsg = "the {} {} card{} of ".format('top' if pick > 0 else 'bottom', abs(pick), pluralize(abs(pick)))
               owner = pickMsg + owner
            notify(MSG_PLAYER_LOOKS.format(me, owner, zone[1]))
            title = msg.format(qtyMsg, qtyPlural, article, zone[1], sourceName)
            # If there aren't enough cards to select, just show the cards
            if len(cards_f1) <= minQty:
               showCardDlg(cards if reveal == 'all' else cards_f1, title, min=0, max=0)
            else:
               while True:
                  cards_sel = showCardDlg(cards if reveal == 'all' else cards_f1, title, min=minQty, max=maxQty)
                  if cards_sel == None or minQty == 0 or not reveal or len(set(cards_sel) & set(cards_f1)) >= 1:
                     if cards_sel == None:
                        notify(MSG_PLAYER_SELECTS_NONE.format(me, owner, zone[1]))
                     cards_f1 = cards_sel
                     break
                  title = 'Please ' + title[0].lower() + title[1:]
                  warning(title)
            if cards_f1:
               if isVisible(cards_f1[0]):
                  notify(MSG_PLAYER_SELECTS_NAMED.format(me, cardsAsNamesListStr(cards_f1)))
               else:
                  notify(MSG_PLAYER_SELECTS.format(me, len(cards_f1)))
         if cards_f1 == None and minQty != 0:
            return False

      # At this point there are not cards to which apply the effect, but the ability
      # is activated anyway
      if cards_f1 and len(cards_f1) == 0 and minQty != 0:
         notify(MSG_ERR_NO_CARDS)

      return cards_f1

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

"""
***RuleScript***
Case Insensitive

---------------------------------------------------
target = <qty> type <pick> [filters] @ zone
target? = ...

Defines a target used for all effects.
Only one target key is allowed.
? -> Target is optional and will always execute actions

qty:
   Values:
      integer
   Syntax:
      min
      [min],max
   Keywords:
      r[#]
      ** (any number of cards)

type:
   Operators:
      , (or)
   Values:
      Any Type: Character, Action, Reaction
      Any Subtype: Warrior, Pilot, Captain...
      A card name surrounded by double quotes (")
   Keywords:
      player
      me
      opp
      this
      * (any one card)
      all
   Prefixes:
      ^ (other)
      ! (not)
   Sufixes:
      s (plural) (valid on Type, Subtype, player or *)
   Default:
      *
      
pick:
   Values:
      Positive number (top of pile)
      Negative number (bottom of pile)

filters: (optional)
   Operators:
      , (or)
      & (and)
   Values:
      Any Type: Character, Action, Reaction
      Any Subtype: Warrior, Pilot, Captain...
   Keywords:
      bp =|>=|<= number || bp:lowest
      sp =|>=|<= number
      backedup
      backup
      attack
      uattack
      block
      blocked
      frozen
      fresh
      powerful
      powerless
      abinstant
      abtrigger
      abauto
   Prefixes:
      - (not)

zone: (optional)
   Keywords:
      arena (default)
      ring
      infront
      hand
      deck
      discards
      kill
   Prefixes:
      my (default)
      opp
      ctrl
      same (only applies to ring)
      any

---------------------------------------------------
action = {cost}: [[cond]] effect [& effect] to(target) restr; ...

Multiple action keys are allowed. If there are two or more, a dialog will be show to choose the action.
Several actions can be joined with ';'.
Effects in the same action are executed synchronously; actions are async.

cost: (optional)
   Keywords:
      F
      S | S(target)
      D | D(#|target)
      E | E(target)

cond: (optional)
   Keywords:
      may
      may 'Question'
      if expr (@see Expressions)
      
effect:
   Values:
      Effect command (followed by () with 0 or more parameters):
         damage(#|expr)
         swapPiles(pile1, pile2)
         shuffle([myDeck])
         destroy()
         reveal([pile])     # default: target
         discard([#|target])  # default: 1, zone: myHand
         rndDiscard([#])
         moveTo(zone [, pos] [, reveal])  # pos = signed int or '?'
         bp(#|x#|=#|expr)    # default target = this
         sp(#|=#|expr)  # default target = me
         hp(#|expr)     # default target = me
         playExtraChar()
         draw([#|expression])  # Default: 1
         steal()
         loseAbility()
         copyAbility(expr)
         swapAbilities()
         each(expr in group -> effect)  # effect context: group item
         transform(card name|expr)
         moveRestTo(zone)
         enableRule(rule)
         disableRule(rule)
         freeze([toggle])
         unfreeze()
         alterCost(cardtype, #)
         swapChars()
         moveToSlot()
         trash([#])     # default: 1
         prophecy([#])  # default: 1
         activate(expr)
         turns(#)  # unsiged int, target = current player
      Ability:
         Keywords:
            @see abilities
         Prefixes (mandatory):
            +
            -
   Operators:
      & (and)
      
to(): (optional)
   Parameters:
      A valid target or a expression
   Alias:
      target
   Default:
      current player or the card (depend on context)

to?(): Same as to(), but target is optional and will run next effect in the action
      
restr: (optional)
   Keywords:
      ueot
      unac
      uynt
   Prefixes:
      my (default)
      opp
      
---------------------------------------------------
abilities = ability [, ability]

Only one abilities key is allowed.

ability:
   Keywords:
      unblockable
      cantattack
      cantblock
      cantplayac
      cantplayre
      unlimitedbackup
      unfreezable
      pierce
      preventpierce
      rush
      frosted
      
---------------------------------------------------
auto = [~event[,event]~ | hook?] [[cond]] effect [& effect] to(target) restr; ...

Only one auto key is allowed.

event:
   Keywords:
      activatephase
      drawphase
      blockphase
      endphase
      cleanupphase
      handchanges
      ringchanges
      removed
      powerless
      backedUp
      playerCombatDamaged:[suffix]
      playerDamaged:[suffix]
      attacks:[suffix]
      blocks:[suffix]
      blocked:[suffix]
   Prefixes:
      my (default)
      opp
      any
   Suffixes:
      fromThis
      this
      any
      action
      
hook:
   Keywords:
      canBeBlocked:[suffix]
   Prefixes:
      @see auto:event:prefixes
   Suffixes:
      @see auto:event:suffixes

cond:
   @see action:cond
   Some conditions may create an event if there aren't any
   After an if condition, it there aren't any effect, the result of the condition may cancel or allow the event default action

effect:
   @see action:effect

to:
   @see action:to
   Default
      this card

restr:
   @see action:restr

---------------------------------------------------
requisite = target [&& target]

A list of targets that all must exist in order to execute the action.
@see target

---------------------------------------------------
vars = varname := value [; varname := value] 

Assigns a value to a variable, which will exists during the execution of the effects.

Several variables can be joined with ';'.

varname:
   A valid identifier
   
value:
   number
   string
   boolean
   A valid expression (@see Expressions)
   
   
Identifier:
   An identifier is a word that contain the character _ and/or any of the following character ranges: a-z, A-Z, 0-9.

---------------------------------------------------
label = "string"

A label to show in the "choose an action" dialog.
Value can be quoted or not. Case-sensitive.
@see action

---------------------------------------------------
Expressions:

A valid Python expression.
Available variables:
   tgt (current target)
   prevTgt
   -- players --
   me
   opp
   damagedPlayer
      .hp
      .sp
      .hand
         .size
      .ring
      .chars
      .damaged
      .lostSP
   -- piles --
   discarded
   trashed
   destroyed
   moved
   sacrificed
      .size
   -- cards --
   this
   attacker
   blocker
   trigger
      .bp
   -- bool --
   alone
   soloAttack
   oppLostSP   
   
   context: each()
      card
      character
      action
      reaction
   
Available functions:
   all group: expr   # context = group item
"""

RulesDict = {}

# Nina's WINGS
RulesDict['55b0c9ff-4b3a-4b08-adc1-f1b5e03adef9'] = """
auto = [[if me.hand.size == 0]] +unblockable
"""

# Ryu no Senshi's DRAGON TRANSFORM
RulesDict['48a07b48-7415-42e7-a3cd-6bae37c56489'] = """
action = {F}: damage(1) to(characters@oppRing)
"""

# Cap. Commando's CAPTAIN CORRIDOR
RulesDict['8ce9a56f-8c0c-49e7-879c-12179c63f288'] = """
action = {F}: damage(4) to(characters[frozen])
"""

# Mack Knife's GRAVE KEEPER
RulesDict['9c6b99fa-ff60-4d70-aee8-7e1eae6f29b7'] = """
action = {D}{F}: +cantblock to(character@oppRing) ueot
"""

# Shinjin Akuma's MASTERED DESTINY
RulesDict['9da88c0d-7915-43e2-a555-23ffbcf11226'] = """
action = swapPiles(deck,discards) & shuffle()
"""

# Blodia's ENERGY COST
RulesDict['b8a8653c-0286-4b05-a255-c436fd23132d'] = """
action = damage(3) to(me)
"""

# Jin Saotome's SAOTOME DYNAMITE
RulesDict['af43872e-e47d-4fe0-9b55-aedd8a0d0fc7'] = """
action = {S}: destroy() target(character@oppRing)
"""

# Zero Akuma's GIGA CRUSH
RulesDict['fd1a3f1c-7df1-443e-97b1-f093d66e74c9'] = """
action = reveal(hand) & discard(actions) & discard(reactions)
"""

# Regina's RADIO TRANSMITTER
RulesDict['0a8f39ff-6b21-4805-bafb-27c3f38d1986'] = """
auto = ~myEndPhase~ moveTo(ctrlHand) target(characters[bp>=8])
"""

# Cody (Alpha)'s BAD STONE
RulesDict['525d8365-c90e-491f-9811-1f23efbafccb'] = """
auto = oppCanBeBlocked:any? [[if attacker.bp > 3]]
"""

# Damn D's WHISTLE
RulesDict['66d424bb-e5da-4f61-b063-61efd1fc61a6'] = """
target? = character[bp<=5]@deck
action = {F}: reveal() & moveTo(hand) & shuffle()
"""

# Guy's HAYA-GAKE
RulesDict['2c1d8c60-0858-4524-adc1-e7596a4d08e0'] = """
auto = oppCanBeBlocked:this? [[if me.ring > 1]] # me.ring is opp.ring
"""

# Haggar's SPINNING LARIAT
RulesDict['be2728eb-0a2d-4f27-8cc5-3208d103b888'] = """
action = {F}: moveTo(ctrlDeck) target(characters[-backup]) & shuffle(myDeck) & shuffle(oppDeck)
"""

# Maki's FIGHTING SPIRIT
RulesDict['a9478fcd-e1e2-403b-b1e4-5076b342fd50'] = """
action = [[if alone]] bp(x2) target(this)
"""

# Lucifer's SACRIFICE
RulesDict['39b7d042-d2c5-4ff3-aad5-231bd3ccc9e7'] = """
action = {F}: destroy() target(^character@myRing); damage(prevTgt.BP) to(character)
"""

# Mech Zangief's ANTISOCIAL
RulesDict['365cddf9-f741-4a3e-bf07-de4b3eecc6d2'] = """
action = destroy() target(^character@myRing)
"""

# Ruby Heart's TAG ALONG
RulesDict['ee979882-67cc-4549-881c-8e158df495ce'] = """
action = [[if all card.bp <= 3 in me.chars]] playExtraChar()
"""

# Son Son's BUNSHIN
RulesDict['b8325eaa-1687-4d18-b1e7-6bf335e447c2'] = """
action = [[if me.hand.size < opp.hand.size]] draw(opp.hand.size - me.hand.size) target(me)
"""

# Mega Man's ENEMY'S ABILITY
RulesDict['7717e285-f824-4bfa-bd76-c0039c97190e'] = """
action = {F}: steal() target(^character)
"""

# Mega Man X's PARTS CHANGE
RulesDict['e367c942-342e-4434-a2d1-dd7188b2d15a'] = """
action = {D(action)}{F}: draw(2)
"""

# Rock's BOUKEN
RulesDict['aaf18dab-973f-4126-a47a-78798ec5058b'] = """
action = {F}: moveTo(oppDeck) target(*@hand); moveTo(hand) target(*<-1>@oppDeck)
"""

# Rock Man's ROCK BUSTER
RulesDict['1c986de3-bec5-430b-a661-ebbe9b20c20f'] = """
action = {S}: damage(3) to(characters)
"""

# Roll's OPERATE
RulesDict['91cb59bd-1e5a-472d-a410-8fa0e1698eb5'] = """
action = {F}: moveTo(myDeck, -1) target(character@myRing)
"""

# Roll Caskett's RECYCLED PARTS
RulesDict['81ec2067-daec-4678-b5fd-9ab13e410551'] = """
action = moveTo(hand) target(reaction@discards)
"""

# Roll-chan's ROLL BUSTER
RulesDict['47804cd4-2cc5-4aba-a4f8-393da73a5758'] = """
action = {F}: damage(2) to(characters)
"""

# Tron Bonne's HELP FROM KOBUN
RulesDict['8e8e0107-db05-4cb3-a912-af2b2dea92d9'] = """
auto = ~myDrawPhase~ draw() target(me)
"""

# Samanosuke's DEMON GAUNTLET
RulesDict['a68dc591-6976-4341-b8b9-1a7dc1c71775'] = """
action = reveal(hand) & each(card.bp <= 3 in me.hand -> bp(+2)) target(this)
"""

# Ayame's BUTTERFLY ILLUSION
RulesDict['33796f5f-c699-42e8-a084-fd28663f08ae'] = """
auto = ~activatePhase~ moveTo(hand) target(this)
"""

# Falcon's POWER STONE
RulesDict['6f733db6-883b-41f5-a657-4e19784d183c'] = """
action = {D(<r>)}{F}: bp(3) target(character)
"""

# Ryoma's BUSHIDO
RulesDict['3d5fb82c-2ad5-44e3-83e1-ef00f370c604'] = """
action = discard(all); moveTo(hand) target(<,2>*@myDiscards)
"""

# Omokane Saki's STAND-BY
RulesDict['c6ee2630-7f1a-4ac1-95f3-be8db970e855'] = """
target? = character@deck
action = {F}: reveal() & shuffle() & moveTo(deck)
"""

# Chris Redfield's DISORDER
RulesDict['38d6c7a8-7463-4aa6-88c4-13f725ada0be'] = """
action = [[if opp.ring >= 3]] damage(2) to(characters@oppRing)
"""

# Claire's DECOY
RulesDict['a25d74b5-8774-4729-8ac2-b820878241b9'] = """
action = {S}: moveTo(hand) target(<r>character@myDeck)
"""

# Jill's BERETTA
RulesDict['0b2c9e8a-5f9b-4ab5-a9b3-414f1154ce24'] = """
action = {F}: damage(1) to(opp,character@oppRing)
"""

# Jill Valentine's HANDGUN
RulesDict['163c9ec0-61d2-45ae-842b-15aba8cc61f8'] = """
action = {D(reaction)}{F}: damage(3) to(opp,character@oppRing)
"""

# Leon's CONFINEMENT
RulesDict['d5e70014-8a56-4d9b-8b06-0192bac3f0b8'] = """
action = {F}: +cantplayac to(opp) oppueot
"""

# Zombie's RESIDENT EVIL
RulesDict['80d411e3-c3df-486f-927f-1592d9db65de'] = """
action = {S}: transform(Zombie) target(character)
"""

# Akira's BROTHER SEARCH
RulesDict['1cd7580b-d396-496c-afac-bcd6da9c1f83'] = """
target = action<1>@deck
action = moveRestTo(discards) & reveal() & moveTo(hand)
"""

# Batsu's BOILING BLOOD
RulesDict['4bd333d6-f063-424e-8cf9-3512f96f23b4'] = """
auto = enableRule(ab_trigger_fresh)
"""

# Daigo's FINISH IT!
RulesDict['e6e46f83-d089-4762-8d8e-2a3252cfc9db'] = """
action = [[if opp.ring >= 3]] bp(x2) target(this)
"""

# Edge's MANIPULATION
RulesDict['e9c8e4ca-7d41-43c5-b427-f7e47125052e'] = """
action = steal() target(character@infront)
"""

# Hinata's GO FOR IT!
RulesDict['514717b1-432b-4da7-aa84-a751b996416f'] = """
action = bp(3) target(character)
"""

# Hyo's PULL THE PLUG
RulesDict['fb3d3a49-a1de-4887-9ea4-ec761426471e'] = """
action = {F}: loseAbility() target(character[powerful]@ring) & draw()
"""

# Kurow's MADNESS
RulesDict['d38dc1f6-4586-44f2-bacc-adb649f4d38f'] = """
auto = ~activatephase~ destroy()
"""

# Kyoko's MASSAGE
RulesDict['09dfc071-ce3a-448f-86fe-502bd5d1392b'] = """
action = unfreeze() target(characters[frozen]@ring)
"""

# Kyosuke's COOL
RulesDict['7abee6d7-1831-4090-b882-eee2fd3aa246'] = """
auto = alterCost(action, +2)
"""

# Momo's DADAKKO
RulesDict['9d92f2f0-7395-4f1e-bc32-99ec9c82c686'] = """
action = +cantplayre to(opp) ueot
"""

# Natsu's ENCOURAGEMENT
RulesDict['7e0c215c-72f6-4967-83a5-27491376280f'] = """
auto = ~activatephase~ bp(+2) to(characters[backedup])
"""

# Raizou's MEDDLER
RulesDict['c553b9d0-946a-4c61-bc9b-a4b074c49045'] = """
auto = alterCost(reaction, -3)
"""

# Roberto's GOAL KEEPER
RulesDict['6b1e210a-4846-419c-87f8-875aae812c6e'] = """
action = swapChars() target(<2>character@sameRing)
action = moveToSlot() target(character@sameRing)
"""

# Roy's BLESSED TWICE
RulesDict['770a55b0-f68d-46ce-bb52-23ec3372b92a'] = """
target = character
action = +unlimitedbackup ueot
"""

# Shoma's RI-RI-RI!
RulesDict['a7b36a01-dbb4-4442-aaf8-e415611581a9'] = """
auto = ~anyCleanupPhase~ moveTo(hand) target(this[block,blocked])
"""

# Tiffany's GROOVY KNUCKLES
RulesDict['40ef0410-798f-4d60-865b-9af14ed4e355'] = """
target = opp
action = rndDiscard()
"""

# Zaki's SUKEBAN
RulesDict['faa72b01-cf50-4cff-8b70-13245a7fa5df'] = """
action = [[if me.sp == 0]] sp(+11)
"""

# Bilstein's PLASMA POWER
RulesDict['c3bb69f7-4b77-469f-a9ff-79cca1e52574'] = """
action = {F}: draw(2) & discard()
"""

# Hayato's ASHURA
RulesDict['f232c282-6a03-436f-aae2-53f6988c6603'] = """
action = reveal(hand); each(action in me.hand -> bp(+2)) target(this); discard(actions)
"""

# June's PLASMA RING
RulesDict['f67a1f9b-29c7-4ccc-bb17-b80a1c25b67a'] = """
auto = disableRule(ab_trigger_act)
"""

# Rain's BACK OFF!
RulesDict['cb1440e1-42f7-47e5-92d5-2246d399bd64'] = """
action = moveTo(hand) target(character@myRing)
"""

# Akuma's SHUN-GOKU-SATSU
RulesDict['bc5e5159-fe3c-4324-97bb-2b56b920a6a3'] = """
action = destroy() target(character@infront)
"""

# Alex's SONIC HEADBUTT
RulesDict['c7c73d2e-1728-4c1b-ba7e-dcd989e61d98'] = """
auto = ~playerCombatDamaged:fromThis~ +cantplayac to(opp) oppueot
"""

# Blanka's ELECTRIC DISCHARGE
RulesDict['70df22cd-ebe5-461e-a017-26879f2cb71f'] = """
target = players
action = trash(5)
"""

# Cammy (Alpha)'s SPY
RulesDict['de28f9bf-d995-4743-afcd-a28065beb39d'] = """
action = moveTo(oppDeck, ?) target(*@oppHand)
"""

# Chun-Li's S.B. KICK
RulesDict['a124cd33-4427-4584-8216-885bbb97baa8'] = """
action = sp(=0); bp(=1) target(^characters)
"""

# Chun-Li (Alpha)'s GOMEN-NE!
RulesDict['7b9371dc-63a4-4dd8-91e9-5380aae0491f'] = """
action = moveTo(oppDiscards) target(<2>*<3>@oppDeck)
"""

# Dan's WHAT GIVES?
RulesDict['9d7ec580-fdc3-4222-92ec-10fd33741a2b'] = """
action = sp(-6) to(opp)
"""

# Dhalsim's ENLIGHTENMENT
RulesDict['9c383f6b-2813-407f-be87-f9746fbb6d18'] = """
target = *s@anyDeck
action = prophecy(1)
"""

# E. Honda's KAMIZU
RulesDict['3036ebcc-7b49-42a5-89f3-118399f34d47'] = """
target = players
action = draw(2)
"""

# Elena's HEALING
RulesDict['c023c0dd-677d-488a-83a6-2e9419bcb868'] = """
action = {D}{F}: hp(+2)
"""

# Evil Ryu's EVIL ENERGY
RulesDict['759b3fef-e5c0-406e-b186-a94b211e8735'] = """
action = destroy() target(character[frozen])
"""

# Gen's CHANGE SCHOOL
RulesDict['137d17e0-7c5a-4216-9085-21f05a744fd8'] = """
action = moveTo(deck) target(actions@discards) & shuffle()
"""

# Gill's ARAHITOGAMI
RulesDict['298bd386-e304-4739-95c6-78c9de4c17e4'] = """
action = {D(action)}{F}: destroy() target(character[powerless])
"""

# Guile's SOMERSAULT KICK
RulesDict['20cfabef-f733-478f-89d6-25a71371a89e'] = """
auto = disableRule(ab_instant_act)
"""

# Hugo's TOUGHNESS
RulesDict['3b05eb6f-d20f-433f-9ceb-4d6bb31d0328'] = """
auto = ~activatephase~ bp(=5)
"""

# Ibuki's HANA UTA
RulesDict['fd549399-59de-4b2c-8aca-5454f7862e50'] = """
requisite = character<1>@oppRing
action = {F}: bp(+3) target(character@oppRing); bp(+3) target(character@myRing)
"""

# Juli's PSYCHO CHARGE ALPHA
RulesDict['a2536791-c173-4228-84ce-4d2dec036ac3'] = """
action = {D(character)}{F}: sp(discarded[0].SP)
"""

# Karin's COMPENSATION
RulesDict['3eb68262-58ec-41c2-8fe0-b8284afc87fb'] = """
auto = ~blocked:this~ damage(2) to(opp)
"""

# Ken's RAGE WAVE
RulesDict['366963a0-6515-4b14-ae36-475b8000be26'] = """
abilities = unfreezable
"""

# M. Bison's EVIL CHARISMA
RulesDict['229cbb1b-9710-4981-b4ea-e476145d73f4'] = """
action = moveTo(hand) target?("Juni"&"Juli"<1>@myDeck) & shuffle(myDeck)
"""

# Makoto's YELL
RulesDict['216e0a0d-a46c-42f4-a0f4-c32ac83d6cc1'] = """
abilities = preventpierce
"""

# Oro's TENGU STONE
RulesDict['d8e2ad6f-32a1-46e2-b9cc-936dec91b919'] = """
auto = ~activatephase~ bp(+1)
"""

# Q's MYSTERIOUS ORIGIN
RulesDict['929afc04-8fc6-4419-80ec-0c9ead5ea105'] = """
target = players
auto = ~myEndPhase~ trash(2)
"""

# Remy's REVENGE
RulesDict['63df795b-236c-4449-aa96-287a836ed648'] = """
auto = ~activatephase~ each(card in me.hand -> sp(-1)); each(card in opp.hand -> sp(-1)) to(opp)
"""

# Rose's TAROT CARD
RulesDict['2a039849-7e43-43e2-b67a-2d341d27d9e1'] = """
action = draw(4) & discard(3)
"""

# Ryu's SHINKU HADOKEN
RulesDict['4f2454d7-2294-47a2-a473-a838c1f7d874'] = """
action = {D(2)}{F}: damage(5) to(character)
"""

# Ryu (Alpha)'s HADOKEN
RulesDict['03a6a70c-6f38-48b5-bcc0-4529ec0a18c2'] = """
action = {D}{F}: damage(3) to(character)
"""

# Sagat's TRUE POWER
RulesDict['2981e9ad-11e1-4f14-a707-2120bfc0cc2f'] = """
target = players
action = reveal(hand) & discard(actions)
"""

# Sakura's FIGHTING SPIRIT
RulesDict['f53e910f-8aef-47dc-a919-af81a5b0d2c4'] = """
action = [[if me.hp <= 10]] bp(x2) target(this)
"""

# Sean's SORE LOSER
RulesDict['7f5099da-4bcf-4895-9493-e83a993118b7'] = """
auto = ~myEndPhase~ [[if me.hand.size < opp.hand.size]] draw()
"""

# Twelve's X.C.O.P.Y.
RulesDict['e4ae5562-a510-4a1d-98e8-59a91dc1cb8c'] = """
auto = ~blocks:this~ bp(=attacker.bp)
"""

# Urien's DESPOT
RulesDict['79239cad-fd51-4557-9534-af96bd1302bc'] = """
target = opp
action = {F}: reveal(hand) & discard(reactions)
"""

# Option's SUPPORT
RulesDict['c3a432e3-3642-46a2-a1e2-e2d5d5f698ab'] = """
auto = enableRule(backup_fresh)
"""

# Strider Hiryu's CYPHER
RulesDict['c09e1c30-468b-4173-8aa8-3e6ba31cd3e8'] = """
action = {F}: destroy() target(character[backedup])
"""

# Kikaioh's FAIR PLAY
RulesDict['99081829-e898-4766-8727-b0a2918df49f'] = """
target = players
action = reveal(hand) & discard(reactions)
"""

# Anakaris's J.O.T.P.
RulesDict['9ec88c6c-dc57-41fd-bb90-cf2822a735aa'] = """
action = loseAbility() target(characters)
"""

# B. B. Hood's APPLE FOR YOU
RulesDict['d44d9e8a-785c-48f2-85a5-ed076c1aa518'] = """
action = {F}: destroy() target(^character); moveTo(deck) target(this) & shuffle()
"""

# Bishamon's REGRETFUL LOP
RulesDict['e778bf71-2f0f-4094-b096-b443fdbac8de'] = """
action = destroy() target(^characters@myRing); each(card in destroyed -> bp(+3))
"""

# Demitri's MIDNIGHT BLISS
RulesDict['563fbb65-90bc-43aa-9246-2f69e56ab119'] = """
action = {F}: destroy() target(character@myRing) & draw()
"""

# Donovan's CHANGE IMMORTAL
RulesDict['7f7fe518-3669-4dad-9063-79052f5067b7'] = """
action = {D}{F}: bp(+3)
"""

# Felicia's SIDEKICK ART
RulesDict['53eafaec-68bc-4fe8-88ee-be578a785f5c'] = """
action = {F}: moveTo(hand) target(<r>action@myDeck)
"""

# Hsien-Ko's DARK WEAPON
RulesDict['299377b4-f955-420b-b252-85ed6cf98c14'] = """
action = {F}: moveTo(deck); moveTo(deck) target(all@hand) & shuffle() & draw(3)
"""

# J. Talbain's SEETHING BLOOD
RulesDict['3a0e4fbc-6895-43e0-97d1-e1f667aca271'] = """
action = [[if opp.damaged]] bp(+3)
"""

# Jedah's P.D.C.
RulesDict['1d07a01b-e099-44a8-87eb-71fb2f3fa762'] = """
auto = ~playerCombatDamaged:fromThis~ draw()
"""

# Lilith's BECOMING ONE
RulesDict['60b0d429-c2bf-482d-84f1-10c78f424cc6'] = """
action = moveTo(deck) target(characters@discards) & shuffle()
"""

# Morrigan's LIFE SUCKER
RulesDict['4e34756e-34e4-45e5-a6ab-698604c6fb99'] = """
auto = ~playerCombatDamaged:fromThis~ hp(this.bp)
"""

# Morrigan Aensland's GOODNIGHT KISS
RulesDict['73e4c201-f462-4106-9e03-3b63ecd04aab'] = """
action = {S(character)}{F}: sp(+8)
"""

# Pyron's COSMO POWER
RulesDict['d646ffc5-bec9-4e98-b799-510b4e1ea464'] = """
auto = ~myEndPhase~ [[if me.sp < opp.sp]] sp(+3)
"""

# Q-Bee's PLUS B
RulesDict['65c91e9d-761c-4978-ba3e-6e05026f080e'] = """
action = moveTo(hand) target?("Q-Bee"s@myDeck) & shuffle(myDeck)
"""

# Rikuo's WETNESS
RulesDict['6c8ec7ed-2442-4847-8f38-8c8f5967b2ba'] = """
action = {F}: bp(+2) to(characters[backedup])
"""

# Kenji's MITTEI
RulesDict['487f66ee-c717-41a1-ad2e-31d3fe0dd424'] = """
action = moveTo(oppDiscards) target(*@hand); moveTo(hand) target(*<1>@oppDeck)
"""

# Tessa's SOLAR CANE
RulesDict['559c6131-7a72-47c7-9669-6a6c23a48cb7'] = """
action = {F}: alterCost(action, =0) unac
"""

# Eiji's PROPHECY
RulesDict['62067a74-53f9-4bb0-872c-f77e735fc826'] = """
action = prophecy(3)
"""

# Kasumi's OVERLAP CRUNCH
RulesDict['fc2e9e7c-98dc-4d46-b3ad-0f3ede2fd166'] = """
action = {D}{F}: damage(2) to(opp,character@oppRing)
"""

# King's DEALER
RulesDict['513f441d-fcec-4064-bbe6-152967cf38b8'] = """
action = discard(all); moveTo(hand) target(*@deck) & shuffle()
"""

# Mr. Big's BIG FREEBIE
RulesDict['d14dd0ed-cba6-404d-b7d1-e25c9b5c78ed'] = """
action = {D(character[powerful])}{F}: copyAbility(discarded[0]) to(character@myRing)
"""

# Mr. Karate's M.I.A.
RulesDict['06c4b88f-8634-4b67-87d0-c0406fa268f1'] = """
action = {F}: moveTo(deck) & shuffle() target(this)
"""

# Ryo's SPIRIT SURGE
RulesDict['952dc83f-9f22-4993-a824-707b0682753e'] = """
action = {D(action)}{F}: each(card in me.hand -> sp(+1))
"""

# Ryo Sakazaki's KOUKEN
RulesDict['d66622dd-27e3-4e3b-bb1f-245907ee3b66'] = """
action = moveTo(ctrlHand) target(character[abinstant])
"""

# Yuri's BRING IT ON!
RulesDict['3e1736d4-354b-4a5b-962a-4aea0a9e1a4b'] = """
action = {F}: sp(-3) target(opp)
"""

# Guy Tendo's LONELY RING
RulesDict['9aa78672-8e22-488a-ae4a-ce6c433f3216'] = """
auto = ~blockPhase~ [[if soloAttack]] bp(+2) target(this[attack])
"""

# Takato's AIKI
RulesDict['d5f9a649-cae0-46dc-b22c-139128ac8d52'] = """
auto = ~blocks:this~ draw(2)
"""

# God Rugal's YUUGOU POWER
RulesDict['067d592e-2ddf-43f5-82cc-25c70d29a996'] = """
target = character<1>[powerful]@anyDeck
action = moveRestTo(ctrlDeck, -1) & moveTo(ctrlDeck, -1, true); copyAbility(prevTgt) to(character)
"""

# Alfred's WAVE RIDER
RulesDict['3d044b8c-bac6-4b9a-bcf5-4868538de313'] = """
abilities = rush
"""

# Andy's SHADOW SLICER
RulesDict['299685df-122c-4fbe-a8dd-05ceaaf41055'] = """
target = opp
action = discard(<r>)
"""

# B. Jenet's LILIEN KNIGHTS
RulesDict['5ca6f345-403b-4ad9-973a-673b8cd1cdb8'] = """
action = reveal() & moveTo(hand) target?(character[bp<=3]@myDeck) & shuffle()
"""

# Billy's SHRIKE DROP
RulesDict['2e6f329d-9a1e-45b7-864d-67feeb5eade2'] = """
action = discard(<1>action) target(opp)
"""

# Blue Mary's MARY ARACHNID
RulesDict['6814ab83-c21d-4df9-8d07-e977ee27f131'] = """
action = {F}: +frosted target(character[frozen]@oppRing) oppueot
"""

# Duck King's DUCK DANCE
RulesDict['510c1217-5b95-467e-ae49-93fd5e726797'] = """
action = bp(3) target(character)
"""

# Gato's LOBOTOMY
RulesDict['f3557575-c61e-42fd-9442-9413cea64bdf'] = """
target = character
action = {F}: loseAbility() & bp(+3)
"""

# Geese's COMPOSURE
RulesDict['59253bbd-0dbd-4d43-9a2b-7f01b4bc1f76'] = """
action = reveal(hand) & discard(actions) & discard(reactions)
"""

# Geese Howard's REPPU KEN
RulesDict['526c4102-b6da-4880-91dc-1b9b007d4cc5'] = """
action = {F}: damage(this.bp) to(character@infront); moveTo(hand) target(this)
"""

# Grant's UNBREKABLE BOND
RulesDict['ae301f49-6e9d-4ca3-aba8-54bb5142e46d'] = """
action = {S}: hp(this.bp)
"""

# Griffon Mask's DAA!
RulesDict['d5038a1d-55a1-4d85-a43e-52eb2b8d7b09'] = """
action = bp(=this.bp) target(characters[bp:lowest])
"""

# Hokutomaru's FEAR ME
RulesDict['75e57026-e4fe-4470-88b2-22268ddd6b61'] = """
auto = oppCanBeBlocked:this? [[if blocker.bp <= this.bp]]
"""

# Hon Fu's KUURON NO YOMI
RulesDict['782a8773-1837-4d7a-8629-30ff08ccddca'] = """
auto = ~blocked:this~ draw()
"""

# Hotaru's ITOKATSU
RulesDict['928b8c60-483a-467c-9c11-e858009ff362'] = """
action = moveTo(deck) target(action@discards)
"""

# Jin Chonshu's FOGEY FISTS
RulesDict['b77da717-47d7-4dc1-bb79-cddecf0c5af5'] = """
action = {S(^character)}{F}: bp(+sacrificed[0].BP)
"""

# Joe's SCREW UPPER
RulesDict['8cb08852-491e-4a34-9589-79bf3959ba63'] = """
action = {F}: trash(2) target(opp)
"""

# Kain's RISOU
RulesDict['e81e9366-b3e1-45a6-b010-bd02934b2efd'] = """
auto = ~anyPlayerDamaged:action~ damage(1) to(damagedPlayer)
"""

# Kim's TRAINING!
RulesDict['38fcbdaf-0025-4692-adac-be99aa1be750'] = """
action = {F}: unfreeze() target(^character[frozen]@myRing)
"""

# Krauser's GIGANTIC CYCLONE
RulesDict['f286cc08-ae18-4a40-bd66-17aedcfd9267'] = """
action = destroy() target(^character@myRing)
"""

# Mai's MORPH
RulesDict['a33974af-3d8e-41d6-8f90-fd6c8d525e18'] = """
action = {F}: discard(all) & draw(discarded.size + 1)
"""

# Marco R.'s WAKE UP!
RulesDict['54d70bdf-7bfb-4c8a-8111-99b411513622'] = """
auto = ~anyCleanupPhase~ unfreeze() target(characters[frozen])
"""

# Raiden's MIKE APPEAL
RulesDict['bfb5d6cd-afca-4aeb-a1da-8204eb4b2eed'] = """
auto = ~anyBackedUp~ draw() to(trigger.controller)
"""

# Rock Howard's NEO DEADLY RAVE
RulesDict['b1082f22-34d1-4ecf-b972-261ace7b2a68'] = """
action = {S}: each(card in opp.hand -> damage(1)) to(opp)
# action = {S}: damage(opp.hand.size) to(opp)
"""

# Terry's TERRY RUSH
RulesDict['02157c40-3b96-480d-99c5-083613d8eb45'] = """
abilities = unfreezable
"""

# Terry Bogard's POWER GEYSER
RulesDict['eb648ee7-aa4e-41ce-a7fc-04af31349ca9'] = """
action = {D}{F}: destroy() target(character[bp>=8])
"""

# Wild Wolf's SORRY!
RulesDict['8995cad8-feaa-4704-9610-ae5e0dc6d800'] = """
action = {F}: moveTo(hand) target(<1>*<5>@deck); moveTo(discards) target(*<4>@deck)
"""

# Yamazaki's FACE OFF
RulesDict['8b6c2617-7c58-459c-b09f-63c86556d17e'] = """
action = freeze() target(character@infront)
"""

# Rosa's GET BACK!
RulesDict['51ad9363-8ba8-447b-bed5-b6e0e5f85ce8'] = """
action = moveTo(hand) target(character@myRing)
"""

# Athena Asamiya's PSYCHO CHARGE
RulesDict['08b229e2-6af7-478a-bda5-774dd66af9f9'] = """
action = {F}: sp(+3)
"""

# Benimaru's THUNDERGOD FIST
RulesDict['4f3dd284-fc50-4d11-8771-3154d2010845'] = """
requisite = character<1>@oppRing
action = {F}: damage(5) to(character@oppRing); damage(5) to(this)
"""

# Chizuru's CONTAIN!
RulesDict['55ab2891-c99e-4647-8a9d-b01fbce3009f'] = """
action = {D(action)}{F}: loseAbility() & bp(=1) target(character)
"""

# Choi's I'LL CUT YOU GOOD!
RulesDict['0d76ceeb-f809-464f-9954-240de260a132'] = """
action = discard(<1>reaction) target(opp)
"""

# Clone Zero's MIMIC
RulesDict['ab45b64f-e231-44ca-83ad-bd4d89bcb851'] = """
target = ^character[powerful]
action = copyAbility(prevTgt) to(this)
"""

# Heidern's STORM BRINGER
RulesDict['aa591fb7-0136-4af8-9229-9b6da2e02aca'] = """
auto = ~playerCombatDamaged:fromThis~ sp(-3) to(opp); sp(+opp.lostSP) to(me)
"""

# Hinako's HINAKO'S READY!
RulesDict['bbdd3687-7200-4f34-9c96-ed882cee3588'] = """
action = [[if me.hp <= 10]] draw(2)
"""

# Iori's BLOOD CONTRACT
RulesDict['4d7520b9-9ced-43e0-a2e7-974d76d8eb82'] = """
abilities = cantblock
"""

# Jhun Hoon's BROMIDE
RulesDict['eba4b6d7-1b14-4112-8e1e-6bee2017d338'] = """
action = {F}: draw(3) target(opp)
"""

# K's UNSTOPPABLE
RulesDict['78fc2eb4-f142-471b-83c0-1b615b67bb89'] = """
action = damage(3) to(^characters)
"""

# Kensou's MEAT MUFFIN!
RulesDict['a099049d-37ff-4c72-8691-a1bba86e506a'] = """
action = hp(+2)
"""

# Krizalid's DATA SHOCK
RulesDict['2ba9556c-59b0-4154-8325-f9793a8eacb5'] = """
action = {F}: copyAbility(this) to(^character); loseAbility() target(this)
"""

# Kula's EARLY THAW
RulesDict['1f11dc82-0581-49c2-ae93-35688c6acb7a'] = """
auto = enableRule(ab_trigger_fresh)
"""

# Kyo's OROCHI WAVE
RulesDict['0fa9c81d-eee6-47e9-9c9b-d4d802bca0c4'] = """
action = damage(5) to(opp)
"""

# Kyo Kusanagi's 182 WAYS
RulesDict['37af4395-3d1c-470a-b8e4-cefc39eaa27a'] = """
action = damage(3) to(opp,character@oppRing)
"""

# Leona's X-CALIBRE
RulesDict['835fc2ce-bbea-4798-b911-18cc8f1156c7'] = """
action = damage(2) to(^character)
"""

# Lin's DOKUSHU
RulesDict['30ecabeb-4da9-4e9c-a936-222b90532e78'] = """
auto = ~blocked:this~ sp(-3) to(opp)
"""

# Orochi's SANITY
RulesDict['e9c7f532-89ff-4f69-a885-bc09b549d989'] = """
action = sp(=0) target(players)
"""

# Rugal's GENOCIDE CUTTER
RulesDict['c0f1e98e-4233-446a-af2d-6e50eb8e6177'] = """
action = loseAbility() target(^character[powerful])
"""

# Saishu's EXORCISM
RulesDict['b25a11ac-1166-4868-990a-5113350f1502'] = """
action = damage(2) to(opp)
"""

# Shermie's GO EASY ON ME
RulesDict['672ac290-d6f2-4579-b5ae-1067add14601'] = """
action = +cantattack target(characters@oppRing) oppueot
"""

# Shingo's BURNING SHINGO!
RulesDict['f0163d6b-bd20-4737-a40b-c84ca19da681'] = """
requisite = character<1>@oppRing
action = {F}: damage(3) to(character@oppRing); damage(3) to(this)
"""

# Vanessa's FOOTWORK
RulesDict['0fdadc92-0864-46cc-a3ff-c20e2af8249c'] = """
auto = alterCost(reaction, +2)
"""

# Wild Iori's KURF
RulesDict['3e38ee5c-2421-4267-b0da-86035060fcc0'] = """
action = destroy() target(character[bp>=8])
"""

# Wild Leona's AWAKENING
RulesDict['ba027d6e-4bc2-4c0d-8e97-4ad1c3baf24c'] = """
action = damage(4) to(character)
"""

# Yashiro's COUNTERBLOW
RulesDict['0eeaf712-f3c6-4696-93cc-615c081b6cdd'] = """
action = moveTo(oppHand) target(character@infront)
"""

# Akari's PONTA LEAF
RulesDict['9c405677-1d42-4eb7-bb44-7b21c1d84859'] = """
action = {D(character)}{F}: bp(=discarded[0].bp)
"""

# Akari (Power)'s 100 DEMON NIGHT
RulesDict['03416225-8ed1-48fc-8178-c82559f61dcd'] = """
action = {F}: destroy() target(characters)
"""

# Akari (Speed)'s ONE-WAY MORPH
RulesDict['299c01d7-37f0-41de-81f3-712b8dd63f11'] = """
action = {D(character[abinstant])}{F}: activate(discarded[0])
"""

# Akari Ichijou's LET'S GAMBLE!
RulesDict['95675af9-956c-4b27-b7e1-a59b10a0cb7c'] = """
vars = coin := flipCoin()
action = {F}: [[if coin == 1]] bp(+5) target(character) [[else]] damage(3) to(this)
"""

# Awakened Kaede's POWER MATCH
RulesDict['da18d80a-ffa3-4df4-a3a7-7779bb5ad577'] = """
auto = ~activatephase~ sp(-2) to(players)
"""

# Kagami's PHOENIX
RulesDict['57de9ee8-5791-4696-96a1-057bf866ed9f'] = """
action = {S}: each(card in me.hand -> hp(+1))
"""

# Kojiroh's SHUNJIN
RulesDict['f3ddafb5-e6b5-4d07-b883-23cfe6ea6782'] = """
auto = disableRule(ab_instant_act)
"""

# Moriya's OBORO
RulesDict['9aac7225-cffe-452c-8b8f-e2382ff7219c'] = """
auto = ~activatephase~ damage(1) to(opp)
"""

# Mukuro's LIVING CORPSE
RulesDict['34f11eff-b3e2-4ac9-b505-a274eb5291c9'] = """
action = loseAbility() target(characters)
"""

# Setsuna's LIFE SIGN
RulesDict['781bd288-e9bf-4cf1-b630-0883a2834d0b'] = """
label  = "KO this character"
action = destroy()
label  = "Discard a character card"
action = discard(character)
"""

# Shigen's STEEL BULB
RulesDict['ddbfda17-0ba7-422e-9ed3-376a0ba64644'] = """
abilities = preventpierce
"""

# Wanderer's CHANGE!
# RulesDict['f71ccccf-4c2e-4adf-a409-b8ab8e17c8f1'] = ""

# Yuki's PRIESTESS SEAL
# RulesDict['48a553a1-fd40-482a-9161-86be2e29f246'] = ""

# Zantetsu's BYOUMA
RulesDict['5ccdb31f-f7f8-4f89-916f-74e9db9130cb'] = """
auto = ~myEndPhase~ damage(2) to(characters)
"""

# Eri's HOTHEAD
RulesDict['04660547-18c8-4eb4-96b5-2a977dda0dcb'] = """
action = [[if me.ring > 1]] moveTo(hand) target(this)
"""

# Marco's ENEMY CHASER
RulesDict['fa585a56-2a8f-48ff-9cc5-1234fecb4b09'] = """
action = {D(all)}{F}: each(card in discarded -> damage(1)) to(^characters)
"""

# Amakusa's GIVE YOURSELF
RulesDict['e590d588-84af-4c26-8dbe-e28d5b626747'] = """
action = destroy() target(^characters@myRing); each(card in destroyed -> sp(+5))
"""

# Asura's RISING EVIL
RulesDict['48aba37c-374b-4362-b30a-d41fa9727b2c'] = """
action = moveTo(deck) target(reactions@discards) & shuffle()
"""

# Cham Cham's PAKU PAKU
RulesDict['483b9441-d435-43a3-beb7-61e41c9e4045'] = """
action = {D(reaction)}{F}: draw(3)
"""

# Gaira's SHOUT!
RulesDict['40ece65c-0c59-4000-ab13-d948c4012f84'] = """
action = unfreeze() target(characters)
"""

# Galford's HEY POPPY!
RulesDict['494cb024-ef21-4019-98fe-9afc4355e424'] = """
action = draw()
"""

# Genan's PEEPING KAY!
RulesDict['1c7bc861-c4e0-4127-9fc8-fd56d06ec965'] = """
action = reveal(hand) target(opp)
"""

# Genjuro's I KNEW IT!
RulesDict['9a52f604-bf68-4ef4-934b-1c984877d484'] = """
abilities = cantblock
"""

# Hanzo's DUST CLOUD
RulesDict['90c1ccf4-999a-4567-92e4-0f7602b7799e'] = """
action = {F}: moveTo(hand) target(this)
"""

# Haohmaru's IRON SLICE
RulesDict['30eaa33f-ca59-4233-81b8-8fe3f0db94dd'] = """
abilities = pierce
"""

# Haohmaru (WR)'s GANKOU
RulesDict['bfb737c0-4dcf-4b0c-b201-45857c83016b'] = """
auto = ~myEndPhase~ loseAbility() target(character@infront)
"""

# Kazuki's IMBROGLIO
RulesDict['54c61d60-d68a-4ce8-8c2f-65bd0192c26a'] = """
action = {S}: damage(5) to(<r>character@oppRing)
"""

# Kyoshiro's WARRIOR DANCE
RulesDict['7b2a974c-de9b-4f42-a8da-f15b68dbc41c'] = """
action = bp(+1) target(characters@myRing)
"""

# Mikoto's RED EYES
RulesDict['ae20ea05-0df7-4360-99a5-11a7dfe44b9f'] = """
auto = ~attacks:this~ +cantplayre to(opp) ueot
"""

# Nakoruru's MAMAHAHA CALL
RulesDict['248517e9-d7a0-450d-9281-df91d20f68ab'] = """
action = {F}: draw()
"""

# Nakoruru (Bust)'s SHIKURO'S FANG
RulesDict['f3f105e5-a0b1-4b4b-9f88-5932182d3ace'] = """
auto = ~myEndPhase~ damage(2) to(characters[frozen]@oppRing)
"""

# Nakoruru (Slash)'s NATURE'S BALM
RulesDict['d231ed6e-8f7c-417e-8826-64f9297b395f'] = """
action = hp(+5)
"""

# Nicotine's EXORCISM CARD
RulesDict['37ccd6b2-dadc-48e2-91fa-da6c823293e9'] = """
auto = disableRule(ab_trigger_act)
"""

# Rimoruru's I'LL PUNISH YOU!
RulesDict['b428a15e-adf3-4fd1-897e-8dea39b8d9ca'] = """
action = {F}: damage(2) to(opp)
"""

# Rimoruru (Bust)'s KONRIL
RulesDict['537aa0e6-9231-423a-8aaa-3b9722cef6ec'] = """
action = {F}: freeze() target(character[-frozen]@oppRing)
"""

# Rimoruru (Slash)'s WIND WHISPER
RulesDict['e3c021d7-8ba2-471e-b74e-b5129da32f62'] = """
auto = ~myEndPhase~ hp(+1)
"""

# Seishiro's INEMURI
RulesDict['0f9e815a-d71a-4eba-9264-6e65c05fe8d7'] = """
abilities = frosted
"""

# Shiki's WISHING OF A SMILE
# RulesDict['235b8800-ad31-4224-93c2-4713ae4c45ec'] = ""

# Shiki (Bust)'s YUGA'S SPELL
RulesDict['9d836743-0d5e-4b4e-951a-cbe216558e6f'] = """
auto = alterCost(action, -3)
"""

# Shiki (Slash)'s NRG SYPHON
RulesDict['de04d64c-9d97-490f-a8c3-7469416bfc85'] = """
action = {F}: destroy() target(character@myRing); hp(+2)
"""

# Shizumaru's MIDSUMMER RAIN
# RulesDict['07fb9dba-ef83-4a69-a700-11cff3e313f3'] = ""

# Sougetsu's FRIGID SMIRK
# RulesDict['ce62aaad-d114-4ce6-842f-7f6ed39f1afa'] = ""

# Ukyo's DWINDLING LIFE
RulesDict['8bb3dd10-bb0f-4380-9772-c97ba0428378'] = """
auto = ~anyCleanupPhase~ destroy() target(this[attack,block])
"""

# The Ump's MYSTIC
RulesDict['e0c2ac67-1925-4e63-b9ae-9dcbc7ff229f'] = """
abilities = cantblock, cantattack
"""

# Athena's FIRE SWORD
# RulesDict['2f8ecb64-d513-4e67-b537-5acef9de6c68'] = ""

# Abduction
RulesDict['f7a00823-d37b-48eb-b2f6-c530623a2a9c'] = """
action = {S(<**>characters@myRing)}: each(card in sacrificed -> sp(+5))
"""

# Activate!
# RulesDict['e2597326-5639-435f-ae33-3303b181527c'] = ""

# Awakening
# RulesDict['80692723-3895-435f-bf8f-e94507704af5'] = ""

# Best shot
RulesDict['b0346de5-63b8-4443-8ea4-8155d889a0fc'] = """
action = moveTo(hand) target(<1>*<3>@deck); moveTo(discards) target(*<2>@deck)
"""

# Bopper
RulesDict['c50f1a40-87e9-41b9-a69c-600b36b68077'] = """
action = destroy() target(character@myRing); damage(prevTgt.BP) to(character)
"""

# Break up
RulesDict['4e493533-2d51-4af6-8a8e-ec55cb1b7ca5'] = """
action = destroy() target(characters[backedup])
"""

# Chaos
RulesDict['f215a022-c742-4c96-95d1-40c202f8d104'] = """
action = destroy() target(character@myRing); damage(3) to(characters)
"""

# Cover fire
RulesDict['713207f3-e051-43f8-9953-0a78e295122b'] = """
target = character
action = damage(3)
"""

# Crossover
# RulesDict['ab631979-20d8-4789-85be-149b414d1ef1'] = ""

# Curse
RulesDict['e1fb17f3-c4bf-4993-9b2f-91706cccf448'] = """
target = character<1>[powerful]@anyDeck
action = moveRestTo(ctrlDeck, -1) & moveTo(ctrlDeck, -1, true); copyAbility(prevTgt) to(characters)
"""

# Domination
# RulesDict['e5fa3d6f-3368-4450-8327-3f7672c78834'] = ""

# Double
RulesDict['4124ac7a-b7f5-4784-8246-872621cc9d95'] = """
target = character[frozen]@oppRing
action = +frosted oppueot
"""

# Double KO
RulesDict['e22264db-d58f-48ce-9be7-608bdfdd4299'] = """
action = destroy() target(character@myRing); destroy() target(character@oppRing)
"""

# Earth's pike
RulesDict['98e1e7ed-8c66-4105-a2fc-1290036c0f70'] = """
target = opp
action = damage(5)
"""

# Emulate
# RulesDict['053ba349-515d-4293-898b-625f837f62b6'] = ""

# Engokogeki
RulesDict['1ef4cecb-c096-47e0-995f-a20b6b75325a'] = """
target = opp
action = damage(1)
"""

# Escape
RulesDict['96c5cd74-a898-42f3-a169-9f98e1ce8945'] = """
target = character@myRing
action = moveTo(hand)
"""

# ESP
RulesDict['7b7ffef2-2790-46ed-8407-e7395c26b4a0'] = """
target = character[abtrigger]
action = copyAbility(prevTgt) to(character@myRing)
"""

# Fate duel
# RulesDict['3c92b6f8-d68f-4d0f-8a29-f5172b09a864'] = ""

# Fight!
RulesDict['b95b2104-d184-43cc-bb04-b3eb096c6fca'] = """
action = unfreeze() target(characters[frozen]@ring)
"""

# Glare off
RulesDict['faea0028-c313-438e-b9f0-8536e494ddb1'] = """
action = +cantattack target(characters) uynt
"""

# Grace
RulesDict['6597d835-666b-4056-8cae-dbf3a3bdc3df'] = """
action = hp(+5)
"""

# Grenade
RulesDict['26fa7e0e-eb86-40d5-b5ab-39723fd67e43'] = """
target = opp
action = damage(3)
"""

# Heritage
RulesDict['14a057f5-be46-4ec0-abee-a6c573f4711e'] = """
action = {S(<**>characters@myRing)}: each(card in sacrificed -> draw())
"""

# Hey! Hey!
RulesDict['c8284885-2ab1-4020-afc7-faae4e196e74'] = """
target = players
action = sp(=0)
"""

# Indulge
# RulesDict['6eec9528-7473-47a5-916b-a22261f79816'] = ""

# Last resort
# RulesDict['eece88a0-17d8-4b16-90b4-ac7317d36f95'] = ""

# Laundry
RulesDict['96f72173-528d-4a3a-a85c-9cf92439435a'] = """
action = target(all@discards) moveTo(deck) & shuffle()
"""

# Lightning
RulesDict['b7f9fdff-641d-4c16-b9fb-c7429b990fff'] = """
action = +unfreezable to(characters@myRing) ueot
"""

# Lucky kitty
RulesDict['9610668a-18c9-4448-8216-f40119a03269'] = """
action = draw(2)
"""

# Lunch rush
RulesDict['58580e2e-1f48-4210-a68f-57cd900b1036'] = """
action = reveal(hand) target(players); each(action in me.hand -> draw()); each(action in opp.hand -> draw()) target(opp)
"""

# Makeover
RulesDict['f6a32199-62df-49b5-8544-ae7a86915cbe'] = """
action = {F}: moveTo(deck) target?(all@hand) & shuffle() & draw(moved.size + 1)
"""

# Management
RulesDict['fd8db3d4-7df1-45fb-8712-5c35bb5acb3f'] = """
target? = action@deck
action = {F}: reveal() & shuffle() & moveTo(deck)
"""

# Mega crush
RulesDict['5d3bc1c3-692b-4d7c-9781-68fcdc0bd96e'] = """
target = characters
action = damage(5)
"""

# Mischief
RulesDict['7a394ff3-727d-48d9-91a9-b9cba90510b6'] = """
target = *s@anyDeck
action = prophecy(3)
"""

# Morph
# RulesDict['51a47b27-abf3-4219-a241-c72bd23b178b'] = ""

# No tricks
RulesDict['69cf51ab-090c-4c60-8b58-b71d6455f0a2'] = """
target = players
action = reveal(hand) & discard(!characters)
"""

# Nothingness
RulesDict['6c6fd560-017e-4819-accf-a66faef84218'] = """
target = characters[bp<=4]
action = destroy()
"""

# Peacemaker
RulesDict['153e2c26-7329-4a5e-a405-43191f75a2ac'] = """
requisite = character<1>@myRing && character<1>@oppRing
action = moveTo(hand) target(character@myRing); moveTo(oppHand) target(character@oppRing)
"""

# Pester
RulesDict['e8c43fc9-a217-49e6-9847-9c9ced63b0ac'] = """
action = trash(3) target(opp)
"""

# Pride
RulesDict['a8b949ff-7def-4c0a-8d79-49ad2a1d02d8'] = """
action = [[if me.hand.size > opp.hand.size]] discard(all) & draw(opp.hand.size) [[elif opp.hand.size > me.hand.size]] discard(all) & draw(me.hand.size) target(opp)
"""

# Psyche up!
RulesDict['11fa47f0-9573-48ca-9a4a-7aa16a4ec76e'] = """
action = sp(+5)
"""

# Puppet
RulesDict['0d1f3d2d-72ef-42e4-9c24-d0b36371b230'] = """
target = character
action = freeze(toggle)
"""

# Raw shield
RulesDict['50afc361-3dd7-4847-ae4c-d9ed84f1d991'] = """
action = {F}: destroy() target(character@myRing); hp(prevTgt.BP)
"""

# Reparation
RulesDict['a89ae46c-bbbe-4780-9a7f-3d68857047ac'] = """
target = character
action = moveTo(ctrlHand)
"""

# Reset button
RulesDict['85d84ab1-dede-4fc7-b80d-00778f73c905'] = """
action = freeze() target(characters@myRing) & turns(+1)
"""

# Revive
# RulesDict['5f19902c-60fb-44b8-9e64-eab4b31c9d3d'] = ""

# Roulette
# RulesDict['7f869cae-cf68-4d2d-881d-4f4107134469'] = ""

# Round 2
RulesDict['5ed66b91-2f3a-4fae-a1ba-ceb59040ea8c'] = """
action = discard(all) & draw(5)
"""

# School's out
RulesDict['0d7b5186-92db-4d61-8309-bfbd593df160'] = """
target = characters
action = moveTo(ctrlHand)
"""

# Seraphic wing
RulesDict['ac01bbbe-583e-46ae-b26c-3c25eb8f0779'] = """
target = characters[bp>=5]
action = destroy()
"""

# Shadow
RulesDict['0e1b4f81-93e9-44be-ab31-7aed8cb354d0'] = """
target = character<1>@anyDeck
action = moveRestTo(ctrlDeck, -1) & moveTo(ctrlDeck, -1, true); transform(prevTgt) to(character)
"""

# Shopping
RulesDict['0035d193-fe4b-4927-9dc1-6124b26768bc'] = """
action = {F}: moveTo(deck) target(<,3>*@discards) & shuffle() & draw()
"""

# Showtime!
# RulesDict['7302a3d9-0ee7-4a5e-93aa-b93cc44b6463'] = ""

# Slaughter
RulesDict['62a6c4e0-51d0-4a23-9854-9ba0a25bc751'] = """
target = characters
action = destroy()
"""

# SP partner
# RulesDict['37b88c5f-026b-40e4-bfd2-e5b7b83a7394'] = ""

# Stifler
RulesDict['77792408-ba0f-4e5f-a079-f7eca5955543'] = """
target = opp
action = discard(<1>*)
"""

# Storm rush
RulesDict['4d7fd45a-aa2a-48e3-856b-cfb04e203e3b'] = """
target = players
action = reveal(hand) & discard(characters)
"""

# Study
# RulesDict['c977a855-1358-4dab-870f-dee886f929c3'] = ""

# Substitute
RulesDict['6504b1a3-e432-4c6c-845b-6ca72500b458'] = """
action = swapAbilities() target(<2>character[powerful])
"""

# Successor
RulesDict['5e2211a0-e52e-4b7b-b03d-f6ecb3660bb0'] = """
action = {D(character[powerful])}: copyAbility(discarded[0]) to(character@myRing)
"""

# Synchro
RulesDict['83c33aa8-5981-4352-8107-cbb7e05547ec'] = """
action = moveTo(hand) target(*<1>@oppDeck); moveTo(oppHand) target(*<1>@deck)
"""

# Tooptadon
# RulesDict['fa4ee219-8264-41bc-b8a3-23a24df61d9a'] = ""

# Tri-Quiz
RulesDict['2d3891a7-6fc0-4793-9122-5abfc0bb3e22'] = """
action = damage(3) target(opp)
action = hp(+5)
action = bp(+2) to(characters@myRing)
"""

# Amnesia
RulesDict['b9023490-790e-4e5f-a495-c196f6672dff'] = """
target = characters
action = loseAbility()
"""

# Ancestry
# RulesDict['e038ebfd-6c19-4b1c-bf38-a2fd9f5ffbfd'] = ""

# Aura spark
RulesDict['be84124e-5057-4511-a181-7492451db5b2'] = """
target = character
action = each(characters[backedup] -> damage(3))
"""

# Bamboo shoots
RulesDict['826a8255-ed98-4c13-bb8c-96502837df52'] = """
action = each(card in opp.hand -> hp(+1))
"""

# Banquet
RulesDict['bc59a360-18f6-4c79-8305-77d0975d4106'] = """
action = hp(+5)
"""

# Cash profits
RulesDict['0a5179dd-e5a0-499e-90ac-8d62391743b8'] = """
target = <**>characters@myRing
action = moveTo(hand) & each(card in moved -> draw())
"""

# Charm
RulesDict['36450a2c-321b-4697-a37e-1563b16faf0e'] = """
action = disableRule(piercing) oppueot
"""

# Clone
RulesDict['74def9a7-0898-4ed4-93eb-33e57cf3a215'] = """
action = {D(character[powerful])}: copyAbility(discarded[0]) to(character@myRing)
"""

# Cruel hunt
RulesDict['fef1b38c-a055-4cd7-9436-34e220c30d52'] = """
target = characters[bp>=8 & attack]
action = destroy()
"""

# Evil eye
RulesDict['ed5b10af-ad01-4d70-bdac-0a7dfbf9de3f'] = """
action = {S(character@myRing)}: bp(=sacrificed[0].bp) target(character)
"""

# Face off
RulesDict['130c068d-bf62-4013-8b17-32af4a3f6994'] = """
action = draw(2); draw(3) target(opp)
"""

# Fellowship
RulesDict['2644337b-a5f8-4669-858b-824d9607f2d8'] = """
action = trash(10) & each(char in trashed -> sp(+1))
"""

# Ferocity
RulesDict['55dd552f-0c26-4bc1-819a-92cf32f285ae'] = """
action = {S(<**>characters@myRing)}: each(card in sacrificed -> damage(3)) to(characters)
"""

# Galactica phantom
# RulesDict['dd49c2e2-3455-481d-b8a7-5f813796b3f4'] = ""

# Go home
RulesDict['46deecf5-7f7b-42b5-b6fa-e3162dce2013'] = """
action = moveTo(deck) target?(reactions@discards) & shuffle() & draw()
"""

# Grandmaster
# RulesDict['5972ea54-137c-41a7-a1eb-b9d9cd0ecfe5'] = ""

# Held back
RulesDict['372525df-1345-47cc-ae2f-2fe34a226ac9'] = """
action = freeze() target(character[-attack & -uattack & -frozen]@oppRing)
"""

# Lend a hand
RulesDict['fd8b647c-9fc7-4c3a-bc91-ac5266e50a55'] = """
action = each(characters[attack] -> draw(2))
"""

# Lucky card
RulesDict['21db37a5-3483-41d4-9c6a-529071fce7ba'] = """
action = draw(3); moveTo(myDeck) target(<2>*@hand)
"""

# Manari's song
# RulesDict['2b3ad6cd-61d8-4786-9268-5963491a1ffa'] = ""

# Overdoing it
# RulesDict['556b3359-e642-419a-ab5c-67f70de1bb4f'] = ""

# Overheat
# RulesDict['27befc33-c2be-40d2-8839-bb8ee41f8d95'] = ""

# Painful treatment
# RulesDict['81b95f17-ba79-4f2f-aa7f-4808d6fad1ec'] = ""

# Power mode
RulesDict['559a71aa-0d14-44b0-bfb9-557d08ae0e0b'] = """
action = {D(2)}: bp(+5) target(character)
"""

# Reliable warrior
RulesDict['016a06d3-e739-4862-848a-d40ba0ec12ee'] = """
target = characters[frozen]@myRing
action = unfreeze()
"""

# Rest
RulesDict['2c9000df-e21a-4482-9dfc-8df3f702e29e'] = """
action = {D(character)}: sp(discarded[0].SP)
"""

# Robber
# RulesDict['eaf346c3-d2e6-4066-adae-e1678746673d'] = ""

# Robot punch
RulesDict['91e441cc-0f1f-4b01-a2b0-94678d6f0b56'] = """
target = character
action = damage(3)
"""

# Scan
RulesDict['1722e9d6-30e1-4355-9aa3-9b80b765754a'] = """
target = opp
action = {F}: reveal(hand); each(reaction in opp.hand -> draw(2)) target(me)
"""

# Snared
# RulesDict['30fdfea5-4781-40b8-a8e7-7830fba3bcd6'] = ""

# SP leak
RulesDict['68eaee28-a00a-480f-b8e5-e14d2a8f102c'] = """
action = sp(-5) to(opp)
"""

# Striker
RulesDict['f9a93f64-d331-4aa8-b58d-c213c8dfd742'] = """
action = {D(2)}: damage(+3) to(characters)
"""

# Super Art select
RulesDict['0a951ced-4508-40b9-8350-5dafb6b7e8aa'] = """
action = swapAbilities() target(<2>character[powerful])
"""

# Suspicious
RulesDict['3507e173-6329-4541-99fb-f4b81a482308'] = """
target = opp
action = {F}: reveal(hand) & discard(!characters)
"""

# Three sisters
RulesDict['76c3d3b5-b3bc-41b1-8fef-d9c005269646'] = """
action = {D(reaction)}{F}: draw(3)
"""

# Time bomb
RulesDict['48a11103-e08d-4237-952e-bf4cdc2868f7'] = """
action = {D(character)}: damage(discarded[0].BP) to(character[attack])
"""

# Vacation
# RulesDict['f4df6ee6-2fcd-4ba1-b86f-59d5028eb96b'] = ""

# Waiting in vain
# RulesDict['1e54d73a-4795-4eae-b1d1-c0ca5d075fcf'] = ""

# Wanna gimme
RulesDict['c6acfab6-c7cb-442e-87f0-432779af5ad9'] = """
target? = *@deck
action = {F}: shuffle() & moveTo(deck)

"""

# Who's taller
RulesDict['2298624c-1eeb-4f71-b028-b0118ea614ac'] = """
action = [[if me.hand.size < opp.hand.size]] discard(all) & draw(opp.hand.size) [[elif opp.hand.size < me.hand.size]] discard(all) & draw(me.hand.size) target(opp)
"""
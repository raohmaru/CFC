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

#------------------------------------------------------------------------------
# Debugging
#------------------------------------------------------------------------------

def debug(msg, level = 1):
   if debugVerbosity < DebugLevel.Info:
      return
   if debugVerbosity >= level:
      msg = "{}".format(msg)
      msg = DebugLevelPrefixes[level] + ' ' + msg
      whisper(msg)
   

def debugScenario():
   debug(">>> debugScenario()") #Debug
   
   if turnNumber() == 0: 
	   nextTurn(me, True)
   
   global debugVerbosity
   debugVerbosity = DebugLevel.All
   me.SP = 50
   chooseSide()
   gotoMain()
   rnd(100, 10000)  # Delay the next action until all animation is done
   tableCards = [
       'd66622dd-27e3-4e3b-bb1f-245907ee3b66' # Ryo Sakazaki
      ,'3e1736d4-354b-4a5b-962a-4aea0a9e1a4b' # Yuri
      ,'526c4102-b6da-4880-91dc-1b9b007d4cc5' # Geese Howard
      ,'0eeaf712-f3c6-4696-93cc-615c081b6cdd' # Yashiro
   ]
   for i, id in enumerate(tableCards):
      debug("Creating card {} at slot {}".format(id, i))
      card = table.create(id, 0, 0, quantity=1, persist=True)
      playAuto(card, i)
      ability = Ability(card)
      if ability.type and ability.type != InstantAbility:
         card.markers[MarkersDict['Just Entered']] = 0
      state['charsPlayed'] = 0
      rnd(1, 100)  # Delay the next action until all animation is done
      
   handCards = [
       '04660547-18c8-4eb4-96b5-2a977dda0dcb' # Eri
      ,'90c1ccf4-999a-4567-92e4-0f7602b7799e' # Hanzo
      ,'96c5cd74-a898-42f3-a169-9f98e1ce8945' # Escape
      ,'153e2c26-7329-4a5e-a405-43191f75a2ac' # Peacemaker
      ,'a89ae46c-bbbe-4780-9a7f-3d68857047ac' # Reparation
      ,'0d7b5186-92db-4d61-8309-bfbd593df160' # School's out
      # ,'248517e9-d7a0-450d-9281-df91d20f68ab' # Char 500 BP
      # ,'eb648ee7-aa4e-41ce-a7fc-04af31349ca9' # Char 700 BP
      # ,'4d7520b9-9ced-43e0-a2e7-974d76d8eb82' # Char 1000 BP
      # ,'5e2211a0-e52e-4b7b-b03d-f6ecb3660bb0' # Action 0 SP
      # ,'83c33aa8-5981-4352-8107-cbb7e05547ec' # Action -1 SP
      # ,'b95b2104-d184-43cc-bb04-b3eb096c6fca' # Action -2 SP
      # ,'ac01bbbe-583e-46ae-b26c-3c25eb8f0779' # Action -6 SP
      # ,'556b3359-e642-419a-ab5c-67f70de1bb4f' # Reaction 0 SP
      # ,'46deecf5-7f7b-42b5-b6fa-e3162dce2013' # Reaction -1 SP
      # ,'91e441cc-0f1f-4b01-a2b0-94678d6f0b56' # Reaction -4 SP
   ]
   for id in handCards:
      debug("Adding card {} to hand".format(id))
      card = table.create(id, 0, 0, quantity=1, persist=True)
      card.moveTo(me.hand)
      # rnd(1, 100)  # Delay the next action until all animation is done
   
   deckCards = [
       # '55ab2891-c99e-4647-8a9d-b01fbce3009f' # Char 300 BP
      # ,'55ab2891-c99e-4647-8a9d-b01fbce3009f' # Char 300 BP
      # ,'248517e9-d7a0-450d-9281-df91d20f68ab' # Char 500 BP
      # 'eb648ee7-aa4e-41ce-a7fc-04af31349ca9' # Char 700 BP
      # ,'4d7520b9-9ced-43e0-a2e7-974d76d8eb82' # Char 1000 BP
      # ,'5e2211a0-e52e-4b7b-b03d-f6ecb3660bb0' # Action 0 SP
      # ,'83c33aa8-5981-4352-8107-cbb7e05547ec' # Action -1 SP
      # ,'b95b2104-d184-43cc-bb04-b3eb096c6fca' # Action -2 SP
      # ,'ac01bbbe-583e-46ae-b26c-3c25eb8f0779' # Action -6 SP
      # ,'556b3359-e642-419a-ab5c-67f70de1bb4f' # Reaction 0 SP
      # ,'46deecf5-7f7b-42b5-b6fa-e3162dce2013' # Reaction -1 SP
      # ,'91e441cc-0f1f-4b01-a2b0-94678d6f0b56' # Reaction -4 SP
   ]
   for id in deckCards:
      debug("Adding card {} to Deck".format(id))
      card = table.create(id, 0, 0, quantity=1, persist=True)
      card.moveTo(me.deck)
      # rnd(1, 100)  # Delay the next action until all animation is done
   
   discardCards = [
      #  '365cddf9-f741-4a3e-bf07-de4b3eecc6d2' # Char
      # ,'d14694b4-484c-4b45-962e-8cbb636d8a9a' # Char
      # ,'8ce9a56f-8c0c-49e7-879c-12179c63f288' # Char
      # ,'61ef9ecd-980b-46b8-83fc-12399ce044f1' # Char
      # ,'0a8f39ff-6b21-4805-bafb-27c3f38d1986' # Char
      # ,'525d8365-c90e-491f-9811-1f23efbafccb' # Char
      # ,'bdeceb7c-9d94-4c98-824b-90d5317d8cda' # Char
      # ,'e94aaa00-2449-46a4-9ff4-273e6dac272a' # Char
      # ,'85d84ab1-dede-4fc7-b80d-00778f73c905' # Action
      # ,'ac01bbbe-583e-46ae-b26c-3c25eb8f0779' # Action
      # ,'556b3359-e642-419a-ab5c-67f70de1bb4f' # Reaction
      # ,'91e441cc-0f1f-4b01-a2b0-94678d6f0b56' # Reaction
   ]
   for id in discardCards:
      debug("Adding card {} to Discard pile".format(id))
      card = table.create(id, 0, 0, quantity=1, persist=True)
      card.moveTo(me.piles['Discard Pile'])
      # rnd(1, 100)  # Delay the next action until all animation is done
      
   if len(players) > 1:
      update()
      remoteCall(players[1], "debugOpp", [])
      
   debug("<<< debugScenario()") #Debug
   
   
def debugOpp():
   tableCards = [
       'd14694b4-484c-4b45-962e-8cbb636d8a9a' # 200 BP
      ,'ff8a97e3-9a78-4c5f-86fa-23480fa57da5' # 400 BP
      ,'24e99a13-cb42-4e16-9900-78dde12e1a4c' # 600 BP
      ,'e6e46f83-d089-4762-8d8e-2a3252cfc9db' # 1000 BP
   ]
   for i, id in enumerate(tableCards):
      card = table.create(id, 0, 0, quantity=1, persist=True)
      playAuto(card, i, True)
      state['charsPlayed'] = 0
      rnd(1, 100)  # Delay the next action until all animation is done
      
   handCards = [
       # '55ab2891-c99e-4647-8a9d-b01fbce3009f' # Char 300 BP
      # ,'248517e9-d7a0-450d-9281-df91d20f68ab' # Char 500 BP
      # ,'eb648ee7-aa4e-41ce-a7fc-04af31349ca9' # Char 700 BP
      # ,'4d7520b9-9ced-43e0-a2e7-974d76d8eb82' # Char 1000 BP
      # '5e2211a0-e52e-4b7b-b03d-f6ecb3660bb0' # Action 0 SP
      # ,'83c33aa8-5981-4352-8107-cbb7e05547ec' # Action -1 SP
      # ,'b95b2104-d184-43cc-bb04-b3eb096c6fca' # Action -2 SP
      # ,'ac01bbbe-583e-46ae-b26c-3c25eb8f0779' # Action -6 SP
      # ,'556b3359-e642-419a-ab5c-67f70de1bb4f' # Reaction 0 SP
      # ,'46deecf5-7f7b-42b5-b6fa-e3162dce2013' # Reaction -1 SP
      # ,'91e441cc-0f1f-4b01-a2b0-94678d6f0b56' # Reaction -4 SP
   ]
   for id in handCards:
      card = table.create(id, 0, 0, quantity=1, persist=True)
      card.moveTo(me.hand)
   
   deckCards = [
       # '55ab2891-c99e-4647-8a9d-b01fbce3009f' # Char 300 BP
      # ,'55ab2891-c99e-4647-8a9d-b01fbce3009f' # Char 300 BP
      # ,'248517e9-d7a0-450d-9281-df91d20f68ab' # Char 500 BP
      # ,'eb648ee7-aa4e-41ce-a7fc-04af31349ca9' # Char 700 BP
      # '4d7520b9-9ced-43e0-a2e7-974d76d8eb82' # Char 1000 BP
      # ,'5e2211a0-e52e-4b7b-b03d-f6ecb3660bb0' # Action 0 SP
      # ,'83c33aa8-5981-4352-8107-cbb7e05547ec' # Action -1 SP
      # ,'b95b2104-d184-43cc-bb04-b3eb096c6fca' # Action -2 SP
      # ,'ac01bbbe-583e-46ae-b26c-3c25eb8f0779' # Action -6 SP
      # ,'556b3359-e642-419a-ab5c-67f70de1bb4f' # Reaction 0 SP
      # ,'46deecf5-7f7b-42b5-b6fa-e3162dce2013' # Reaction -1 SP
      # ,'91e441cc-0f1f-4b01-a2b0-94678d6f0b56' # Reaction -4 SP
   ]
   for id in deckCards:
      card = table.create(id, 0, 0, quantity=1, persist=True)
      card.moveTo(me.deck)
      

def debugBackups():
   backups = getGlobalVar('Backups')
   debug("BACKUPS ({})".format(len(backups)))
   for id in backups:
      debug("   {} backups {}".format(Card(id), Card(backups[id])))
   
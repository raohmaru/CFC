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
   
   global charsPlayed, debugVerbosity
   debugVerbosity = DebugLevel.All
   me.SP = 50
   chooseSide()
   gotoMain()
   rnd(100, 10000)  # Delay the next action until all animation is done
   tableCards = [
       '66d424bb-e5da-4f61-b063-61efd1fc61a6' # Damn D
      ,'1cd7580b-d396-496c-afac-bcd6da9c1f83' # Akira
      ,'5ca6f345-403b-4ad9-973a-673b8cd1cdb8' # B. Jenet
      # ,'53eafaec-68bc-4fe8-88ee-be578a785f5c' # Felicia
   ]
   for i, id in enumerate(tableCards):
      debug("Creating card {} at slot {}".format(id, i))
      card = table.create(id, 0, 0, quantity=1, persist=True)
      playAuto(card, i)
      ability = Ability(card)
      if ability.type and ability.type != InstantAbility:
         card.markers[MarkersDict['Just Entered']] = 0
      charsPlayed = 0
      rnd(1, 100)  # Delay the next action until all animation is done
      
   handCards = [
       '65c91e9d-761c-4978-ba3e-6e05026f080e' # Q-Bee
      ,'5ca6f345-403b-4ad9-973a-673b8cd1cdb8' # B. Jenet
      ,'de28f9bf-d995-4743-afcd-a28065beb39d' # Cammy (Alpha)'s SPY
      ,'91cb59bd-1e5a-472d-a410-8fa0e1698eb5' # Roll's OPERATE
      # ,'55ab2891-c99e-4647-8a9d-b01fbce3009f' # Char 300 BP
      # ,'248517e9-d7a0-450d-9281-df91d20f68ab' # Char 500 BP
      # ,'eb648ee7-aa4e-41ce-a7fc-04af31349ca9' # Char 700 BP
      # ,'4d7520b9-9ced-43e0-a2e7-974d76d8eb82' # Char 1000 BP
      ,'fd8db3d4-7df1-45fb-8712-5c35bb5acb3f' # Management
      # ,'69cf51ab-090c-4c60-8b58-b71d6455f0a2' # No tricks
      # ,'4d7fd45a-aa2a-48e3-856b-cfb04e203e3b' # Storm rush
      # ,'5e2211a0-e52e-4b7b-b03d-f6ecb3660bb0' # Action 0 SP
      # ,'83c33aa8-5981-4352-8107-cbb7e05547ec' # Action -1 SP
      # ,'b95b2104-d184-43cc-bb04-b3eb096c6fca' # Action -2 SP
      # ,'ac01bbbe-583e-46ae-b26c-3c25eb8f0779' # Action -6 SP
      ,'21db37a5-3483-41d4-9c6a-529071fce7ba' # Lucky card
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
       '65c91e9d-761c-4978-ba3e-6e05026f080e' # Q-Bee
      ,'65c91e9d-761c-4978-ba3e-6e05026f080e' # Q-Bee
      ,'55ab2891-c99e-4647-8a9d-b01fbce3009f' # Char 300 BP
      ,'55ab2891-c99e-4647-8a9d-b01fbce3009f' # Char 300 BP
      ,'248517e9-d7a0-450d-9281-df91d20f68ab' # Char 500 BP
      ,'eb648ee7-aa4e-41ce-a7fc-04af31349ca9' # Char 700 BP
      ,'4d7520b9-9ced-43e0-a2e7-974d76d8eb82' # Char 1000 BP
      ,'5e2211a0-e52e-4b7b-b03d-f6ecb3660bb0' # Action 0 SP
      # ,'83c33aa8-5981-4352-8107-cbb7e05547ec' # Action -1 SP
      # ,'b95b2104-d184-43cc-bb04-b3eb096c6fca' # Action -2 SP
      ,'ac01bbbe-583e-46ae-b26c-3c25eb8f0779' # Action -6 SP
      ,'556b3359-e642-419a-ab5c-67f70de1bb4f' # Reaction 0 SP
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
   debug(">>> debugOpp()") #Debug
   global charsPlayed
   
   tableCards = [
       # 'd14694b4-484c-4b45-962e-8cbb636d8a9a' # Baby Head
      # ,'24e99a13-cb42-4e16-9900-78dde12e1a4c' # Charlie
      # ,'26f3f47c-881f-4d98-a583-ddc6b6b90cd5' # Nemesis
      # ,'ff8a97e3-9a78-4c5f-86fa-23480fa57da5' # Pure Rider Akira
   ]
   for i, id in enumerate(tableCards):
      debug("Creating card {} at slot {}".format(id, i))
      card = table.create(id, 0, 0, quantity=1, persist=True)
      playAuto(card, i, True)
      charsPlayed = 0
      rnd(1, 100)  # Delay the next action until all animation is done
      
   handCards = [
      'eb648ee7-aa4e-41ce-a7fc-04af31349ca9' # Char
      ,'55ab2891-c99e-4647-8a9d-b01fbce3009f' # Char
      # ,'9c405677-1d42-4eb7-bb44-7b21c1d84859' # Char
      # ,'483b9441-d435-43a3-beb7-61e41c9e4045' # Char
      # ,'85d84ab1-dede-4fc7-b80d-00778f73c905' # Action
      ,'ac01bbbe-583e-46ae-b26c-3c25eb8f0779' # Action
      ,'5e2211a0-e52e-4b7b-b03d-f6ecb3660bb0' # Action 0 SP
      # ,'83c33aa8-5981-4352-8107-cbb7e05547ec' # Action -1 SP
      # ,'b95b2104-d184-43cc-bb04-b3eb096c6fca' # Action -2 SP
      ,'556b3359-e642-419a-ab5c-67f70de1bb4f' # Reaction 0 SP
      # ,'46deecf5-7f7b-42b5-b6fa-e3162dce2013' # Reaction -1 SP
      # ,'91e441cc-0f1f-4b01-a2b0-94678d6f0b56' # Reaction -4 SP
   ]
   for id in handCards:
      debug("Adding card {} to hand".format(id))
      card = table.create(id, 0, 0, quantity=1, persist=True)
      card.moveTo(me.hand)
   
   deckCards = [
       '55ab2891-c99e-4647-8a9d-b01fbce3009f' # Char 300 BP
      ,'55ab2891-c99e-4647-8a9d-b01fbce3009f' # Char 300 BP
      ,'248517e9-d7a0-450d-9281-df91d20f68ab' # Char 500 BP
      ,'eb648ee7-aa4e-41ce-a7fc-04af31349ca9' # Char 700 BP
      ,'4d7520b9-9ced-43e0-a2e7-974d76d8eb82' # Char 1000 BP
      ,'5e2211a0-e52e-4b7b-b03d-f6ecb3660bb0' # Action 0 SP
      ,'83c33aa8-5981-4352-8107-cbb7e05547ec' # Action -1 SP
      ,'b95b2104-d184-43cc-bb04-b3eb096c6fca' # Action -2 SP
      ,'ac01bbbe-583e-46ae-b26c-3c25eb8f0779' # Action -6 SP
      ,'556b3359-e642-419a-ab5c-67f70de1bb4f' # Reaction 0 SP
      ,'46deecf5-7f7b-42b5-b6fa-e3162dce2013' # Reaction -1 SP
      ,'91e441cc-0f1f-4b01-a2b0-94678d6f0b56' # Reaction -4 SP
   ]
   for id in deckCards:
      debug("Adding card {} to Deck".format(id))
      card = table.create(id, 0, 0, quantity=1, persist=True)
      card.moveTo(me.deck)
      
   debug("<<< debugOpp()") #Debug
   

def debugBackups():
   backups = getGlobalVar('Backups')
   debug("BACKUPS ({})".format(len(backups)))
   for id in backups:
      debug("   {} backups {}".format(Card(id), Card(backups[id])))
   
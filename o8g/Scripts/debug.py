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

#------------------------------------------------------------------------------
# Debugging
#------------------------------------------------------------------------------

def debug(msg, *args):
   if debugVerbosity > 0:
      res = str(msg)
      if len(args) > 0:
         res = res.format(*args)
      whisper("[#]=> " + res)


def debugSetup():
   settings.update(eval(getSetting("settings", "")))
   settings["PhaseAuto"] = False
   settings["Activate"] = False
   if me.isActive:
      setState(None, "activePlayer", me._id)
      update()


def debugScenario():
   debug(">>> debugScenario()")
   
   if me.name != Author or not debugging:
      return
   
   if turnNumber() == 0: 
      nextTurn(me, True)
   
   me.SP = 50
   debugSetup()
   gotoMain()
   waitForAnimation()
   tableCards = [
       "d14694b4-484c-4b45-962e-8cbb636d8a9a" # 200 BP
      # ,"c7d128ea-a3b9-4b04-b8b2-a61153b5b2e6" # 400 BP
      # ,"24e99a13-cb42-4e16-9900-78dde12e1a4c" # 600 BP
      # ,"e6e46f83-d089-4762-8d8e-2a3252cfc9db" # 800 BP
   ]
   for i, id in enumerate(tableCards):
      debug("Creating card {} at slot {}", id, i)
      card = table.create(id, 0, 0, quantity = 1, persist = True)
      playAuto(card, i)
      ability = Ability(card)
      if ability.type != InstantAbility:
         setMarker(card, "Just Entered", qty = 0)
      setState(me, "charsPlayed", 0)
      waitForAnimation()
      
   handCards = [
       "5972ea54-137c-41a7-a1eb-b9d9cd0ecfe5" # Grandmaster
       # "8bb477f9-5004-4018-8d5e-73c6a23e8912" # Char 300 BP
      # ,"e910f462-bea9-4262-b168-c7c512eb6511" # Char 500 BP
      # ,"0fdadc92-0864-46cc-a3ff-c20e2af8249c" # Char 700 BP
      # ,"af43872e-e47d-4fe0-9b55-aedd8a0d0fc7" # Char 800 BP
      # ,"5e2211a0-e52e-4b7b-b03d-f6ecb3660bb0" # Action 0 SP
      # ,"83c33aa8-5981-4352-8107-cbb7e05547ec" # Action -1 SP
      # ,"80692723-3895-435f-bf8f-e94507704af5" # Action -3 SP
       # "26fa7e0e-eb86-40d5-b5ab-39723fd67e43" # Action -5 SP
      # ,"68eaee28-a00a-480f-b8e5-e14d2a8f102c" # Reaction 0 SP
      # ,"46deecf5-7f7b-42b5-b6fa-e3162dce2013" # Reaction -1 SP
      # ,"91e441cc-0f1f-4b01-a2b0-94678d6f0b56" # Reaction -4 SP
   ]
   for id in handCards:
      debug("Adding card {} to hand", id)
      me.hand.create(id, 1)
   
   deckCards = [
       # "55ab2891-c99e-4647-8a9d-b01fbce3009f" # Char 300 BP
      # ,"248517e9-d7a0-450d-9281-df91d20f68ab" # Char 500 BP
      # ,"eb648ee7-aa4e-41ce-a7fc-04af31349ca9" # Char 700 BP
      # ,"4d7520b9-9ced-43e0-a2e7-974d76d8eb82" # Char 1000 BP
      # ,"5e2211a0-e52e-4b7b-b03d-f6ecb3660bb0" # Action 0 SP
      # ,"83c33aa8-5981-4352-8107-cbb7e05547ec" # Action -1 SP
      # ,"80692723-3895-435f-bf8f-e94507704af5" # Action -3 SP
      # ,"ac01bbbe-583e-46ae-b26c-3c25eb8f0779" # Action -6 SP
      # ,"68eaee28-a00a-480f-b8e5-e14d2a8f102c" # Reaction 0 SP
      # ,"46deecf5-7f7b-42b5-b6fa-e3162dce2013" # Reaction -1 SP
      # ,"91e441cc-0f1f-4b01-a2b0-94678d6f0b56" # Reaction -4 SP
   ]
   for id in list(reversed(deckCards)):
      debug("Adding card {} to Deck", id)
      me.deck.create(id, 1)
   
   discardCards = [
       "8bb477f9-5004-4018-8d5e-73c6a23e8912" # Char 300 BP
      # ,"e910f462-bea9-4262-b168-c7c512eb6511" # Char 500 BP
      # ,"0fdadc92-0864-46cc-a3ff-c20e2af8249c" # Char 700 BP
      # ,"af43872e-e47d-4fe0-9b55-aedd8a0d0fc7" # Char 800 BP
      # ,"5e2211a0-e52e-4b7b-b03d-f6ecb3660bb0" # Action 0 SP
      # ,"83c33aa8-5981-4352-8107-cbb7e05547ec" # Action -1 SP
      # ,"80692723-3895-435f-bf8f-e94507704af5" # Action -3 SP
      # ,"ac01bbbe-583e-46ae-b26c-3c25eb8f0779" # Action -6 SP
      ,"556b3359-e642-419a-ab5c-67f70de1bb4f" # Reaction 0 SP
      ,"46deecf5-7f7b-42b5-b6fa-e3162dce2013" # Reaction -1 SP
      # ,"91e441cc-0f1f-4b01-a2b0-94678d6f0b56" # Reaction -4 SP
   ]
   for id in list(reversed(discardCards)):
      debug("Adding card {} to Discard pile", id)
      me.piles["Discard pile"].create(id, 1)
      
   if len(players) > 1:
      waitForAnimation()
      update()
      remoteCall(players[1], "debugOpp", [])
   else:
      debugSetupDone()
      
   debug("<<< debugScenario()")
   
   
def debugOpp():
   debugSetup()
   
   me.SP = 50
   
   tableCards = [
       "d14694b4-484c-4b45-962e-8cbb636d8a9a" # 200 BP
      # ,"c7d128ea-a3b9-4b04-b8b2-a61153b5b2e6" # 400 BP
      # ,"24e99a13-cb42-4e16-9900-78dde12e1a4c" # 600 BP
      # ,"e6e46f83-d089-4762-8d8e-2a3252cfc9db" # 800 BP
   ]
   for i, id in enumerate(tableCards):
      card = table.create(id, 0, 0, quantity = 1, persist = True)
      playAuto(card, i, True)
      setState(me, "charsPlayed", 0)
      waitForAnimation()
      
   handCards = [
       "5972ea54-137c-41a7-a1eb-b9d9cd0ecfe5" # Grandmaster
       # "8bb477f9-5004-4018-8d5e-73c6a23e8912" # Char 300 BP
      # ,"e910f462-bea9-4262-b168-c7c512eb6511" # Char 500 BP
      # ,"0fdadc92-0864-46cc-a3ff-c20e2af8249c" # Char 700 BP
      # ,"af43872e-e47d-4fe0-9b55-aedd8a0d0fc7" # Char 800 BP
      # ,"5e2211a0-e52e-4b7b-b03d-f6ecb3660bb0" # Action 0 SP
      # ,"83c33aa8-5981-4352-8107-cbb7e05547ec" # Action -1 SP
      # ,"80692723-3895-435f-bf8f-e94507704af5" # Action -3 SP
      # ,"26fa7e0e-eb86-40d5-b5ab-39723fd67e43" # Action -5 SP
      # ,"68eaee28-a00a-480f-b8e5-e14d2a8f102c" # Reaction 0 SP
      # ,"46deecf5-7f7b-42b5-b6fa-e3162dce2013" # Reaction -1 SP
      # ,"91e441cc-0f1f-4b01-a2b0-94678d6f0b56" # Reaction -4 SP
   ]
   for id in handCards:
      me.hand.create(id, 1)
   
   deckCards = [
       # "55ab2891-c99e-4647-8a9d-b01fbce3009f" # Char 300 BP
      # ,"55ab2891-c99e-4647-8a9d-b01fbce3009f" # Char 300 BP
      # ,"248517e9-d7a0-450d-9281-df91d20f68ab" # Char 500 BP
      # ,"eb648ee7-aa4e-41ce-a7fc-04af31349ca9" # Char 700 BP
      # ,"5e2211a0-e52e-4b7b-b03d-f6ecb3660bb0" # Action 0 SP
      # ,"83c33aa8-5981-4352-8107-cbb7e05547ec" # Action -1 SP
      # ,"80692723-3895-435f-bf8f-e94507704af5" # Action -3 SP
      # ,"ac01bbbe-583e-46ae-b26c-3c25eb8f0779" # Action -6 SP
      # ,"68eaee28-a00a-480f-b8e5-e14d2a8f102c" # Reaction 0 SP
      # ,"46deecf5-7f7b-42b5-b6fa-e3162dce2013" # Reaction -1 SP
      # ,"91e441cc-0f1f-4b01-a2b0-94678d6f0b56" # Reaction -4 SP
   ]
   for id in list(reversed(deckCards)):
      me.deck.create(id, 1)
   
   discardCards = [
       "55ab2891-c99e-4647-8a9d-b01fbce3009f" # Char 300 BP
      # ,"248517e9-d7a0-450d-9281-df91d20f68ab" # Char 500 BP
      # ,"eb648ee7-aa4e-41ce-a7fc-04af31349ca9" # Char 700 BP
      # ,"4d7520b9-9ced-43e0-a2e7-974d76d8eb82" # Char 1000 BP
      ,"5e2211a0-e52e-4b7b-b03d-f6ecb3660bb0" # Action 0 SP
      # ,"83c33aa8-5981-4352-8107-cbb7e05547ec" # Action -1 SP
      # ,"80692723-3895-435f-bf8f-e94507704af5" # Action -3 SP
      # ,"ac01bbbe-583e-46ae-b26c-3c25eb8f0779" # Action -6 SP
      ,"556b3359-e642-419a-ab5c-67f70de1bb4f" # Reaction 0 SP
      ,"46deecf5-7f7b-42b5-b6fa-e3162dce2013" # Reaction -1 SP
      ,"91e441cc-0f1f-4b01-a2b0-94678d6f0b56" # Reaction -4 SP
   ]
   for id in list(reversed(discardCards)):
      me.piles["Discard pile"].create(id, 1)
      
   remoteCall(players[1], "debugSetupDone", [])
   
   
def debugSetupDone():
   global debugVerbosity
   debugVerbosity = DebugLevel["Debug"]
      

def debugBackups():
   backups = getGlobalVar("Backups")
   debug("BACKUPS ({})", len(backups))
   for id in backups:
      debug("   {} backups {}", Card(id), Card(backups[id]))


def debugGameState():
   print(u"\u200B\n== GameEvents ==")
   ge = getGlobalVar("GameEvents")
   for e in ge:
      restr = " " + "".join(e["restr"]) if e["restr"] else ""
      print("{}{}: {} ({})".format(e["event"], restr, Card(e["id"]).Name, Player(e["controller"])))
        
   print("\n== Modifiers ==")
   mods = getGlobalVar("Modifiers")
   for t in mods:
      for m in mods[t]:
         print("{}: {} {}".format(t, Card(m[0]).Name, m[1:]))
         
   print("\n== Rules ==")
   rules = getGlobalVar("Rules")
   for r in rules:
      for key, v in rules[r].iteritems():
         print("{}: {} ({})".format(r, Card(key).Name, v))
         
   print("\n== My Rules ==")
   rules = getGlobalVar("Rules", me)
   for r in rules:
      for key, v in rules[r].iteritems():
         print("{}: {} ({})".format(r, Card(key).Name, v))
   
   if len(players) > 1:
      print("\n== Enemy Rules ==")
      rules = getGlobalVar("Rules", players[1])
      for r in rules:
         for key, v in rules[r].iteritems():
            print("{}: {} ({})".format(r, Card(key).Name, v))
        
   print("\n== Transformed ==")
   for id in transformed:
      print("{} ({})".format(Card(id).Name, transformed[id]))
        
   print("\n== Backups ==")
   backups = getGlobalVar("Backups")
   for key, v in backups.iteritems():
      print("{} -> {}".format(Card(key).Name, Card(v).Name))
        
   print("\n== Ring ==")
   print("Mine: {}".format(", ".join(map(lambda id: Card(id).Name if id else "-", getGlobalVar("Ring", me)))))
   if len(players) > 1:
      print("Enemy: {}".format(", ".join(map(lambda id: Card(id).Name if id else "-", getGlobalVar("Ring", players[1])))))
      
   print("\n== CharsAbilities ==")
   abls = getGlobalVar("CharsAbilities")
   for key, v in abls.iteritems():
      print("{}: {}".format(Card(key).Name, v))
      
   print("\n== TempVars ==")
   print(getGlobalVar("TempVars"))
   
   print("\n== GameState ==")
   gs = getGlobalVar("GameState")
   print("priority: {}".format(gs["priority"]))
   print("activePlayer: {}".format(gs["activeplayer"]))
   for p, state in gs.iteritems():
      if isinstance(p, int):
         print(Player(p).name)
         for k, v in state.iteritems():
            print("   {}: {}".format(k, v))
   
   if getActivePlayer():
      print("\n== Attacking Chars ({}) ==".format(getActivePlayer().name))
      ua = getGlobalVar("UnitedAttack")
      for c in getAttackingCards(getActivePlayer()):
         if c._id not in ua:
            print("{}".format(c.Name))
      ua = [Card(id).Name for id in ua]
      print(" + ".join(ua))

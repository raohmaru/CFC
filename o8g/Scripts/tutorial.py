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
# Tutorial
#---------------------------------------------------------------------------

tutorial = None

class Tutorial(object):
   def __init__(self):
      self.msgOnDone = u"When done, please click on the \u25B6 button or press the Tab key."
      self.validatePhase = None
      self.step = 0
      settings["PlayAuto"] = True
      settings["PhaseAuto"] = True
      settings["Activate"] = True
      self.start()
      
      
   def addCardToGroup(self, id, group = table):
      card = table.create(id, 0, 0, quantity = 1, persist = True)
      if group != table:
         card.moveTo(group)
      return card


   def msg(self, str, button = "Next"):
      askChoice(str, [], [], [button])
      
      
   def nextTurn(self):
      nextTurn(me, True)
      waitForAnimation()
      
      
   def setNextStep(self, func, phase):
      self.nextFunc = func
      self.validatePhase = phase
      
      
   def goNextStep(self):
      self.step += 1
      self.nextFunc()
      
   
   def getCard(self, name, group = None):
      if group is None:
         group = getRing(me)
      for c in group:
         if c.Name == name:
            return c
            
   
   def attack(self, card):
      """
      Simulates an attack with a card from the fake player.
      """
      setMarker(card, "Attack")
      card.highlight = AttackColor
      x, y = CardsCoords["Attack1"]
      y = fixCardY(y, inverted = True)
      card.moveToTable(x, y)
      setGlobalVar("Ring", [None, None, card._id, None], self.fakePlayer)
   
   #-------------------   
   # Steps
   #-------------------
   
   def start(self):
      self.msg("""
Welcome to the tutorial of Card Fighters' Clash!

Card Fighters' Clash is a card game for two players, where you try to defeat your enemy (this is, your opponent) by playing Characters cards from Capcom and SNK Playmore video games, Action cards and Reaction cards.
""")

      self.msg("""
You start the game with 3000 HP (Hit Points, this is your life). When it reaches 0, or you cannot draw cards from your Deck in your Draw phase, you lose the game.

The game board is called "Arena", and it is split into two parts: one for each player, called "Ring", with four slots each one (numbered from 1 to 4).
""")

      self.nextTurn()
      self.addCardToGroup("d14694b4-484c-4b45-962e-8cbb636d8a9a", me.hand)  # Baby Head

      self.msg(u"""
But enough talking and let's start the training!
I have added some cards to your hand.

Please play a Character card from your hand into your Ring.

{}

\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B
To play a card form you hand you can do any of the following:
- Drag it into your Ring.
- Double-click on it.
- Right click on the mouse while hovering the card to show the menu and select "Play card".
""".format(self.msgOnDone), "OK")

      self.setNextStep(self.part2, MainPhase)
      
      
   def part2(self):
      if getRingSize() == 0:
         warning("Please play a character card from your hand.")
         return False
   
      self.msg("""
Well done!

You have played a Character card with which you can attack your enemy. Note that you cannot attack yet with this character until your next turn.

Alos note that your Ring has four slots, which means that you cannot have more than four characters at once. Therefore you need to think carefully which character to play.
""")

      self.msg("""
Playing a Character card adds or subtracts their SP value to your SP. You can use your SP to play strong characters with negative SP value or to play Action or Reaction cards.

Additionally, you can only play one character card per turn.
""")

      self.msg("""
The strength of the characters is represented by its BP value. When it attacks, it deals damage equals to its BP. When it is dealt damage, its BP is reduced permanently by that number of damage points.
""")

      self.msg(u"""
Characters also have Abilities, which are effects that are applied to the game. An Ability has a type ({0}, {1} and {2}), a name and a rule text.

{0} ABILITY
It is activated when the character enters the Ring.

{1} ABILITY
It can be activated only in your Main phase. When it is activated the character is frozen.
Frozen characters and characters that just entered the Ring cannot activate {1} abilities in that turn.

{2} ABILITY
It is always active as long as that character is on the Ring.
Whenever a character with a {2} ability takes part in a United Attack, the ability is nullified until the end of the turn.
""".format(InstantUniChar, TriggerUniChar, AutoUniChar))

      self.addCardToGroup("f286cc08-ae18-4a40-bd66-17aedcfd9267", me.hand)  # Krauser
      
      self.msg(u"""
You have a new character card in your hand. Now please play it.

(Note that it has a {} ability, and it will be activated automatically.)

{}
""".format(InstantUniChar, self.msgOnDone), "OK")

      self.setNextStep(self.part3, MainPhase)
      self.nextTurn()
      
      
   def part3(self):
      if not self.getCard("Krauser"):
         warning("Please play the card Krauser from your hand.")
         return False
   
      self.msg("""
Poor Baby Head! But don't worry too much because he will come later again.

When one of your characters is KOed, it goes from your Ring to your Discard pile.

Note also how your SP lowered by {} after playing Krauser because of the negative SP cost of the card.
""".format(abs(self.getCard("Krauser").SP)))
   
      self.msg("""
Now let's advance to the next turn and play another character with a {} ability.
""".format(AutoUniChar))

      self.addCardToGroup("4bd333d6-f063-424e-8cf9-3512f96f23b4", me.hand)  # Batsu
   
      self.msg("""
I have added the card Batsu to your hand. Batsu's {} BOILING BLOOD ability will allow you to activate characters with {} abilities the same turn you play them.

Please play Batsu from your hand.

{}
""".format(AutoUniChar, TriggerUniChar, self.msgOnDone), "OK")

      self.setNextStep(self.part4, MainPhase)
      self.nextTurn()
      
      
   def part4(self):
      if not self.getCard("Batsu"):
         warning("Please play the card Batsu from your hand.")
         return False
   
      self.msg(u"""
Batsu's {} ability will be active until he leaves the Ring, so now it is time to play a character with a {} ability, like Gato.
I will add it to your hand.
""".format(AutoUniChar, TriggerUniChar))

      self.addCardToGroup("f3557575-c61e-42fd-9442-9413cea64bdf", me.hand)  # Gato
      
      self.msg(u"""
Now play Gato from your hand, and then activate its ability.

{}

\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B
To activate a {} ability you can do any of the following:
- Double-click on the card.
- Right click on the mouse while hovering the card and then click "Use ability" in the contextual menu.
""".format(self.msgOnDone, TriggerUniChar), "OK")

      self.setNextStep(self.part5, MainPhase)
      self.nextTurn()
      
      
   def part5(self):
      if not self.getCard("Gato"):
         warning("Please play the card Gato from your hand.")
         return False
      elif self.getCard("Gato").highlight != ActivatedColor:
         warning("Please activate Gato's ability.")
         return False
      
      self.msg("""
Do you remember Batsu's ability? You were able to activate Gato's {} ability because of Batsu's {} BOILING BLOOD ability.

You also have learned that abilities can be removed from a character! Abilities can also be copied between characters or given to other character.
""".format(TriggerUniChar, AutoUniChar))
      
      self.msg("""
And now it is time to learn how to attack!

After the Main phase it comes the Attack phase, where you can attack your enemy with the characters in you Ring that hasn't been played this turn and are not frozen.
""")
      
      self.msg(u"""
Please attack with a character in your Ring.

{}

\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B
To attack with a character you can do any of the following:
- Move it to the front.
- Double-click on the Character card.
- Press Ctrl+A while hovering the card with the mouse.
- Right click on the mouse while hovering the card and then click "Attack" in the contextual menu.
""".format(self.msgOnDone, TriggerUniChar), "OK")
         
      self.setNextStep(self.part6, AttackPhase)
      gotoAttack()
      
      
   def part6(self):
      if len(getAttackingCards()) == 0:
         warning("Please attack with at least one character in your Ring.")
         return False
         
      self.msg("""
Nice!

Attacking characters deal damage equals to its BP to the enemy, reducing their HP. But if it is blocked by another character, they will deal damage to each other instead.

After the attack is done, attacking characters are frozen until your next Activate phase.
""")
     
      self.msg("""
You can use your SP to do a more powerful attack and hit the enemy even if you character is blocked!

This attack is called "United Attack", where two or three characters attack together as a single entity that does one single attack.

If two characters join an United Attack, it cost 5 SP. If three characters do join, then it cost 10 SP.
""")
     
      self.msg("""
The most critical feature of United Attacks is that the sum of the BP of the characters involved in the United Attack is considered when dealing damage.

Furthermore, if the United Attack is blocked, and if the total BP of the attack is greater than the BP of the blocking character, the remaining BP is dealt as damage to the enemy (called "Piercing Damage").

It's a very effective way of hitting the enemy even if he blocks with a character!
""")

      for c in getAttackingCards():
         cancelAttack(c, True)
      
      self.msg(u"""
Attack the enemy with a United Attack.

{}

\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B
To do an United Attack you can do any of the following:
- Drag and drop a character on top of an attacking character.
- Press Ctrl+Alt+A while hovering the card with the mouse.
- Right click on the mouse while hovering the card and then click "United Attack" in the contextual menu.
""".format(self.msgOnDone, TriggerUniChar), "OK")

      self.setNextStep(self.part7, AttackPhase)
      
      
   def part7(self):
      if len(getGlobalVar("UnitedAttack")) == 0:
         warning("Please do an United Attack.")
         return False
      me.SP += UAttackCost
      
      self.msg("""
Did you noticed how your SP lowered from {} to {}? That's because of the cost of the Double United Attack.

Also take into account that {} abilities are nullified (canceled) until the end of your turn if the character joins an United Attack.
""".format(me.SP - UAttackCost, me.SP, AutoUniChar))

      me.SP -= UAttackCost
     
      self.msg("""
Now that you know how to attack, it is about time to learn how to Counter-attack.

You can counter-attack (this is, to block) an attacking character with a non-frozen character in your Ring.

A character can only counter-attack one attack, and an attack can only be countered by one single character (even if it is a United Attack).
""")
         
      self.setNextStep(self.part8, BlockPhase)
      gotoCounterattack()
      addButton("NextButton")
      
      for card in getRing(me):
         freeze(card, unfreeze = card.Name != "Gato", silent = True)
         removeMarker(card, "Attack")
         removeMarker(card, "United Attack")
         clear(card)
         alignCard(card)
         
      # Trick the game that we are playing against an opponent
      self.fakePlayer = FakePlayer()
      global players
      players.append(self.fakePlayer)
      card = self.addCardToGroup("d6441760-574a-447d-bf1e-f900cb39535e")  # Lee Reeka
      setMarker(card, "BP", card.BP)
      self.attack(card)
      
      self.msg(u"""
Block the attacking character with one character in your Ring.

{}

\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B
To do a counter-attack you can do any of the following:
- Drag and drop a character in front of the attacking character.
- Double-click on a Character card.
- Press Ctrl+B while hovering the card with the mouse.
- Right click on the mouse while hovering the card and then click "Counter-attack" in the contextual menu.
""".format(self.msgOnDone), "OK")
      
      
   def part8(self):
      if not getGlobalVar("Blockers"):
         warning("Please counter-attack the attacking character with a character in your Ring.")
         return False
         
      setMarker(self.getCard("Lee Rekka", table), "BP", 0)
      
      self.msg("""
Great! Now you know how to attack and counter-attack.

Let's see the other type of cards of the game.
""")
         
      self.getCard("Lee Rekka", table).delete()
            
      self.addCardToGroup("5f19902c-60fb-44b8-9e64-eab4b31c9d3d", me.hand)  # Revive
      
      self.msg("""
Action cards add instant effects to the battle and can help you to win the game!

To play an Action card you must pay its SP cost from your SP pool. After you play it, its effects are applied immediately and the card is put into your Discard pile.

You can play any number of Action cards as long as you have enough SP, but only in your Main phase.
""")
      
      self.msg(u"""
Please play the card Revive from your hand.

{}

\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B
Hint: You can target Baby Head from the Discard pile with Shift + Left Click as the target of the Action card. Otherwise, the Card Selection dialog will pop-up with the available targets.
""".format(self.msgOnDone), "OK")

      self.setNextStep(self.part9, MainPhase)
      self.nextTurn()
      
      
   def part9(self):
      if self.getCard("Revive", me.hand):
         warning("Please play the card Revive from your hand.")
         return False
      
      self.msg("""
Well done! Baby Head is back into your hand thanks to a powerful Action card.

Don't worry if Revive does not goes immediately to your Discard pile, it will be removed from the table automatically in the next phase. In any case, you can manually put it into your Discard pile with the mouse or by pressing Del key while hovering the mouse over the card.
""")

      self.addCardToGroup("f4df6ee6-2fcd-4ba1-b86f-59d5028eb96b", me.hand)  # Vacation
      for card in table:
         if isAction(card):
            discard(card)
      
      self.msg("""
The third type of card available in the game are Reaction cards.

Reaction cards are like Action cards but that can be only played during enemy's Counter-attack phase, and only if that enemy is attacking you.

You can play Reaction cards before or after blocking with your characters, or even if you don't have any character in your Ring.
""")
      
      self.msg(u"""
Play the card Vacation from your hand in response of the enemy attack.

{}

\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B\u2E3B
Hint: Please remember that you can target a character in the Ring with Shift + Left Click as the target of the reaction card.
""".format(self.msgOnDone), "OK")
         
      self.setNextStep(self.part10, BlockPhase)
      gotoCounterattack()
      addButton("NextButton")
      me.SP += 3
      
      card = self.addCardToGroup("fd1a3f1c-7df1-443e-97b1-f093d66e74c9")  # Zero Akuma
      setMarker(card, "BP", card.BP)
      self.attack(card)
      
      
   def part10(self):
      if self.getCard("Vacation", me.hand):
         warning("Please play the card Vacation from your hand.")
         return False
         
      self.msg("""
Congratulations! You have completed the training!

You will find more information about the game rules at the menu option "Game > Documents" and in the website {}.

Also you can get information in-game about any card by right-clicking on that card and selecting the option "Card info".
""".format(Website), "OK")
         
      self.msg("""
Now you are ready to face any opponent in the online arena! Good luck!
""", "Close")

      del self.fakePlayer
      players.pop()
      global tutorial
      tutorial = None
      resetGame()


#---------------------------------------------------------------------------
# Functions
#---------------------------------------------------------------------------

def startTutorial(group = table, x = 0, y = 0):
   debug(">>> startTutorial()")
   if len(players) > 1:
      warning("Please start a solo game in order to play the tutorial.")
      return
   if turnNumber() > 0 or len([1 for c in table if isCharacter(c)]) > 0 or len(me.hand) > 0 or len(me.deck) > 0:
      warning("Please reset the game before playing the tutorial.")
      return
   global tutorial
   tutorial = Tutorial()

# OCTGN Gameplay

## Starting a New Game
The game expects you to be playing on a two sided table. When you host a game of Card Fighters' Clash, please ensure that in the Pre-Game Lobby, the "Two Sided Table" option is enabled.

The game can be played with 2 players.

Once the game is started you will need to load your deck. Unless you have turned off Play automation, when you load a deck the game will automate player setup. If you have turned automation off you can activate this function manually using the "Setup game" option from the table menu or by using the <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>S</span> shortcut. This will
- Check your deck
- Shuffle your deck
- Draw 5 cards

## Playing the Game
The best way to learn how to play CFC is by playing [SNK vs. Capcom Card Fighters' Clash 2 Expand Edition](http://neogeo.freeplaytech.com/svc-2/). If you don't have a Neo Geo Pocket Color, or you aren't one of the lucky owners of a Card Fighters' Clash 2 cartridge, you can try [CFC2 English patch](http://cfc2english.blogspot.com.es/).

CFC is a turn-based game. To move to the next phase you can press <span class=kb>Tab</span> key or functions keys <span class=kb>F1</span> to <span class=kb>F7</span>. Once you're in the Cleanup phase, pass the turn to your opponent by clicking in the green triangle after its name.

To play a card from your hand you can double click on it, then the game will take care of the rest (if Play automation is on). Or you can drag it manually onto the table.

To activate an ability or effect of a card on the table, double click on it. There is no automation yet for the card's effects, so you need to apply them manually.

You can attack in the Attack phase by pressing <span class=kb>Ctrl</span>+<span class=kb>A</span> over a character card, or <span class=kb>Ctrl</span>+<span class=kb>Alt</span>+<span class=kb>A</span> to join an attacker and do a United Attack.

Defending player can counter an attacking character in the Counterattack phase by targeting that character, and pressing <span class=kb>Ctrl</span>+<span class=kb>B</span> while hovering one of his characters.

If automations are on, it's important to go through all phases, due to some automated tasks are performed on every phase to easy the gameplay.

## The Actions & Keyboard Shortcuts
To play and go through OCTGN, you can use the mouse to interact with the game objects (table, cards, hand, deck), and the contextual menu (right click) and/or the keyboard to activate actions such as drawing cards, moving between phases or flip a coin. When an action is activated some automations take place to assist you and play faster.

In OCTGN there are two kinds of actions: *group actions* and *card actions*. To activate a group action, you need to move the cursor to an empty spot of the group and then right click on the mouse to show a menu with the available options, or press action's keyboard shortcut.

To activate a card action, move the cursor to a card and then right click to show the menu or press the keyboard shortcut.

### Table ![Table](imgs/table.png)
#### Group Actions
| Keys             | Description                                      |
|:-----------------|:-------------------------------------------------|
| <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>S</span> | Setup <span class=sm>(Should be activated on every new game)</span> |
| <span class=kb>Tab</span> | Next phase <span class=sm>(Or double click)</span> |
| <span class=kb>F1</span> | Go to Activate phase      |
| <span class=kb>F2</span> | Go to Draw phase          |
| <span class=kb>F3</span> | Go to Main phase          |
| <span class=kb>F4</span> | Go to Attack phase        |
| <span class=kb>F5</span> | Go to Counterattack phase |
| <span class=kb>F6</span> | Go to End phase           |
| <span class=kb>F7</span> | Go to Cleanup phase       |
| <span class=kb>Ctrl</span>+<span class=kb>0~9</span> | Gain X or 1~9 SP |
| <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>0~9</span> | Lose X or 1~9 SP |
| <span class=kb>Ctrl</span>+<span class=kb>I</span> | Realign all your cards in the ring |
| <span class=kb>Esc</span> | Clear all your cards <span class=sm>(removes targets and highlight colors)</span> |

#### Card Actions
| Keys             | Description                                      |
|:-----------------|:-------------------------------------------------|
| <span class=kb>Double click</span> | Use card ability / Resolve effect |
| <span class=kb>Ctrl</span>+<span class=kb>F</span> | Freeze / Unfreeze character |
| <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>F</span> | Don't unfreeze character on Activate phase |
| <span class=kb>Ctrl</span>+<span class=kb>A</span> | Attack / Remove from attack |
| <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>A</span> | Attack without freezing |
| ![Target](imgs/target.png) <span class=kb>Ctrl</span>+<span class=kb>A</span><br>![Target](imgs/target.png) <span class=kb>Ctrl</span>+<span class=kb>Alt</span>+<span class=kb>A</span> | United Attack |
| ![Target](imgs/target.png) <span class=kb>Ctrl</span>+<span class=kb>B</span> | Counter-attack |
| <span class=kb>Del</span> | Destroy card |
| <span class=kb>Shift</span>+<span class=kb>Del</span> | Remove card from the game |
| <span class=kb>Ctrl</span>+<span class=kb>H</span> | Return card to hand |
| <span class=kb>Ctrl</span>+<span class=kb>D</span> | Put on top of the deck |
| <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>D</span> | Put on bottom of the deck |
| <span class=kb>Ctrl</span>+<span class=kb>X</span> | Lose/Restore abilities |
| ![Target](imgs/target.png) <span class=kb>Ctrl</span>+<span class=kb>C</span> | Copy ability |
| ![Target](imgs/target.png) <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>C</span> | Swap abilities |
| ![Target](imgs/target.png) <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>T</span><br><span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>T</span> | Transform |
| <span class=kb>Ctrl</span>+<span class=kb>I</span> | Realign card in the ring |
| <span class=kb>Esc</span> | Clear card <span class=sm>(removes targets and highlight colors)</span> |
| <span class=kb>Ctrl</span>+<span class=kb>Alt</span>+<span class=kb>B</span> | Show compatible backups types |
| <span class=kb>Ctrl</span>+<span class=kb>0~9</span> | Raise BP of character by X or 1~9 |
| <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>0~9</span> | Lower BP of character by X or 1~9 |
| <span class=kb>Ctrl</span>+<span class=kb>Alt</span>+<span class=kb>0</span> | Change BP |

### Hand ![Hand](../Groups/hand.png)
#### Group Actions
| Keys             | Description                                      |
|:-----------------|:-------------------------------------------------|
| <span class=kb>Ctrl</span>+<span class=kb>Del</span> | Random discard |
| <span class=kb>Ctrl</span>+<span class=kb>D</span> | Put hand on top of the deck |
| <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>D</span> | Put hand on bottom of the deck |
| <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>Del</span> | Discard hand |

#### Card Actions
| Keys             | Description                                      |
|:-----------------|:-------------------------------------------------|
| <span class=kb>Double click</span> | Play card |
| ![Target](imgs/target.png) <span class=kb>Ctrl</span>+<span class=kb>B</span><br>![Target](imgs/target.png) Double click | Play as backup |
| <span class=kb>Ctrl</span>+<span class=kb>Alt</span>+<span class=kb>B</span> | Show compatible backups types |
| <span class=kb>Del</span> | Discard card |
| <span class=kb>Ctrl</span>+<span class=kb>D</span> | Put card on top of the deck |
| <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>D</span> | Put card on bottom of the deck |
| <span class=kb>Ctrl</span>+<span class=kb>F</span> | Put card into Arena face down |
| ![Target](imgs/target.png) <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>T</span><br><span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>T</span> | Transform |

### Deck ![Deck](../Groups/deck.png)
#### Group Actions
| Keys             | Description                                      |
|:-----------------|:-------------------------------------------------|
| <span class=kb>Double click</span> | Draw card |
| <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>D</span> | Draw X cards |
| <span class=kb>Ctrl</span>+<span class=kb>Alt</span>+<span class=kb>R</span> | Draw a random card |
| <span class=kb>Ctrl</span>+<span class=kb>Alt</span>+<span class=kb>C</span> | Draw a random Character card |
| <span class=kb>Ctrl</span>+<span class=kb>Alt</span>+<span class=kb>A</span> | Draw a random Action card |
| <span class=kb>Ctrl</span>+<span class=kb>Alt</span>+<span class=kb>E</span> | Draw a random Reaction card |
| <span class=kb>Ctrl</span>+<span class=kb>S</span> | Shuffle |
| <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>T</span> | Trash X cards |
| <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>S</span> | Rearrange X cards |
| <span class=kb>Ctrl</span>+<span class=kb>R</span> | Reveal/Hide top card |
| <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>Del</span> | Discard hand |

#### Card Actions
| Keys             | Description                                      |
|:-----------------|:-------------------------------------------------|
| <span class=kb>Ctrl</span>+<span class=kb>H</span> | Put card into Hand |
| <span class=kb>Del</span> | Discard card |
| <span class=kb>Ctrl</span>+<span class=kb>D</span> | Put card on top of the deck |
| <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>D</span> | Put card on bottom of the deck |

### Discard Pile ![Discard Pile](../Groups/discards.png)
#### Group Actions
| Keys             | Description                                      |
|:-----------------|:-------------------------------------------------|
| <span class=kb>Ctrl</span>+<span class=kb>S</span> | Shuffle |
| <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>S</span> | Shuffle all cards into deck |
| <span class=kb>Ctrl</span>+<span class=kb>Alt</span>+<span class=kb>S</span> | Swap Discard pile with deck |
| <span class=kb>Ctrl</span>+<span class=kb>Alt</span>+<span class=kb>R</span> | Target a random card |
| <span class=kb>Ctrl</span>+<span class=kb>H</span> | Put all cards into Hand |
| <span class=kb>Ctrl</span>+<span class=kb>D</span> | Put all cards on top of the deck |
| <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>D</span> | Put all cards on bottom of the deck |

#### Card Actions
| Keys             | Description                                      |
|:-----------------|:-------------------------------------------------|
| <span class=kb>Ctrl</span>+<span class=kb>H</span> | Put card into Hand |
| <span class=kb>Ctrl</span>+<span class=kb>D</span> | Put card on top of the deck |
| <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>D</span> | Put card on bottom of the deck |
| <span class=kb>Shift</span>+<span class=kb>Del</span> | Remove card from the game |

### Removed Pile ![Removed Pile](../Groups/removed.png)
#### Group Actions
| Keys             | Description                                      |
|:-----------------|:-------------------------------------------------|
| <span class=kb>Ctrl</span>+<span class=kb>S</span> | Shuffle |
| <span class=kb>Ctrl</span>+<span class=kb>H</span> | Put all cards into Hand |
| <span class=kb>Ctrl</span>+<span class=kb>D</span> | Put all cards on top of the deck |
| <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>D</span> | Put all cards on bottom of the deck |
| <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>Del</span> | Put all cards into Discard pile |

#### Card Actions
| Keys             | Description                                      |
|:-----------------|:-------------------------------------------------|
| <span class=kb>Ctrl</span>+<span class=kb>H</span> | Put card into Hand |
| <span class=kb>Del</span> | Put card into Discard pile |
| <span class=kb>Ctrl</span>+<span class=kb>D</span> | Put card on top of the deck |
| <span class=kb>Ctrl</span>+<span class=kb>Shift</span>+<span class=kb>D</span> | Put card on bottom of the deck |

## OCTGN Functions
__Zoom the Table__
Use the scroll wheel on the table.

__Move/Pan the Table__
Hold the spacebar and click & drag on the table.

__Increment/Decrement counters on a card__
Use the <span class=kb>+</span>/<span class=kb>-</span> keys on your keyboard's NUM pad while hovering over the counter.

__Move counters from one card to another__
Click & drag the counter to the other card.

__Target/untarget a card__
Hold <span class=kb>Shift</span> and click on the card.

__Draw an Arrow between two cards__
Hold <span class=kb>Shift</span> and click & drag from one card to the other card.

__Select multiple cards__
Either click & drag a selection box over the region of cards, or hold <span class=kb>Ctrl</span> and click a card.

__Play card face-down from your hand__
Click & drag a card in your hand, then hold <span class=kb>Shift</span> as you drop the card onto the table.

__Peek a card__
Press <span class=kb>Ctrl</span>+<span class=kb>P</span> while hovering a face-down card.

__Bring card to front or back__
Press <span class=kb>Page Up</span>/<span class=kb>Page Down</span> over a card to bring it to front or to back.

https://github.com/kellyelton/OCTGN/wiki/Octgn-Keyboard-Shortcuts
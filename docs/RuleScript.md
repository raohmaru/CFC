# RuleScript
RuleScript is an scripting language designed for coding cards for OCTGN games, written in Python and inspired by [Wagic CardCode](https://github.com/WagicProject/wagic/wiki/CardCode). It automates the execution of the card mechanics to ease game play.

The syntax is similar to [INI files](https://en.wikipedia.org/wiki/INI_file), comprising key–value pairs to define the actions a card can do.

## Features
RuleScript is case insensitive, including identifiers, commands (functions) and strings. The only exception to this are [Expressions](#Expressions), which are case-sensitive.

## Primitive Data Types
### String
A string is a series of characters that represents a text.  
String literals can be specified using single or double quotes, or no quotes at all (depending on the context).

### Integer
An integer (or *int*) is a decimal (base 10) number that represents an integral value.

### Boolean
A boolean (or *bool*) value represents a truth value, which can be either `true` or `false`.

### nil
The `nil` value denotes lack of value.  
Because internally it is interpreted as the Python object `NoneType`, it is not the same as an empty string, `False`, or 0 (zero).

### List
A list is a collection of objects, like arrays in other languages.  
To access a member of a list, use the index notation `list.#`, where `#` is the index integer starting at 0.

#### Attributes
| Name | Type | Value |
| :--- | :--- | :---- |
| `size`| integer | the size of the list |

### Keyword
A keyword is a special type of string which describes a value depending on the context where it is used.

#### Global Keywords
The following keywords are available in all contexts.

|  |  |
|--|--|
| Card types | `character`, `action`, `reaction` |
| United Attack | `ua2`, `ua3` |
| Game rules | `ab_trigger_fresh`, `ab_trigger_act`, `ab_instant_act`, `piercing`, `backup_fresh`, `play_char_bp_limit`, `dmg_combat_deal`, `attack_freeze`, `attack`, `backup_limit`, `play_removed` |
| Zones | `arena`, `ring`, `infront`, `hand`, `deck`, `discards`, `removed` |
| Piles | `hand`, `deck`, `discards`, `removed` |
| Phases | `activate`, `draw`, `main`, `attack`, `counter-attack` |

## Data Types
The following data types represent different parts of the game. They hold attributes than can be accessed with the dot notation `datatype.attribute`.

### Player
It is a representation of a player, which holds the data of that player.

#### Attributes
| Name | Type | Value |
| :--- | :--- | :---- |
| `hp`        | integer | life of the player |
| `sp`        | integer | SP of the player |
| `hand`      | list    | the player's hand |
| `discards`  | list    | the player's discard pile |
| `ring`      | list    | the player's ring |
| `ncDamaged` | bool    | whether the players was dealt non-combat damage this turn |
| `lostSP`    | integer | the amount of SP the player has lost this turn |

### Card
A card of the game.

#### Attributes
| Name | Type | Value |
| :--- | :--- | :---- |
| `bp`      | integer | the BP (bonus points) of the card |
| `lastbp`  | integer | the BP of the card before it leaved the ring |
| `ability` | string  | the ability type |

## Expressions
An expression is a piece of code that is evaluated as Python code, hence the rules of the Python language applies to expressions. Expressions are case-sensitive.

### Variables
The following variables are available in expressions:

| Name | Type | Value |
| :--- | :--- | :---- |
| `tgt`        | list    | current target cards |
| `prevTgt`    | list    | previous target cards |
| `uaBP`       | integer | united attack total BP |
| `me`         | Player  | the current player |
| `opp`        | Player  | the opponent player |
| `discarded`  | list    | cards that were discarded from the hand |
| `trashed`    | list    | cards that went to the removed pile |
| `destroyed`  | list    | cards that were destroyed |
| `moved`      | list    | cards that were moved from a pile to another pile (including the table) |
| `sacrificed` | list    | cards that were moved from a ring to he discard pile |
| `this`       | Card    | the card which effects is being executed |
| `attacker`   | Card    | an attacking card |
| `blocker`    | Card    | a blocking card |
| `trigger`    | Card    | the card that has triggered an effect |
| `alone`      | bool    | true if the card is the only card in its controller ring |
| `soloAttack` | bool    | true if the card that is attacking alone |
| `oppLostSP`  | bool    | true if an opponent has lost SP |
| `instant`    | string  | the "instant" ability |
| `triggered`  | string  | the "triggered" ability |
| `auto`       | string  | the "auto" ability |

Variables available in the following contexts: `each()`, `all...in`:

| Name | Type | Value |
| :--- | :--- | :---- |
| `card`     | Card | the current card in the list |
| `char`     | Card | the current character card in the list |
| `action`   | Card | the current action card in the list |
| `reaction` | Card | the current reaction card in the list |
   
Available functions in expressions:

| Function | Description |
| :------- | :---------- |
| `all <expr> in <list>` | returns `true` if all the elements of a given list are true |
| `isChar(card)`         | returns `true` if the given card is a character card |
| `flipCoin()`           | asks the player to choose Heads or Tails and returns a random boolean value depending on the player's selection |
| `inUAttack(card)`      | returns `true` if the given card is part of an United Attack |
| `getTargets('<filter>')` | get cards that match the given target filter string |

## Commenting
To comment a line of code, use the character `#`. The code after this character will be ignored by the parser.

## Syntax
RuleScript consists of a text-based content with a structure and syntax comprising key/value pairs (properties), delimited by newlines.

```ini
target = players
action = trash(5)
```

A group of properties form a **rule**.

### Rule
A rule is a group of one or more properties that form the actions a card can perform (the *rules* of the card). A rule can contain any number of properties.

```ini
[81b95f17-ba79-4f2f-aa7f-4808d6fad1ec]
target = characters[bp<=300]
action = bp(+500)
```

### Key / Value (Property)
The primary element in RulesScript is the **key/value** or *property*. A key has a name and a value, delimited by an equals sign (=). The name appears to the left of the equals sign.

```ini
name = value
```

Leading and trailing whitespaces around the property and the equals sign are ignored.

## Properties

### Target
The target property defines one or more targets in the game (card or player) to which apply the effects of the rule.

```ini
target = target filter; ...
```

Only one `target` property is allowed in a rule. Any other `target` rule after the first is ignored.

It is optional. The target can be inferred from the context of the `action` or `auto` properties, or defined by the commands `to()`, `target()` or `from()`. By default the target can be the current player or the current card.

It is volitional. By appending "?" to "target" the actions of the rule will be executed even if there are no matching targets.

```ini
target? = target filter
```

The value of the `target` property is one or several [Target Filter statement](#Target-Filter-Statement), concatenated by the semicolon character `;`.

### Target Filter statement
It is a string composed of several segments. All segments are optional, but a Target Filter statement must contain at least one segment.
```
<qty> type <pick> [filter] @ zone ::selector(args); ...
```

#### `<qty>`
The amount of targets to select. For cards, it will show the [card dialog](https://github.com/octgn/OCTGN/wiki/OCTGN-Python-3.1.0.2-API-Reference#carddlg) where the player would choose the amount of cards. For players, it will show a selection dialog.
Optional.

|  |  |
|--|--|
| Values   | Integer<br>Keyword |
| Syntax   | min<br>[min],max<br>Keyword |
| Keywords | `rint` — Selects `int` number of targets<br>`**` — Any number of cards, minimum 1 |

#### `type`
The type of the target(s) to select. It can be a player, a card by its card type (Character, Action or Reaction), a card by its subtype (Warrior, Pilot, Captain, etc.), or the name of card surrounded with double quotes.

Multiple types can be used by joining them with an operator.

|  |  |
|--|--|
| Operators | `,` — logical OR<br>`&` — logical AND |
| Values    | String<br>Keyword |
| Keywords  | `player` <br> `me` — current player<br> `opp` — opponent player<br> `this` — current card<br> `*` — any one card<br> `all` — all cards<br>`"<card name>"` — the name of a card |
| Prefixes  | `^` — other than the current card<br>`!` — logical NOT |
| Suffixes  | `s` — pluralize (one or more targets). Valid on Type, Subtype, card name, player or `*`. |
| Default   | `*` |

#### `<pick>`
The amount of cards to retrieve. Positive values means from the top of the pile, and negative values from the bottom of the pile. 

|  |  |
|--|--|
| Values   | Integer |
| Default   | 1 |

#### `[filter]`
Filters allow to be more specific about the cards to target, by applying matching rules based on the properties and/or the state of the cards.

Multiple filters can be defined by joining them with an operator.

|  |  |
|--|--|
| Operators | `,` — logical OR<br>`&` — logical AND |
| Values    | String — any card type or subtype<br>Keyword |
| Keywords  | `bp op integer` — compares the given BP with the BP of the card, where "op" is one of `=`, `>=` and `<=`<br>`bp:lowest` — selects the card or cards with the lowest BP <br>`sp op integer` — compares the given SP with the SP of the player, where "op" is one of: `=`, `>=` and `<=`<br>`backedup` — a character with at least one back-up <br>`attack` — an attacking character <br>`uattack` — a character in a United Attack <br>`block` — a defending character <br>`blocked` — an attacking character which is blocked by a defending character <br>`frozen` — a character in the freeze state <br>`fresh` — a character that has just entered the ring in this turn <br>`powerful` — a character with an ability <br>`powerless` — a character without abilities <br>`abinstant` — a character with an instant ability <br>`abtrigger` — a character with an activated ability <br>`abauto` — a character with an auto ability |
| Prefixes  | `-` — logical NOT<br>`^` — logical NOT |

#### `@ zone`
A zone is a playable area of the game where cards can exist.

|  |  |
|--|--|
| Values   | Keyword |
| Keyword   | `arena` — the game area with all the rings<br>`ring` — the area where players can play their cards<br>`infront` — the card in front of the current card<br>`hand` — cards in the "hand" of a player<br>`deck`<br>`discards`<br>`removed` — cards removed from the game |
| Prefixes   | `my` — (default)<br>`opp` — opponent<br>`ctrl` — the controller of the card<br>`same` — cards in the same zone. Only applies to the ring.<br>`any` |
| Default   | arena |

#### ::selector()
A selector executes a function to further filter the resulting target. The optional argument of the selector is an [expression](#Expressions).

|  |  |
|--|--|
| Values   | Keyword |
| Keyword   | `not(expr)` — excludes the cards selected by `expr` |

### Action
The `action` property defines the actions a card can perform, which effects will be applied to the given targets (if any).
```ini
action = action statement;
```
Multiple `action` properties are allowed. If there are two or more, a dialog will be show to choose an action. The text of the button for each action is inferred from the action statement or it can be defined with the [label](#Label) property.
```ini
action = action statement;
label  = "Label"
action = action statement;
```

It is optional, but a rule must contain at least either one `action` or one `auto` property.

The value of the `action` property is one or several [Action statements](#Action-Statement), concatenated by the semicolon character `;`. They will be executed in parallel but respecting the order. Note that effects in the same action statement (joined by `&,` `&&` or `||`) are executed sequentially.

### Action Statement
It is a string composed of several segments. Some segments are optional, but it must contain at least one effect.
```ini
action = {cost}: [[cond]] effect & effect && effect || effect to(target) restr; ...
```

#### `\{cost\}`
It represent the cost the player must pay to execute the action. If it is not present, then the action will be executed as soon as the card is in play.

|  |  |
|--|--|
| Values   | Keyword |
| Keyword   | `F` — freezes the current card<br>`S` — discard the current card<br>`S(target)` — discards the targeted cards<br>`D` — discards a card from the player's hand<br>`D(integer|target filter)` — discards a number of cards or the targeted cards from the player's hand |
| Optional   | true |


#### `[[cond]]`
A condition that must be fulfilled to execute the action.

|  |  |
|--|--|
| Values   | Keyword |
| Keyword   | `may` — will show a confirmation dialog whether the user wants to perform the action<br>`may 'Question'` — will show a confirmation dialog with the given text<br>`if expr` — Will execute the action only if the [expression](Expressions) is true |
| Optional   | true |

#### `effect`
An effect is a piece of code that performs changes in the game.

|  |  |
|--|--|
| Values    | [Command](#Action-Commands)<br>[Ability](#Action-Abilities) |
| Operators | `&` — will execute the next effect after the left effect<br>`&&` — logical AND, will stop execution of the action statement if the left effect failed<br>`||` — logical OR, will execute right effect if the left effect failed |
| Optional  | false |

##### Action Commands
A command has an identifier name followed by parenthesis `()`, which can contain zero or more [arguments](https://en.wikipedia.org/wiki/Parameter_(computer_programming)).

If the identifier name is suffixed with `?`, then the engine will show a confirmation dialog to choose whether to execute the effect or not.

|  |  |
|--|--|
| `activate(expr)`                  | executes the rules of the card that matches the expression |
| `alterCost(cardtype, int|=int)`   | modifies permanently the cost of a [card type](#Global-Keywords) or the cost of [united attacks](#Global-Keywords) by the given amount, or sets an exact (`=`) amount |
| `bp(int|xint|=int|expr)`          | modifies the BP of a character card by the given amount or expression, or multiplies it by `xint` ("x" + integer), or sets an exact (`=`) amount |
| `clear()`                         | removes any highlight from the card |
| `copyAbility(expr)`               | copies the rule of a card to the target card |
| `damage(int|expr)`                | does damage to the target player or character card |
| `destroy()`                       | moves a card in the ring to the discards pile |
| `disableRule(rule)`               | permanently disables a [rule](#Global-Keywords) of the game |
| `discard([int|target])`           | forces a player to discard the given amount of cards, or the cards returned by the target filter. Default: 1. |
| `draw([int|expression])`          | forces a player to draw the given amount of cards. Default: 1. |
| `each(expr in list => effect)`    | applies an effect for each card in the list that matches the expression |
| `each(target => effect)`          | applies an effect for each target matched by the target filter |
| `enableRule(rule)`                | permanently enables a [rule](#Global-Keywords) of the game |
| `freeze([bool])`                  | taps a card, or toggles its tap status if the argument is `true` |
| `hp(int|expr)`                    | modifies the HP of a player by the given amount or expression |
| `loseAbility()`                   | permanently removes the rules of a character card |
| `loseLife(int)`                   | a player loses the given amount of HP |
| `modCost(cardtype, int)`          | modifies the cost of a [card type](#Global-Keywords) by the given amount as long as the effect is in a `auto` property with an event |
| `modDamage(int)`                  | modifies the amount of damage dealt by a source by the given amount |
| `modRule(rule, arg)`              | modifies the value of a rule |
| `movePile(pile1, pile2)`          | moves all card from the [pile of cards](#Global-Keywords) `pile1` to `pile2`. Faster than `moveTo()` when moving all cards from a pile. |
| `moveRevealedTo(zone [, int])`    | moves the cards revealed when searching in a pile to the given zone, to the given position of the pile (default is top, negative values start counting from the bottom) |
| `moveTo(zone [, pos [, reveal]])` | moves a card to the given zone, to the given position of the pile (default is top, negative integers start counting from the bottom, `?` will show a dialog asking where to put the card) and reveals it to all players (by default it doesn't) |
| `moveToSlot()`                    | moves a character card in the ring to a slot chosen by the player |
| `peek()`                          | makes visible the targeted cards in a player's hands to the current player |
| `pileView(pile, state)`           | changes the [`view state`](https://github.com/octgn/OCTGN/wiki/OCTGN-Python-3.1.0.2-API-Reference#pileviewstate) of the given pile. States are `collapsed`, `pile` or `expanded`. |
| `playExtraChar()`                 | allows the current player to play a character card regardless of the limitation of characters per turn |
| `prophecy([int [, top|bottom]])`  | rearranges the given amount of cards from the given position of the deck. Default: 1, top. |
| `removeFromAttack()`              | removes from the attack the targeted character cards of the opponent |
| `reveal()`                        | reveals to all players the targeted cards |
| `reveal([pile])`                  | reveals to all players the given pile |
| `rndDiscard([int])`               | forces a player to discard a number of random cards. Alias of `discard(<rint>)` Default: 1. |
| `shuffle([pile])`                 | shuffles a pile. Default: current player's deck |
| `skip(phase)`                     | a player will skip his next [`phase`](#Global-Keywords) |
| `sp(int|=int|expr)`               | modifies the SP of a player by the given amount or expression, or sets an exact (`=`) amount |
| `steal([target])`                 | removes the rule from a character card and copies it to the current character card or to the character card matched by the given argument |
| `swapAbilities()`                 | swaps the rules between two targeted character cards |
| `swapChars()`                     | swaps the position in the ring between two targeted character cards |
| `swapPiles(pile1, pile2)`         | swaps all the cards between the two given piles |
| `transform("card model"|expr)`    | changes the targeted card to the given [card model](https://github.com/octgn/OCTGN/wiki/OCTGN-Python-3.1.0.2-API-Reference#cardmodel) (GUID) or the card matched by the expression |
| `trash([int])`                    | moves the given amount of cards from the player's deck to its discard pile. Default: 1 |
| `turns(int)`                      | adds the given amount of turns to the active player |
| `unfreeze()`                      | untaps a card |
| `unite()`                         | forces attacking characters that are not part of an United Attack to do an United Attack |

##### Action Abilities
Abilities are effects applied to players or character cards that are permanent and change how the target interacts with the game.

|  |  |
|--|--|
| Keywords | see [abilities](#Abilities) |
| Prefixes | `+` — adds the ability<br>`-` — removes the ability |

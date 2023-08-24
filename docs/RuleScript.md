# RuleScript
RuleScript is a scripting language designed for coding cards for OCTGN games, written in [Python](https://github.com/octgn/OCTGN/wiki/Scripting-in-Python) and inspired by [Wagic CardCode](https://github.com/WagicProject/wagic/wiki/CardCode). It automates the execution of the card mechanics to ease game play.

The syntax is similar to [INI files](https://en.wikipedia.org/wiki/INI_file), comprising key–value pairs to define the actions a card can do.

## Features
RuleScript is case insensitive, including identifiers, commands (functions) and strings. The only exception to this are [Expressions](#expressions), which are case-sensitive.

It can declare and use **variables**, this is a named reference or *identifier* for a particular type of data.

It has **functions** (reusable code snippet that can be called by other code) although functions are predefined (built-in) and cannot be created at runtime.

## Primitive Data Types
A Primitive in RuleScript is data that has no attributes and are not objects of the game.

### String
A string is a series of signs that represents a text.  
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
| `size`| integer | The size of the list |

### Keyword
A keyword is a special type of string which describes a value depending on the context where it is used.

#### Global Keywords
The following keywords are available in all contexts.

| Type | Keywords |
|:-|:-|
| Card type | `character`, `action`, `reaction` |
| United Attack | `ua2`, `ua3` |
| Game rule | `ab_trigger_fresh`, `ab_trigger_act`, `ab_instant_act`, `piercing`, `backup_fresh`, `play_char_bp_limit`, `dmg_combat_deal`, `attack_freeze`, `attack`, `backup_limit`, `play_removed` |
| Zone | `arena`, `ring`, `infront`, `hand`, `deck`, `discards`, `removed` |
| Pile | `hand`, `deck`, `discards`, `removed` |
| Phase | `activate`, `draw`, `main`, `attack`, `counter-attack` |

### Prefixes and Suffixes
Some primitives can be modified with a prefix or suffix value — this is another value that can be prepended or appended to the primitive. Prefixes and suffixes modify the value by being more specific.

## Data Types
The following data types represent different objects of the game. They hold attributes than can be accessed with the dot notation `datatype.attribute`.

### Player
It is a representation of a player, which holds the data of that player.

#### Attributes
| Name | Type | Value |
| :--- | :--- | :---- |
| `hp`        | integer | Life of the player |
| `sp`        | integer | SP of the player |
| `hand`      | list    | The player's hand |
| `discards`  | list    | The player's discard pile |
| `ring`      | list    | The player's ring |
| `ncDamaged` | bool    | Whether the players was dealt non-combat damage this turn |
| `lostSP`    | integer | The amount of SP the player has lost this turn |

### Card
A card of the game.

#### Attributes
| Name | Type | Value |
| :--- | :--- | :---- |
| `bp`      | integer | The BP (bonus points) of the card |
| `lastbp`  | integer | The BP of the card before it leaved the ring |
| `ability` | string  | The ability type |

## Expressions
An expression is a piece of code that is evaluated as [Python 2.7](https://docs.python.org/2.7/contents.html) code, hence the syntax and rules of the Python language applies to expressions. Expressions are case-sensitive.

### Expression Variables
The following variables are available in expressions:

| Name | Type | Value |
| :--- | :--- | :---- |
| `tgt`        | list    | Current targeted cards |
| `prevTgt`    | list    | Previous targeted cards |
| `uaBP`       | integer | Total BP of the United attack |
| `me`         | Player  | The current player |
| `opp`        | Player  | The opponent player |
| `discarded`  | list    | Cards that were discarded from the hand |
| `trashed`    | list    | Cards that went to the removed pile |
| `destroyed`  | list    | Cards that were moved to the discards pile |
| `moved`      | list    | Cards that were moved from a pile to another pile (including the table) |
| `sacrificed` | list    | Cards that were moved from a ring to he discard pile |
| `this`       | Card    | The card which effects is being executed |
| `attacker`   | Card    | An attacking card |
| `blocker`    | Card    | A blocking card |
| `trigger`    | Card    | The card that has triggered an effect or event |
| `alone`      | bool    | True if the card is the only card in its controller ring |
| `soloAttack` | bool    | True if the card that is attacking alone |
| `oppLostSP`  | bool    | True if an opponent has lost SP |
| `instant`    | string  | The "instant" ability |
| `triggered`  | string  | The "triggered" ability |
| `auto`       | string  | The "auto" ability |

Variables available in the following iteration contexts: `each()`, `all...in`:

| Name | Type | Value |
| :--- | :--- | :---- |
| `card`     | Card | The current card in the iteration |
| `char`     | Card | The current character card in the iteration |
| `action`   | Card | The current action card in the iteration |
| `reaction` | Card | The current reaction card in the iteration |
   
### Expression Functions
Available functions in expressions:

| Function | Description |
| :------- | :---------- |
| `all <expr> in <list>`   | Returns `true` if all the elements of a given list are true |
| `isChar(card)`           | Returns `true` if the given card is a character card |
| `flipCoin()`             | Asks the player to choose Heads or Tails and returns a random boolean value depending on the player's selection |
| `inUAttack(card)`        | Returns `true` if the given card is part of an United Attack |
| `getTargets('<filter>')` | Get cards that match the given target filter string.<br>Quotes in the argument are mandatory. |

Plus Python's [built-in functions](https://docs.python.org/2.7/library/functions.html).

## Syntax
RuleScript consists of a text-based content [encoded in UTF-8](https://peps.python.org/pep-3120/) with a structure and syntax comprising key/value pairs (properties), delimited by newlines.

```ini
key = value
```

A group of properties form a **rule**.

### Rule
A rule is a group of one or more properties that form the actions a card can perform (the *rules* of the card). A rule can contain any number of properties.

```ini
target = characters[bp<=300]
action = bp(+500)
```

### Key / Value (Property)
The primary element in RulesScript is the **key/value** or **property**. A property has a key or name and a value, delimited by an equals sign (=). The name appears to the left of the equals sign.

```ini
key = value
```

Leading and trailing whitespaces around the property and the equals sign are ignored.

### Commenting
To comment a line of code, use the sign `#`. The code after this sign will be ignored by the parser.

```ini
#target = players
action = trash(5) # Anything after the hash sign is ignored
```

### Identifier
An identifier is a word that contain the sign "_" and/or any of the following sign ranges: a-z, A-Z, 0-9.

## Properties

### Target Property
The target property defines one or more targets in the game (cards or players) to which apply the effects of the rule.

```ini
target = target filter; ...
```

Only one Target property is allowed in a rule. Any other Target property after the first is ignored.

It is optional. The target can be inferred from the context of the Action or Auto properties, or defined by the commands `to()`, `target()` or `from()`. By default the target is the current player or the current card.

It is volitional. By appending `?` to Target the actions of the rule will be executed even if there are no matching targets.

```ini
target? = target filter
```

The value of the Target property is one or several [Target Filter statement](#target-filter-statement), concatenated by the semicolon sign `;`.


### Action Property
The Action property defines the actions a card can perform, which effects will be applied to the given targets (if any).
```ini
action = action statement; ...
```
Multiple Action properties are allowed. If there are two or more, a dialog will be shown to choose an action. The text of the button for each action is inferred from the action statement or it can be defined with a [label](#label-property) property.
```ini
label  = "Label"
action = action statement
label  = "Label"
action = action statement
```

It is optional, but a rule must contain at least either one Action or one Auto property.

The value of the Action property is one or several [Action statements](#action-statement), concatenated by the semicolon sign `;`. They will be executed in parallel but respecting the order (from left to right). Note that effects in the same action statement (joined by `&,` `&&` or `||`) are executed sequentially.

### Abilities Property
Abilities are permanent properties of cards. They change how the card interacts with the game.

```ini
abilities = ability, ...
```

Only one Abilities property is allowed in a rule. Any other Abilities property after the first is ignored.

One or several [abilities](#abilities-statement) can be specified by separating them with the comma sign `,`.

### Auto Property
Like the Action property, the Auto property defines the actions and effects of the card. But unlike the Action property, the effects of the Auto property are always active or they trigger when a specific event occurs.
```ini
auto = auto statement; ...
```
Only one Auto property is allowed. Any other Auto property after the first is ignored.

It is optional, but a rule must contain at least either one Auto or one Action property.

An Auto property contain one or several [Auto statements](#auto-statement), joined by the semicolon sign `;`. They will be executed in parallel but respecting the order (from left to right).

### Label Property
The Label property adds a label to an Action property when it is rendered as an action button. The first Label property modifies the first Action property, the second label modifies the second action, and so on.

```ini
label  = "Action button 1"
action = action statement
label  = Action button 2
action = action statement
```

The value of the Label property is a String. Quotes are optional. 

Multiple Label properties are allowed, up to the number of Action properties.

### Requisite Property
The Requisite property defines targets which must exist in order to execute the rule of the card. It only works along with Action properties.

```ini
requisite = target filter && ...
```

It accepts one or more [Target Filter statement](#target-filter-statement) separated by the `&&` operator.

Only one Requisite property is allowed in a rule.

### Variables Property
The Variables property allows to create variables at runtime, by declaring the variable name and assigning a value to it. These variables will exists only during the execution of the rule of the card.

```ini
vars = varname := value ; ...
```
A variable has a name and a value, delimited by the operator `:=`.

The name of the variable must be a valid [identifier](#identifier).

> It is a common practice to start the variable name with an underscore `_`.

The value of the variable is one of the following:
+ Number
+ String
+ Boolean
+ A valid [expression](#expressions)

Example:
```ini
vars = _cards := getTargets('*s@myDiscards')
action = {F}: [[if _cards.size > 0]] bp(+500) to(*[bp<=300])
```

Several variables can be declared by separating them with the semicolon sign `;`.

Only one Variables property is allowed in a rule.

## Statements
A statement is a line of code commanding a task.

### Target Filter statement
The Target Filter statement defines the targets to match to apply the effects of a card.  
It is a string composed of several segments. All segments are optional, but a Target Filter statement must contain at least one segment.

The segments of the Target Filter statement:
```
<qty> type <pick> [filter] @ zone ::selector(args); ...
```

#### `<qty>`
The amount of targets to select. For cards, it will show the [card dialog](https://github.com/octgn/OCTGN/wiki/OCTGN-Python-3.1.0.2-API-Reference#carddlg) where the player would choose the amount of cards. For players, it will show a selection dialog.  

|  |  |
|:-|:-|
| Values   | Integer<br>Keyword |
| Syntax   | min<br>[min],max<br>Keyword |
| Keywords | `r#` — Selects `#` integer number of targets. `#` is optional (default 1).<br>`**` — Any number of cards, minimum 1 |
| Optional | true |

#### `type`
The type of the target(s) to select. It can be a player, a card by its card type (Character, Action or Reaction), a card by its subtype (Warrior, Pilot, Captain, etc.), or the name of card surrounded with double quotes.

Multiple types can be used by joining them with an operator.

|  |  |
|:-|:-|
| Operators | `,` — logical OR<br>`&` — logical AND |
| Values    | String<br>Keyword |
| Keywords  | `player` <br>`me` — current player<br>`opp` — opponent player<br>`this` — current card<br>`*` — any one card<br>`all` — all cards<br>`"<card name>"` — the exact name of a card |
| Prefixes  | `^` — other than the current card<br>`!` — logical NOT |
| Suffixes  | `s` — pluralize (one or more targets). Valid on Type, Subtype, card name, `player` or `*`. |
| Default   | `*` |

#### `<pick>`
The amount of cards to retrieve. Positive values means from the top of the pile, and negative values from the bottom of the pile.  

|  |  |
|:-|:-|
| Values   | Integer |
| Default  | 1 |
| Optional | true |

#### `[filter]`
Filters allow to be more specific about the cards to target, by applying matching rules based on the properties and/or the state of the cards.

Multiple filters can be defined by joining them with an operator.

|  |  |
|:-|:-|
| Operators | `,` — logical OR<br>`&` — logical AND |
| Values    | String — any card type or subtype<br>Keyword |
| Keywords  | `bp op integer` — compares the given BP with the BP of the card, where "op" is one of `==`, `>=` or `<=`<br>`bp:lowest` — selects the card or cards with the lowest BP <br>`sp op integer` — compares the given SP with the SP of the player, where "op" is one of: `==`, `>=` or `<=`<br>`backedup` — a character with at least one back-up <br>`attack` — an attacking character <br>`uattack` — a character in a United Attack <br>`block` — a defending character <br>`blocked` — an attacking character which is blocked by a defending character <br>`frozen` — a character in the freeze state <br>`fresh` — a character that has just entered the ring in this turn <br>`powerful` — a character with at least one ability <br>`powerless` — a character without abilities <br>`abinstant` — a character with an instant ability <br>`abtrigger` — a character with an activated ability <br>`abauto` — a character with an auto ability |
| Prefixes  | `-` — logical NOT<br>`^` — logical NOT |
| Optional  | true |

#### `@ zone`
A zone is a playable area of the game where cards can exist.

|  |  |
|:-|:-|
| Values   | Keyword |
| Keyword  | `arena` — the game area with all the rings<br>`ring` — the area where players can play their cards<br>`infront` — the card in front of the current card<br>`hand` — cards in the "hand" of a player<br>`deck`<br>`discards`<br>`removed` — cards removed from the game |
| Prefixes | `my` — (default)<br>`opp` — opponent player<br>`ctrl` — the controller of the card<br>`same` — cards in the same zone. Only applies to the ring.<br>`any` |
| Default  | `arena` |
| Optional | true |

#### ::selector()
A selector executes a function to further filter the resulting target. The optional argument of the selector is an [expression](#expressions).

|  |  |
|:-|:-|
| Values   | Keyword |
| Keyword  | `not(expr)` — excludes the cards selected by `expr` |
| Optional | true |

### Action Statement
An Action statement contains the effects of a card to apply immediately or when triggered.  
It is a string composed of several segments. Some segments are optional, but it must contain at least one effect.
```ini
{cost}: [[cond]] effect & effect && effect || effect to(target filter) restr; ...
```

#### `{cost}:`
It represent the cost the player must pay to execute the action. If it is not present, then the action will be executed as soon as the card is in play.

|  |  |
|:-|:-|
| Values   | Keyword |
| Keyword  | `F` — freezes the current card<br>`S` — discard the current card<br>`S(target)` — discards the targeted cards<br>`D` — discards a card from the player's hand<br>`D(integer)` — discards a number of cards from the player's hand<br>`D(target filter)` — discards the targeted cards from the player's hand<br>`D(<r#>)` — discards `#` integer number of cards from the player's hand. `#` is optional (default 1). |
| Optional | true |


#### `[[cond]]`
A condition that must be fulfilled to execute the action.

|  |  |
|:-|:-|
| Values   | Keyword |
| Keyword  | `may` — will show a confirmation dialog whether the user wants to perform the action<br>`may 'Question'` — will show a confirmation dialog with the given text<br>`if expr` — Will execute the action only if the [expression](Expressions) is true |
| Optional | true |

#### `effect`
An effect is a code statement that performs changes in the game.

|  |  |
|:-|:-|
| Values    | [Command](#action-commands)<br>[Ability](#action-abilities) |
| Operators | `&` — will execute the next effect after the left effect<br>`&&` — logical AND, will stop execution of the action statement if the left effect failed<br>`||` — logical OR, will execute right effect if the left effect failed |
| Optional  | false |

##### Action Commands
Action commands are like functions in other languages: a sequence of instructions that performs a specific task.

A command has an [identifier](#identifier) name followed by parenthesis `()`, which can contain zero or more [arguments](https://en.wikipedia.org/wiki/Parameter_(computer_programming)).

If the identifier name is suffixed with `?`, the engine will show a confirmation dialog to choose whether to execute the effect or not.

| Command | Task |
|:-|:-|
| `activate(expr)`                  | Executes the rules of the card that matches the expression |
| `alterCost(cardtype, int\|=int)`   | Modifies permanently the cost of a [card type](#global-keywords) or the cost of [united attacks](#global-keywords) by the given amount, or sets an exact (`=`) amount |
| `bp(int\|xint\|=int\|expr)`          | Modifies the BP of a character card by the given amount or expression, or multiplies it by `xint` (`x` + integer), or sets an exact (`=`) amount |
| `clear()`                         | Removes any [highlight](https://github.com/octgn/OCTGN/wiki/OCTGN-Python-3.1.0.2-API-Reference#cardhighlight) from the card |
| `copyAbility(expr)`               | Copies the rule of a card to the target card |
| `damage(int\|expr)`                | Does damage to the target player or character card |
| `destroy()`                       | Moves a card in the ring to the discards pile |
| `disableRule(rule)`               | Permanently disables a [rule](#global-keywords) of the game |
| `discard([int\|target])`           | Forces a player to discard the given amount of cards, or the cards returned by the target filter. Default: 1. |
| `draw([int\|expression])`          | Forces a player to draw the given amount of cards. Default: 1. |
| `each(expr in list => effect)`    | Applies an effect for each card in the list that matches the expression |
| `each(target => effect)`          | Applies an effect for each target matched by the target filter |
| `enableRule(rule)`                | Permanently enables a [rule](#global-keywords) of the game |
| `freeze([bool])`                  | Taps a card, or toggles its tap status if the argument is `true` |
| `hp(int\|expr)`                    | Modifies the HP of a player by the given amount or expression |
| `loseAbility()`                   | Permanently removes the rules of a character card |
| `loseLife(int)`                   | A player loses the given amount of HP |
| `modCost(cardtype, int)`          | Modifies the cost of a [card type](#global-keywords) by the given amount as long as the effect is in a `auto` property with an event |
| `modDamage(int)`                  | Modifies the amount of damage dealt by a source by the given amount as long as the effect is in a `auto` property with an event |
| `modRule(rule, value)`              | modifies the value of a rule |
| `movePile(pile1, pile2)`          | Moves all card from the [pile of cards](#global-keywords) `pile1` to `pile2`. Faster than `moveTo()` when moving all cards from a pile. |
| `moveRevealedTo(zone [, int])`    | Moves the cards revealed when searching in a pile to the given zone, to the given position of the pile (default is top, negative values start counting from the bottom) |
| `moveTo(zone [, pos [, reveal]])` | Moves a card to the given zone, to the given position of the pile (default is top, negative integers start counting from the bottom, `?` will show a dialog asking where to put the card) and reveals it to all players (by default it doesn't) |
| `moveToSlot()`                    | Moves a character card in the ring to a slot chosen by the player |
| `peek()`                          | Makes visible the targeted cards in a player's hands to the current player |
| `pileView(pile, state)`           | Changes the [`view state`](https://github.com/octgn/OCTGN/wiki/OCTGN-Python-3.1.0.2-API-Reference#pileviewstate) of the given pile. States are `collapsed`, `pile` or `expanded`. |
| `playExtraChar()`                 | Allows the current player to play a character card regardless of the limitation of characters per turn |
| `prophecy([int [, top\|bottom]])`  | Rearranges the given amount of cards from the given position of the deck. Default: 1, top. |
| `removeFromAttack()`              | Removes from the attack the targeted character cards of the opponent |
| `reveal()`                        | Reveals to all players the targeted cards |
| `reveal(pile)`                    | Reveals to all players the given pile |
| `rndDiscard([int])`               | Forces a player to discard a number of random cards. Alias of `discard(<rint>)` Default: 1. |
| `shuffle([pile])`                 | Shuffles a pile. Default: current player's deck |
| `skip(phase)`                     | Target player will skip his next [`phase`](#global-keywords) |
| `sp(int\|=int\|expr)`               | Modifies the SP of a player by the given amount or expression, or sets an exact (`=`) amount |
| `steal([target])`                 | Removes the rule from a character card and copies it to the current character card or to the character card matched by the given argument |
| `swapAbilities()`                 | Swaps the rules between two targeted character cards |
| `swapChars()`                     | Swaps the position in the ring between two targeted character cards |
| `swapPiles(pile1, pile2)`         | Swaps all the cards between the two given piles |
| `transform("card model"\|expr)`    | Changes the targeted card to the given [card model](https://github.com/octgn/OCTGN/wiki/OCTGN-Python-3.1.0.2-API-Reference#cardmodel) (GUID) or the card matched by the expression |
| `trash([int])`                    | Moves the given amount of cards from the player's deck to its discard pile. Default: 1 |
| `turns(int)`                      | Adds the given positive amount of turns to the active player |
| `unfreeze()`                      | Untaps a card |
| `unite()`                         | Forces attacking character cards that are not part of an United Attack to do an United Attack |

##### Action Abilities
Abilities are effects applied to players or character cards that are permanent and change how the target interacts with the game.

|  |  |
|:-|:-|
| Keywords | see [Abilities](#abilities-statement) |
| Prefixes | `+` — adds the ability<br>`-` — removes the ability |

#### `to(target filter)`
It defines the targets (cards or players) to which apply the effects of the rule.  
It is optional. By default the target is the current player or the current card (it is inferred from the context of the effects).

|  |  |
|:-|:-|
| Argument | [Target Filter statement](#target-filter-statement), concatenated by the semicolon sign `;`. |
| Default  | Current player or the current card |
| Alias    | `target()`, `from()` |
| Optional | True |

Like the volitional `target? =` property, with `to?()` the effects of the action statements will be executed even if there are no matching targets.

#### `restr`
Restrictions until when to apply the effects of an action statement.

|  |  |
|:-|:-|
| Values   | Keyword |
| Keywords | `ueot` — Until the end of the turn<br>`unac` — Until the next Action card is played<br>`uynt` — Until the beginning your next turn |
| Prefixes | `my` — The current player (default)<br>`opp` — opponent player |
| Optional | True |

### Abilities Statement
All abilities are keywords.

| Ability Name | Targets | Effect |
|:--------|:--------|:-------|
| unblockable     | Character | Cannot be blocked when it attacks |
| cantattack      | Character | Cannot attack |
| cantblock       | Character | Cannot block |
| unlimitedbackup | Character | Can receive any number of back-ups |
| unfreezable     | Character | Doesn’t freeze (tap) after a solo attack |
| pierce          | Character | Deals excess damage to the blocking player if it is blocked |
| preventpierce   | Character | Prevents piercing damage when blocking |
| rush            | Character | Can attack the turn it enters the ring |
| frosted         | Character | Doesn’t unfreeze (untap) as normal |
| cantplayac      | Player    | Cannot play Action cards |
| cantplayre      | Player    | Cannot play Reaction cards |

### Auto Statement
An Auto statement defines the effects of the [Auto property](#auto-property). It is a string composed of several segments.

The following is the default syntax. All segments are optional but the `effect` segment (it must contain at least one effect).
```ini
~event~ [[cond]] effect & effect to(target filter) restr; ...
```
When using hooks the syntax is the following:
```ini
?hook? [[cond if expr]]
```

#### `~event~`
It defines one or more game event listeners that when triggered will execute the Auto statement of the rules.

Several events can be specified by separating them with the comma sign `,`.

| Values    | Keyword |
|:----------|:--------|
| Keyword   | `activatephase` — beginning of the Activate phase<br>`drawphase` — beginning of the Draw phase<br>`blockphase` — beginning of the Block phase<br>`endphase` — beginning of the End phase<br>`cleanupphase` — beginning of the last phase of the turn<br>`handchanges` — the cards in the hand changes<br>`ringchanges` — the characters in a ring change<br>`removed` — a card is removed for the game<br>`powerless` — a character loses his abilities<br>`backedUp` — a character is backed-up<br>`beforePayCostAction` — before paying the cost of the card<br>`beforePayCostReaction` — before paying the cost of the card<br>`beforeDamage` — before damage is dealt<br>`cancelCombatDamage` — cancels combat damage done by a character<br>`playerCombatDamaged` — player is damaged by characters in combat<br>`attacks` — character attacks<br>`blocks` — character blocks<br>`blocked` — character is blocked |
| Prefixes  | `my` — (default)<br>`opp` — opponent player<br>`any` — any player |
| Suffixes  | `:this` — (default)<br>`:fromThis` — (default)<br>`:any` — listens for any object that triggers the event<br>`:once` — triggers only once and then deletes the event listener<br>`:action` — triggers for action cards<br>`:reaction` — triggers for reaction cards<br>`:char` — triggers for character cards |
| Optional  | true |

#### `?hook?`
Hooks are a way to modify the behaviour of the game life cycle. They trigger after an specific game event, and must be followed only by a condition evaluation `[[cond if expr]]` which result may cancel or allow the event default action.

Several hooks can be joined with the comma sign `,`.

| Values    | Keyword |
|:----------|:--------|
| Keyword   | `canBlock` — whether the character can block or not |
| Prefixes  | See [event prefixes](#event) |
| Suffixes  | See [events suffixes](#event) |

#### `[[cond]]`
See [Action statement conditions](#cond).

`[[cond if expr]]` conditions may create an event listener if there is no `~event~` segment defined.

#### `effect`
See [Action statement effects](#effect).

#### `to(target filter)`
See [Action statement to()](#to-target-filter).

#### `restr`
See [Action statement restrictions](#restr).

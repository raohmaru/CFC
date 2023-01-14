# RuleScript
RuleScript is an scripting language designed to code cards for OCTGN games, written in Python and inspired by [Wagic CardCode](https://github.com/WagicProject/wagic/wiki/CardCode). It automates the execution of the card mechanics to ease game play.

The syntax is similar to [INI files](https://en.wikipedia.org/wiki/INI_file), comprising key–value pairs to define the actions a card can do.

## Features
RuleScript is case insensitive, including identifiers, commands (functions) and strings. The only exception to this are Expressions, which are case-sensitive.

## Primitive Data Types
### String
A string is a series of characters that represents a text.  
String literals can be specified using single or double quotes, or no quotes at all (depending on the context).

### Integer
An integer is a decimal (base 10) number that represents an integral value.  

### Boolean
A boolean value represents a truth value, which can be either `true` or `false`.

### nil
The `nil` value denotes lack of value.  
Because internally it is interpreted as the Python object `NoneType`, it is not the same as an empty string, `False`, or zero.

### List
A list is a collection of objects, like arrays in other languages.  
To access a member of a list, use the index notation `list.#`, where `#` is the index integer starting at 0.

#### Attributes
| Name | Type | Value |
| :--- | :--- | :---- |
| `size`| integer | the size of the list |

### Keyword
A keyword is a special type of string which describes a value depending on the context where it is used.

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
| `getTargets('filter')` | get cards that match the given target filter string |

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

Leading and trailing whitespaces around the property are ignored.

## Properties
### Target
The target property defines one or more targets in the game (card or player) to which apply the effects of the rule.

```ini
target = target filter; ...
```

Only one `target` property is allowed in a rule. Any other `target` rule after the first is ignored.

It is optional. The target can be inferred from the context of the `action` or `auto` properties, or defined by the commands `to()`, `target()` or `from()`.

It is volitional. By appending "?" the actions of the rule will be executed even if there are no matching targets.

```ini
target? = target filter
```

The value of the `target` property is one or several Target Filter strings, concatenated by the character `;`.

### Target Filter String
It is composed of several segments. All segments are optional, but a Target Filter string must contain at least one segment.
```
<qty> type <pick> [filter] @ zone ::selector(args); ...
```

#### `<qty>`
The amount of targets to select. For cards, it will show the [card dialog](https://github.com/octgn/OCTGN/wiki/OCTGN-Python-3.1.0.2-API-Reference#carddlg) where the player would choose the amount of cards. For players, it will show a selection dialog.
Optional.

|  |  |
|---|---|
| Values   | Integer<br>Keyword |
| Syntax   | min<br>[min],max<br>Keyword |
| Keywords | `r[int]` — Selects `int` number of targets<br>`**` — Any number of cards, minimum 1 |

#### `type`
The type of the target(s) to select. It can be a player, a card by its card type (Character, Action or Reaction), a card by its subtype (Warrior, Pilot, Captain, etc.), or the name of card surrounded with double quotes.

Multiple types can be used by joining them with an operator.

|  |  |
|---|---|
| Operators | `,` — logical OR<br>`&` — logical AND |
| Values    | String<br>Keyword |
| Keywords  | `player` <br> `me` — current player<br> `opp` — opponent player<br> `this` — current card<br> `*` — any one card<br> `all` — all cards |
| Prefixes  | `^` — other than the current card<br>`!` — logical NOT |
| Suffixes  | `s` — pluralize (one or more targets). Valid on Type, Subtype, card name, player or `*`. |
| Default   | `*` |

#### `<pick>`
The amount of cards to retrieve. Positive values means from the top of the pile, and negative values from the bottom of the pile. 

|  |  |
|---|---|
| Values   | Integer |
| Default   | 1 |

#### filter
Filters allow to be more specific about the cards to target, by applying matching rules based on the properties and/or the state of the cards.

Multiple filters can be defined by joining them with an operator.

|  |  |
|---|---|
| Operators | `,` — logical OR<br>`&` — logical AND |
| Values    | String — any card type or subtype<br>Keyword |
| Keywords  | `bp [= | >= | <=] integer` — compares the given BP with the BP of the card <br>`bp:lowest` — selects the card or cards with the lowest BP <br>`sp [= | >= | <=] integer` — compares the given SP with the SP of the player <br>`backedup` — a character with at least one back-up <br>`attack` — an attacking character <br>`uattack` — a character in a United Attack <br>`block` — a defending character <br>`blocked` — an attacking character which is blocked by a defending character <br>`frozen` — a character in the freeze state <br>`fresh` — a character that has just entered the ring in this turn <br>`powerful` — a character with an ability <br>`powerless` — a character without abilities <br>`abinstant` — a character with an instant ability <br>`abtrigger` — a character with an activated ability <br>`abauto` — a character with an auto ability |
| Prefixes  | `-` — logical NOT<br>`^` — logical NOT |

#### `@ zone`
A zone is a playable area of the game where cards can exist.

|  |  |
|---|---|
| Values   | Keyword |
| Keyword   | `arena` — the game area with the rings<br>`ring`<br>`infront` — the card in front of the current card<br>`hand`<br>`deck`<br>`discards`<br>`removed` |
| Prefixes   | `my` — default<br>`opp` — opponent<br>`ctrl` — the controller of the card<br>`same` — only applies to the ring<br>`any` |
| Default   | arena |

#### ::selector()
A selector executes a function to further filter the resulting target. The optional argument of the selector is an [expression](#Expressions).

|  |  |
|---|---|
| Values   | Keyword |
| Keyword   | `not(expr)` — excludes the cards selected by `expr` |
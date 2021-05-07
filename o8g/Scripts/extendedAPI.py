# Python Scripts for the Card Fighters' Clash definition for OCTGN
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

#---------------------------------------------------------------------------
# Some extended constants
#---------------------------------------------------------------------------

Colors = Struct(**{
   'Black'    : '#000000',
   'Red'      : '#CC0000',
   'Blue'     : '#2C6798',
   'LightBlue': '#5A9ACF',
   'Orange'   : '#b35900'
})


#---------------------------------------------------------------------------
# Extended API
#---------------------------------------------------------------------------

try:
   import clr
   # Start to hack :)
   clr.AddReference("Octgn")
   clr.AddReference("Octgn.Core")
   clr.AddReference("Octgn.JodsEngine") # 3.4.350.0
   # clr.AddReference("Octgn.DataNew")
   import Octgn
   import System
except (IOError, ImportError):
   settings['ExtAPI'] = False
   whisper("There was an error while starting the game and some functionalities won't be available.\nPlease restart OCTGN.")
   
class ExtendedApi(object):
# An extended API with methods that directly call C# methods
   def __init__(self):
      # self._game = Octgn.Program.GameEngine.Definition  # 3.4.286.0 
      self._game = Octgn.Core.DataManagers.GameManager.Get().GetById(Guid.Parse(GameId))  # 3.4.350.0
      self._gameMethods = Octgn.Core.DataExtensionMethods.GameExtensionMethods
      self._cardMethods = Octgn.Core.DataExtensionMethods.CardExtensionMethods
      self.customPlayer = False
      
   @property
   def game(self): return self._game
   
   def getSets(self):
      """Gets a list with the sets of the game.
      Returns: [Octgn.DataNew.Entities.Set]
      """
      sets = Octgn.Core.DataManagers.SetManager.Get().Sets
      return [set for set in sets]
      
      
   def getSetByModel(self, setModel):
      """Gets a set by its GUID.
      Returns: Octgn.DataNew.Entities.Set
      """
      return self._gameMethods.GetSetById(self._game, Guid.Parse(setModel))
      
      
   def getSetByCardData(self, cardData):
      """Gets a set by the given card data.
      Returns: Octgn.DataNew.Entities.Set
      """
      return self._cardMethods.GetSet(cardData)
      
      
   def getCardById(self, cardId):
      """Gets a card by its internal id.
      Examples: _extapi.getCardById(card._id)
      Returns: Octgn.Play.Card
      """
      return Octgn.Play.Card.Find(cardId)
      
      
   def getCardDataByName(self, cardName):
      """Gets a card data by its name.
      Returns: Octgn.DataNew.Entities.Card
      """
      return self._gameMethods.GetCardByName(self._game, cardName)
      
      
   def getCardDataByModel(self, cardModel):
      """Gets a card data by its GUID.
      Returns: Octgn.DataNew.Entities.Card
      """
      return self._gameMethods.GetCardById(self._game, Guid.Parse(cardModel))
      
      
   def getCardIdentityById(self, cardId):
      """Gets a card identity by its internal id.
      Examples: _extapi.getCardIdentityById(card._id)
      Returns: Octgn.Play.CardIdentity
      """
      return Octgn.Play.CardIdentity.Find(cardId)
      
      
   def getCardDataById(self, cardId):
      """Gets a card data by its internal id.
      Examples: _extapi.getCardDataById(card._id)
      Returns: Octgn.DataNew.Entities.Card
      """
      card = self.getCardIdentityById(cardId)
      if card is None:
         return None
      return card.Model
      
      
   def getCardProperties(self, cardData, propset=''):
      """Gets all properties from a card data given the property set name (aka alternate).
      Returns: dict
      """
      cardPropertySet = cardData.PropertySets[propset]
      props = {}
      # Keys are objects Octgn.DataNew.Entities.PropertyDef
      for k in cardPropertySet.Properties.Keys:
         props[k.Name] = cardPropertySet.Properties.Item[k]
      return props
      
      
   def getCardProperty(self, cardData, propName, propset=''):
      """Gets a value of a property from a card data given the property set name (aka alternate).
      Returns: str
      """
      cardPropertySet = cardData.PropertySets[propset]
      # Keys are objects Octgn.DataNew.Entities.PropertyDef
      prop = [p for p in cardPropertySet.Properties.Keys if p.Name == propName]
      if len(prop) > 0:
         return cardPropertySet.Properties.Item[prop[0]]
      return None
      
      
   def setCardProperty(self, cardData, propName, value, propset=''):
      """Sets the value of a property of a card data given the property set name (aka alternate).
      """
      cardPropertySet = cardData.PropertySets[propset]
      # Keys are objects Octgn.DataNew.Entities.PropertyDef
      prop = [p for p in cardPropertySet.Properties.Keys if p.Name == propName]
      if len(prop) > 0:
         cardPropertySet.Properties.Item[prop[0]] = value
         
         
   def getCardProxyUri(self, set, cardData):
      """Gets the absolute path to the proxy image of the given card data.
      Returns: str
      """
      return System.Uri(Path.Combine(set.ProxyPackUri, self._cardMethods.GetImageUri(cardData) + ".png"))
         
         
   def generateProxy(self, cardData, alternate):
      """Generates and writes into the disk a new proxy image for the given property set (aka alternate) name.
      """
      currAlternate = cardData.Alternate
      cardData.Alternate = alternate
      set = self.getSetByCardData(cardData)
      uri = self.getCardProxyUri(set, cardData)
      files = Directory.GetFiles(set.ProxyPackUri, self._cardMethods.GetImageUri(cardData) + ".png")
      if files.Length == 0:
         cropPath = Path.Combine(Path.Combine(set.ImagePackUri, "Crops"))
         crop = None
         if Directory.Exists(cropPath):
            crops = Directory.GetFiles(cropPath, cardData.ImageUri + ".jpg")
            try:
               if crops.Length == 0:
                  self._gameMethods.GetCardProxyDef(self._game).SaveProxyImage(self._cardMethods.GetProxyMappings(cardData), uri.LocalPath)
               else:
                  self._gameMethods.GetCardProxyDef(self._game).SaveProxyImage(self._cardMethods.GetProxyMappings(cardData), uri.LocalPath, crops[0])
            except EnvironmentError:
               self.warning('An error occurred while generating the proxy image.')
      cardData.Alternate = currAlternate
      
      
   def addMessage(self, message):
      try:
         Octgn.Program.GameMess.AddMessage(message)
      except AttributeError:
         whisper(message.Message)
      
   def warning(self, str):
      self.addMessage(Octgn.Core.Play.WarningMessage(replIdsWithNames(str), {}))
      
            
   def system(self, str):
      self.addMessage(Octgn.Core.Play.SystemMessage(replIdsWithNames(str), {}))
      
      
   def whisper(self, str, color = Colors.Black, bold = False):
      msg = replIdsWithNames(str)
      customPlayer = CustomPlayer(color, bold)
      if bold:
         customPlayer.name = msg
         msg = ''
      update()  # To make next function work if this has been invoked from a remote call
      self.addMessage(Octgn.Core.Play.PlayerEventMessage(customPlayer, msg, {}))
      del customPlayer
      
      
   def notify(self, str, color = Colors.Black, bold = False):
      self.whisper(str, color, bold)
      if len(players) > 1:
         remoteCall(players[1], "_extapi_whisper", [str, color, bold])
      
      
# Make it global
if settings['ExtAPI']:
   _extapi = ExtendedApi()
   # Alias for remoteCall()
   _extapi_whisper = _extapi.whisper


#---------------------------------------------------------------------------
# Utilities
#---------------------------------------------------------------------------

# Custom player object to format text messages
class CustomPlayer(Octgn.Core.Play.IPlayPlayer):
   id = 555
   def __init__(self, color = Colors.Black, bold = False):
      # `color` is a System.Windows.Media.Color C# object, which is not available as a Python object
      self.color = Octgn.Core.Play.BuiltInPlayer.Notify.Color.FromRgb(*hexToRGB(color))
      self.name = u'\u200B'  # Zero-width space character
      CustomPlayer.id += 1
      self.id = CustomPlayer.id
      
   # Getters that IronPython calls when getting a property
   def get_Color(self):
      return self.color
      
   def get_Name(self):
      return self.name
      
   def get_Id(self):
      return self.id
      
   def get_State(self):
      return Octgn.Core.Play.PlayerState.Connected
      
   def ToString(self):
      return self.name


def hexToRGB(hex):
   hex = hex.lstrip('#')
   return list(int(hex[i:i+2], 16) for i in (0, 2, 4))

'''
Scribble - a DND information manager to make campaign note taking a little easier and computer-based
Authors: sun & RogueFyker

Features:
- DND Dice Rolls from 2 - 20 sided dice
- manage a personal database of items, enemies, locations, spells, equipment, and more!
- battleboard feature; visualize your fights with a tiled 2D grid you can place your character, allies, and enemies on
- tallies how many deaths, beers consumed, and enemies slain during campaign!

Code Format (in order):
- imports
- global variables / constants
- classes
- private functions
- public functions
- while loop action logic function
'''
import PySimpleGUI as sg # library needed for graphical elements, website: https://www.pysimplegui.org/en/latest/
import json # library needed for .json parsing and manipulation
import configparser # library needed to parse the 'config.ini' file located in 'settings'
import random # library needed for the randomness of a dice roller

CONFIG = 'config.ini'
INVENTORY_JSON = 'inventory.json'
ENEMY_JSON = 'enemies.json'
LOCATION_JSON = 'locations.json'
THEME = 'Topanga'
CURRENT_WINDOW = None

class Item:
    __name = None
    __desc = None
    __count = None # how many of this item you have
    __activeOrPassive = None # is a consumable or a passive item
    __key = None # cannot be removed from inventory

    def __init__(self, values):
        self.__name = values['-Item Name-']
        self.__desc = values['-Item Desc-']
        self.__count = values['-Item Count-']
        self.__activeOrPassive = self.activeOrPassive(values)
        self.__key = self.keyOrNotKey(values)

    def getName():
        return __name
    def getDesc():
        return __desc
    def getCount():
        return __count
    def getActiveOrPassive():
        return __activeOrPassive
    def getKey():
        return __key

    def setName(self, a):
        self.__name = a
    def setDesc(self, a):
        self.__desc = a
    def setCount(self, a):
        self.__count = a
    def setActiveOrPassive(self, a):
        self.__activeOrPassive = a
    def setKey(self, a):
        self.__key = a

    # determine weither or not the item is active or passive
    def activeOrPassive(self, values):
        if bool(values['-Item Passive-']) == True:
            return 'Passive'
        else:
            return 'Active'

    # determine weither or not the item is permanant to your inv.
    def keyOrNotKey(self, values):
        if bool(values['-Item Key-']) == True:
            return 'Key'
        else:
            return 'Not Key'

    # check if all variables have a value
    def allFieldsFilled(self):
        values = self.toDict()
        for k in values.values():
            if bool(k) == False:
                return False
        return True

    # convert class data into dictionary and return
    def toDict(self):
        return {
            'name': self.__name,
            'desc': self.__desc,
            'count': self.__count,
            'activeOrPassive': self.__activeOrPassive,
            'key': self.__key
        }

# Stats - data container for statistical information about your character, enemies, allies
class Stats:
    __hp = None
    __str = None
    __dex = None
    __con = None
    __int = None
    __wis = None
    __cha = None

    def __init__(self, hp):
        self.__hp = hp

    # convert class data into dictionary and return
    def toDict(self):
        return {
            'health': self.__hp,
            'strength': self.__str,
            'dexterity': self.__dex,
            'constitution': self.__con,
            'intelligence': self.__int,
            'wisdom': self.__wis,
            'charisma': self.__cha
        }

# Enemy - their stats, dropped items, equipment, name and description, and optional .PNG photo of enemy for battleboard
class Enemy:
    __name = None
    __desc = None
    __stats = None

    def __init__(self, name, desc):
        self.__name = name
        self.__desc = desc

    # convert class data into dictionary and return
    def toDict(self):
        return {
            'name': self.__name,
            'desc': self.__desc
        }

# takes a dictionary and string as input, saves data to fileName.json
def saveToJson(info, fileName):
    with open(fileName, 'w') as jsonFile:
        json.dump(info, jsonFile, indent = 2)
        print(f'Successfully entered info into {fileName}')

# returns a dictionary containing all data from .json file
def loadJsonFile(fileName):
    try:
        with open(fileName, 'r') as jsonFile:
            # Attempt to load JSON data from the file
            try:
                dndItems = json.load(jsonFile)
                if not isinstance(dndItems, list):
                    dndItems = []
                return dndItems
            except json.decoder.JSONDecodeError:
                print(f"Error decoding JSON from {fileName}. Returning an empty list.")
                return []
    except FileNotFoundError:
        print(f"{fileName} not found. Creating a new file.")
        with open(fileName, 'w') as jsonFile:
            json.dump([], jsonFile)
        return []

# formats the inventory add/remove display
def createLayoutMenu():
    return [[sg.Menu([['Add/Remove', ['Inventory', 'Enemies', 'Locations']], ['Search', ['Search']], ['Dice', ['Roller']], ['Settings', ['Edit Config']], ['Credits'], ['Quit']])]]

def createLayoutInv():
    return [[sg.Text('Add Item', font='_ 14')],
            [sg.Text('Name:'), sg.Input(k = '-Item Name-', do_not_clear=False)],
            [sg.Text('Desc:'), sg.Input(k = '-Item Desc-', do_not_clear=False)],
            [sg.Text('Count:'), sg.Input(k = '-Item Count-', do_not_clear=False)],
            [sg.Radio('Active', 1, key='-Item Active-'), sg.Radio('Passive', 1, key='-Item Passive-')],
            [sg.Radio('Key', 2, key='-Item Key-'), sg.Radio('Not Key', 2, key='-Item NotKey-')]]

# formats the enemy add/remove display
def createLayoutEnemy():
    return [[sg.Text('Enemy')],
            [sg.Text('Name:'), sg.Input(k = '-Enemy Name-', do_not_clear=False)],
            [sg.Text('Desc:'), sg.Input(k = '-Enemy Desc-', do_not_clear=False)]]

# formats the dice rolling display
def createLayoutDice():
    return [[sg.Text('Dice Roller', font='_ 14', justification='center', expand_x=True)],
            [sg.Text('# of Dice'), sg.Input(k ='-Dice Numbers-', do_not_clear=False, s=(10,1)), sg.Text('# of Sides'), sg.Input(k ='-Dice Sides-', do_not_clear=False, s=(10,1)), sg.Button('Roll')],
            [sg.Text('Number Rolled - ') ,sg.Text(s=(20,1), key = '-Output-')]]

def createLayoutSearch():
    return [[sg.Text('Search Database', font='_ 14', justification='center', expand_x=True)],
            [sg.Text('Name:'), sg.Input(k='-Search-', do_not_clear=False, s=(20, 1))],
            [sg.Output(s=(75,13))]]

# formats the button layout
def createLayoutButtons():
    return [[sg.Button('Enter')]]

# return the created mainMenu window
def makeMainMenuWindow():
    sg.theme(THEME) # set color palette / theme of application
    layout_final = [[createLayoutMenu()],
                    [sg.Text('Welcome to Scribble!', font='_ 14', justification='c', expand_x=True)]]
    return sg.Window('Scribble', layout_final, size=(800, 400))

def makeInventoryWindow():
    layout_final = [[createLayoutMenu()],
                    [createLayoutInv()],
                    [createLayoutButtons()]]
    return sg.Window('Scribble', layout_final, size=(800,400))

def makeEnemyWindow():
    layout_final = [[createLayoutMenu()],
                    [createLayoutEnemy()],
                    [createLayoutButtons()]]
    return sg.Window('Scribble', layout_final, size=(800,400))

def makeDiceWindow():
    layout_final = [[createLayoutMenu()],
                    [createLayoutDice()]]
    return sg.Window('Scribble', layout_final, size=(800,400))

def makeSearchWindow():
    layout_final = [[createLayoutMenu()],
                    [createLayoutSearch()],
                    [createLayoutButtons()]]
    return sg.Window('Scribble', layout_final, size=(800,400))

def invMenuLogic(values):
    item = Item(values) # create item object

    # if inventory fields have data, add them to json
    if bool(item.allFieldsFilled()):
        existingItems = loadJsonFile(INVENTORY_JSON)
        existingItems.append(item.toDict())
        saveToJson(existingItems, INVENTORY_JSON)
        print("Successfully printed to json")
    else:
        print("You are missing fields in item")

def enemiesMenuLogic(values):
    enemy = Enemy(values['-Enemy Name-'], values['-Enemy Desc-'])

    # if enemy fields have data, add them to json
    if bool(values['-Enemy Name-']) == True and bool(values['-Enemy Desc-']) == True:
        existingEnemies = loadJsonFile(ENEMY_JSON)
        existingEnemies.append(enemy.toDict())
        saveToJson(existingEnemies, ENEMY_JSON)
    else:
        print("You are missing fields in enemy")

def diceMenuLogic(window, values):
    sides = int(values['-Dice Sides-'])
    numOfDie = int(values['-Dice Numbers-'])
    finalValue = 0
    for x in range(0, numOfDie):
        numberRolled = random.randrange(1, sides+1)
        finalValue = finalValue + numberRolled
    if numberRolled == sides and sides == 20:
        window['-Output-'].update(str(finalValue) + ' - CRIT!')
    else:
        window['-Output-'].update(finalValue)

def searchMenuInventoryLogic(values):
    input_value = values['-Search-'].lower()  # Convert input to lowercase
    inventory_items = loadJsonFile(INVENTORY_JSON) # Load inventory data from JSON
    matching_items = [] # Create a list to store matching items

    # Iterate over inventory items and check if the input matches item names
    for item in inventory_items:
        if item['name'].lower() == input_value:
            matching_items.append(item)

    # Display matching items or inform user if no match is found
    if matching_items:
        for item in matching_items:
            print(f"Item Name: {item['name']}")
            print(f"Description: {item['desc']}")
            print(f"Count: {item['count']}")
            print(f"Active/Passive: {item['activeOrPassive']}")
            print(f"Key/Not Key: {item['key']}")
            print('-' * 30)
    else:
        print('Item not found in database')


# all program logic
def runApplication(window):
    while True:
        event, values = window.read() # when program is interacted with, capture that action as a variable

        # if 'X' button is pressed, close program and break from while loop
        if event == sg.WIN_CLOSED:
            break

        # if 'Inventory' is selected in the Menu
        if event == 'Inventory':
            window.close()
            window = makeInventoryWindow()
            CURRENT_WINDOW = 'Inventory'

        # if 'Enemy' is selected in the Menu
        if event == 'Enemies':
            window.close()
            window = makeEnemyWindow()
            CURRENT_WINDOW = 'Enemies'

        # if 'Dice -> Roller' is selected in the Menu
        if event == 'Roller':
            window.close()
            window = makeDiceWindow()
            CURRENT_WINDOW = 'Roller'

        # if 'Search -> Find' is selected in the Menu
        if event == 'Search':
            window.close()
            window = makeSearchWindow()
            CURRENT_WINDOW = 'Search'

        # logic for each window: Inventory, Enemies
        if event == 'Enter' and CURRENT_WINDOW == 'Inventory':
            invMenuLogic(values)
        elif event == 'Enter' and CURRENT_WINDOW == 'Enemies':
            enemiesMenuLogic(values)
        elif event == 'Roll' and CURRENT_WINDOW == 'Roller': #Large piece for rolling, took a lot more lines than I thought
            diceMenuLogic(window, values)
        elif event == 'Enter' and CURRENT_WINDOW == 'Search':
            searchMenuInventoryLogic(values)


window = makeMainMenuWindow() # create the first initial window
runApplication(window) # start running program logic
window.close() # when the while loop in `runApplication` is broken, close the application

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
from pathlib import Path

#global variables / constants
CONFIG = 'config.ini'
INVENTORY_JSON = 'inventory.json'
ENEMY_JSON = 'enemies.json'
THEME = 'Topanga'
CURRENT_WINDOW = None

# classes
# Item - consumables, foods, passive, etc
class Item:
    # __private variables
    __name = None
    __desc = None
    __count = None # how many of this item you have
    __activeOrPassive = None # is a consumable or a passive item
    __key = None # cannot be removed from inventory

    # constructor
    def __init__(self, name, desc, count, key):
        self.__name = name
        self.__desc = desc
        self.__count = count
        self.__activeOrPassive = 'Active'
        self.__key = key

    # convert class data into dictionary and return
    def toDict(self):
        return {
            'name': self.__name,
            'desc': self.__desc,
            'count': self.__count,
            'activeOrPassive': self.__activeOrPassive,
            'key': self.__key
        }

# Stats = data container for statistical information about your character, enemies, allies
class Stats:
    # private variables
    __hp = None
    __str = None
    __dex = None
    __con = None
    __int = None
    __wis = None
    __cha = None

    # constructor
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
    # private variables
    __name = None
    __desc = None
    __stats = None

    # constructor
    def __init__(self, name, desc):
        self.__name = name
        self.__desc = desc

    # convert class data into dictionary and return
    def toDict(self):
        return {
            'name': self.__name,
            'desc': self.__desc
        }

# public functions
# saveToJson - takes a dictionary and string as input, saves data to fileName.json
def saveToJson(info, fileName):
    with open(fileName, 'w') as jsonFile:
        json.dump(info, jsonFile, indent = 2)
        print(f'Successfully entered info into {fileName}')

# loadJsonFile - returns a dictionary containing all data from .json file
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

def ItemActiveOrPassive(values):
    if values['Active'] == True:
        return True
    else:
        return False

def createLayoutMenu():
    return [[sg.Menu([['Add/Remove', ['Inventory', 'Enemies', 'Locations']], ['Settings', ['Edit Config']], ['Credits'], ['Quit']])]]

def createLayoutInv():
    return [[sg.Text('Add Item', font='_ 14')],
            [sg.Text('Name:'), sg.Input(k = '-Item Name-', do_not_clear=False)],
            [sg.Text('Desc:'), sg.Input(k = '-Item Desc-', do_not_clear=False)],
            [sg.Text('Count:'), sg.Input(k = '-Count-', do_not_clear=False)],
            [sg.Radio('Active', 1, key='-Active-'), sg.Radio('Passive', 1, key='-Passive-')],
            [sg.Radio('Key', 2, key='-Key-')]]

def createLayoutEnemy():
    return [[sg.Text('Enemy')],
            [sg.Text('Name:'), sg.Input(k = '-Enemy Name-', do_not_clear=False)],
            [sg.Text('Desc:'), sg.Input(k = '-Enemy Desc-', do_not_clear=False)]]

def createLayoutButtons():
    return [[sg.Button('Enter')]]

# return the created mainMenu window
def makeMainMenuWindow():
    # set color palette / theme of application
    sg.theme(THEME)

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

def invMenuLogic(values):
    item = Item(values['-Item Name-'], values['-Item Desc-'], values['-Count-'], values['-Key-'])

    # if inventory fields have data, add them to json
    if bool(values['-Item Name-']) == True and bool(values['-Item Desc-']) == True and bool(values['-Count-']) == True and bool(values['-Key-']):
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

# all program logic
def runApplication(window):
    while True:
        # when program is interacted with, capture that action as a variable
        event, values = window.read()

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

        # logic for each window: Inventory, Enemies
        if event == 'Enter' and CURRENT_WINDOW == 'Inventory':
            invMenuLogic(values)
        elif event == 'Enter' and CURRENT_WINDOW == 'Enemies':
            enemiesMenuLogic(values)

window = makeMainMenuWindow() # create the first initial window
runApplication(window) # start running program logic
window.close() # when the while loop in `runApplication` is broken, close the application

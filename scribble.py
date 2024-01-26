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
- makeWindow
- while loop action logic
'''
import PySimpleGUI as sg # library needed for graphical elements, website: https://www.pysimplegui.org/en/latest/
import json # library needed for .json parsing and manipulation
import configparser # library needed to parse the 'config.ini' file located in 'settings'

#global variables / constants
CONFIG = 'settings/config.ini'
INVENTORY_JSON = 'data-base/inventory.json'

# classes
# Item - consumables, foods, passive, etc
class Item:
    # __private variables
    __name = None
    __desc = None
    __count = None
    __consumable = None
    __activeOrPassive = None
    __key = None

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

# makeWindow - build the application, not deploy it yet
def makeWindow():
    # set color palette / theme of application
    sg.theme('Topanga')

    # list containing data input elements for items and inventory management
    layout_inv = [[sg.Text('Add Item')],
                  [sg.Text('Name:'), sg.Input(k = '-Item Name-')],
                  [sg.Text('Desc:'), sg.Input(k = '-Item Desc-')]]

    # list containing data input elements for enemy management
    layout_enemy = [[sg.Text('Enemy')],
                    [sg.Text('Name:'), sg.Input(k = '-Enemy Name-')],
                    [sg.Text('Desc:'), sg.Input(k = '-Enemy Desc-')]]

    # list containing button elements for GUI interaction
    layout_buttons = [[sg.Button('Enter')]]

    # layout containing all previously made layouts
    layout_final = [[sg.Col(layout_inv, p=0), sg.Col(layout_enemy, p=0)],
                    [layout_buttons]]

    # create a window and add list of elements to window as a parameter in it's constructor
    return sg.Window('Scribble', layout_final)

# calls makeWindow, application is built and deployed here
window = makeWindow()

'''
needed for closing program properly
runs indefinite 'action listener' that captures actions. Like clicking buttons, typing, etc.
actions that are made are set equal to the 'event' and 'values' variable.

if 'event' is clicking the X close button, while loop breaks and ends program
'''
while True:
    # when program is interacted with, capture that action as a variable
    event, values = window.read()

    # if 'X' button is pressed, close program and break from while loop
    if event == sg.WIN_CLOSED:
        break

    # if 'enter' is pressed, enter item information into 'inventory.json'
    if event == 'Enter':
        # create dictionary of item information
        item = Item(values['-Item Name-'], values['-Item Desc-'])
        enemy = Enemy(values['-Enemy Name-'], values['-Enemy Desc-'])

        # (DOES NOT WORK) if input fields are empty, don't save to the .json
        if '' not in values or ' ' not in values:
            existingItems = loadJsonFile(INVENTORY_JSON)
            existingItems.append(item.toDict())
            saveToJson(existingItems, INVENTORY_JSON)
            print("Successfully printed to json")

window.close()

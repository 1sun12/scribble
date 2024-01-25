'''
Scribble - a DND information manager to make campaign note taking a little easier and computer-based
Authors: sun & RogueFyker

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
CONFIG =
INVENTORY_JSON = 'data-base/inventory.json'

# classes
# Item - consumables, foods, passive, etc
class Item:
    # __private variables
    __name = None
    __desc = None

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

# makeWindow - build the application, not deploy it yet
def makeWindow():
    # set color palette / theme of application
    sg.theme('Topanga')

    # create a 'list' containing elements, the list is later added to the window with elements in it's indexes'
    layout_inv = [[sg.T(s=20), sg.Text('Add Item')],
                  [sg.Text('Item Name:'), sg.Input(k = '-Item Name:-')],
                  [sg.Text('Item Desc:'), sg.Input(k = '-Item Desc:-')],
                  [sg.Button('Enter')]]

    # create a window and add list of elements to window as a parameter in it's constructor
    return sg.Window('Scribble', layout_inv)

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
        item = Item(values['-Item Name:-'], values['-Item Desc:-'])
        existingItems = loadJsonFile(INVENTORY_JSON)
        existingItems.append(item.toDict())
        saveToJson(existingItems, INVENTORY_JSON)

window.close()

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
import os # interact with the file system and other operating system features
import glob # search for files with a specific pattern

CONFIG = 'config.ini'
INVENTORY_JSON = 'inventory.json'
ENEMY_JSON = 'enemies.json'
LOCATION_JSON = 'locations.json'
STATS_JSON = 'stats.json'
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
        self.__count = int(values['-Item Count-'])
        self.__activeOrPassive = self.activeOrPassive(values)
        self.__key = self.keyOrNotKey(values)

    def getName(self):
        return self.__name
    def getDesc(self):
        return self.__desc
    def getCount(self):
        return self.__count
    def getActiveOrPassive(self):
        return self.__activeOrPassive
    def getKey(self):
        return self.__key

    def setName(self, a):
        self.__name = a
    def setDesc(self, a):
        self.__desc = a
    def setCount(self, a):
        self.__count = int(a)
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
    __lvl = None
    __hp = None
    __ac = None
    __spd = None
    __str = None
    __dex = None
    __con = None
    __int = None
    __wis = None
    __cha = None

    def __init__(self, hp):
        self.__hp = hp

    # Gets for all the stats
    def getLvl(self):
        return self.__lvl
    def getHp(self):
        return self.__hp
    def getAc(self):
        return self.__ac
    def getSpd(self):
        return self.__spd
    def getStr(self):
        return self.__str
    def getDex(self):
        return self.__dex
    def getCon(self):
        return self.__con
    def getInt(self):
        return self.__int
    def getWis(self):
        return self.__wis
    def getCha(self):
        return self.__cha
    
    # Sets for all the stats as well
    def setLvl(self, a):
        self.__lvl = a
    def setHp(self, a):
        self.__hp = a
    def setAc(self, a):
        self.__ac = a
    def setSpd(self, a):
        self.__spd = a
    def setStr(self, a):
        self.__str = a
    def setDex(self, a):
        self.__dex = a
    def setCon(self, a):
        self.__con = a
    def setInt(self, a):
        self.__int = a
    def setWis(self, a):
        self.__wis = a
    def setCha(self, a):
        self.__cha = a
    
    # convert class data into dictionary and return
    def toDict(self):
        return {
            'level': self.__lvl,
            'health': self.__hp,
            'armor class': self.__ac,
            'speed': self.__spd,
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
    return [[sg.Menu([['Add/Remove', ['Inventory', 'Enemies', 'Locations']], ['Search', ['Search']], ['Character',['Equipment', 'Stats', 'Skills']],
                      ['Dice', ['Roller']], ['Settings', ['Edit Config']], ['Credits'], ['Quit']])]]

def createLayoutInv():
    return [[sg.Text('Add/Remove Item', font='_ 14')],
            [sg.Text('Name:'), sg.Input(k = '-Item Name-', do_not_clear=False, s=(15,1))],
            [sg.Text('Desc:'), sg.Input(k = '-Item Desc-', do_not_clear=False, s=(25,1))],
            [sg.Text('Count:'), sg.Input(k = '-Item Count-', do_not_clear=False, s=(5,1))],
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
            [sg.Text('# of Dice'), sg.Input(k ='-Dice Numbers-', do_not_clear=False, s=(10,1)),
             sg.Text('# of Sides'), sg.Input(k ='-Dice Sides-', do_not_clear=False, s=(10,1)), sg.Button('Roll')],
            [sg.Text('Number Rolled - ') ,sg.Text(s=(20,1), key = '-Output-')]]

def createLayoutSearch():
    return [[sg.Text('Search Database', font='_ 43', justification='center', expand_x=True)],
            [sg.Text('Name:'), sg.Input(k='-Search-', do_not_clear=False, s=(20, 1))],
            [sg.Output(s=(75,13))]]

# formats the button layout
def createLayoutButtons():
    return [[sg.Button('Enter')]]

def createLayoutInvButtons():
    return [[sg.Button('Enter'), sg.Button('Remove')],
            [sg.Text('- Enter: Type JUST name and count to add more of this item to inv.')],
            [sg.Text('- Remove: Type JUST name and count, # for that amount, 0 to set 0, or -1 to completely remove')]]

def createLayoutStats1():
    layout_1 = [[sg.Text('Level', s=(10,1), font='_ 14')],
                [sg.Text('HP', s=(10,1), font='_ 14')],
                [sg.Text('Armor Class', s=(10,1), font='_ 14')],
                [sg.Text('Speed', s=(10,1), font='_ 14')],
                [sg.Text('Strength', s=(10,1), font='_ 14')],
                [sg.Text('Dexterity', s=(10,1), font='_ 14')],
                [sg.Text('Constitution', s=(10,1), font='_ 14')],
                [sg.Text('Intelligence', s=(10,1), font='_ 14')],
                [sg.Text('Wisdom', s=(10,1), font='_ 14')],
                [sg.Text('Charisma', s=(10,1), font='_ 14')]]
    
    layout_2 = [[sg.Text(key='-OutLvl-', s=(10,1), font='_ 14')],
                [sg.Text(key='-OutHP-', s=(10,1), font='_ 14')],
                [sg.Text(key='-OutAc-', s=(10,1), font='_ 14')],
                [sg.Text(key='-OutSpd-', s=(10,1), font='_ 14')],
                [sg.Text(key='-OutStr-', s=(10,1), font='_ 14')],
                [sg.Text(key='-OutDex-', s=(10,1), font='_ 14')],
                [sg.Text(key='-OutCon-', s=(10,1), font='_ 14')],
                [sg.Text(key='-OutInt-', s=(10,1), font='_ 14')],
                [sg.Text(key='-OutWis-', s=(10,1), font='_ 14')],
                [sg.Text(key='-OutCha-', s=(10,1), font='_ 14')]]
    
    layout_3 = [[sg.Button('+', k= '-+Lvl-'), sg.Button('-',k= '--Lvl-')],
                [sg.Button('+', k= '-+Hp-'), sg.Button('-',k= '--Hp-')],
                [sg.Button('+', k= '-+Ac-'), sg.Button('-',k= '--Ac-')],
                [sg.Button('+', k= '-+Spd-'), sg.Button('-',k= '--Spd-')],
                [sg.Button('+', k= '-+Str-'), sg.Button('-',k= '--Str-')],
                [sg.Button('+', k= '-+Dex-'), sg.Button('-',k= '--Dex-')],
                [sg.Button('+', k= '-+Con-'), sg.Button('-',k= '--Con-')],
                [sg.Button('+', k= '-+Int-'), sg.Button('-',k= '--Int-')],
                [sg.Button('+', k= '-+Wis-'), sg.Button('-',k= '--Wis-')],
                [sg.Button('+', k= '-+Cha-'), sg.Button('-',k= '--Cha-')]]
    
    return [[[sg.T('Stats', font='_ 16', justification='center', expand_x=True)]],
            [sg.Col(layout_1,p=0), sg.Col(layout_2,p=0), sg.Col(layout_3,p=0)]]

def createLayoutSkills():
    return [[sg.T('Skills', font='_ 14', justification='center', expand_x=True)]]

# return the created mainMenu window
def makeMainMenuWindow():
    sg.theme(THEME) # set color palette / theme of application
    layout_final = [[createLayoutMenu()],
                    [sg.Text('Welcome to Scribble!', font='_ 14', justification='c', expand_x=True)]]
    return sg.Window('Scribble', layout_final, size=(800, 400))

def makeInventoryWindow():
    layout_final = [[createLayoutMenu()],
                    [createLayoutInv()],
                    [createLayoutInvButtons()]]
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

def makeStatsWindow():
    layout_final = [[createLayoutMenu()],
                    [createLayoutStats1()]]
    return sg.Window('Scribble', layout_final, size=(800,400))

def makeSkillsWindow():
    layout_final = [[createLayoutMenu()],
                    [createLayoutSkills()]]
    return sg.Window('Scribble', layout_final, size=(800,400))

def search(find):
    currentDirectory = os.getcwd() # the current directory the script is located in
    jsonFiles = glob.glob(os.path.join(currentDirectory, '*.json')) # create list of all .json files in current directory
    jsonNames = [os.path.basename(file) for file in jsonFiles] # create list of all .json file names

    for jsonFile in jsonNames:
        data = loadJsonFile(jsonFile)
        for item in data:
            if item['name'].lower() == find.lower():
                return data
    print('Search could not find item, does not exist?')
    return []

def invMenuAddLogic(values):
    item = Item(values)  # Create item object
    existingItems = search(item.getName())  # Search if item is pre-existing in database
    existingItem = None  # Single item we are looking to edit

    # Get the single item we are looking for in 'existingItems'
    for x in existingItems:
        if x['name'] == item.getName():
            existingItem = x
            break

    if existingItem:
        # If item already exists in the inventory, update its count
        oldItemCount = int(existingItem['count'])
        newCount = item.getCount()
        existingItem['count'] = str(oldItemCount + newCount)  # Increase count by new count
        saveToJson(existingItems, INVENTORY_JSON)
    else:
        # If item is not found in the inventory, add it
        if item.allFieldsFilled():
            existingItems = loadJsonFile(INVENTORY_JSON)
            existingItems.append(item.toDict())
            saveToJson(existingItems, INVENTORY_JSON)
            print("Successfully added item to inventory")
        else:
            print("You are missing fields in item")

def invMenuRemoveLogic(values):
    inputValue = values['-Item Name-'].strip()  # Get the name of the item to remove (trimmed)
    count = int(values['-Item Count-'])  # Get the count of the item to remove
    data = loadJsonFile(INVENTORY_JSON)  # Load inventory data from JSON
    removed = False  # Flag to track if any item was removed

    # Iterate over the list of items and remove the matching item based on name and count
    for item in data:
        if item['name'].strip().lower() == inputValue.lower():
            itemCount = int(item['count'])
            if count < 0:
                # Complete removal from database if count is negative and item is not a key
                if item['key'] == 'Key':
                    print('Item is a key and cannot be removed completely.')
                else:
                    data.remove(item)
                    removed = True
            elif count > 0: # Decrease the count of the item by the specified amount
                newCount = max(0, itemCount - count)
                item['count'] = newCount
                if newCount == 0:
                    data.remove(item)
                    removed = True
                else:
                    print(f'Successfully removed {count} of that item.')
            else: # set equal to 0
                newCount = 0
                item['count'] = newCount
                removed = True

    if removed:
        print('Successfully removed item(s).')
    else:
        print('No matching item found or count is invalid.')

    # Save the updated inventory data to the JSON file
    saveToJson(data, INVENTORY_JSON)

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
    if(str(values['-Dice Sides-']).isnumeric() == False or str(values['-Dice Numbers-']).isnumeric() == False):
        print("Please enter Numbers.")
        window['-Output-'].update(" ")
    else:
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

def addStatsMenuLogic(values):
    if loadJsonFile(STATS_JSON) == FileNotFoundError:

        stats = loadJsonFile(STATS_JSON)

def subStatsMenuLogic(values):
    stats = loadJsonFile(STATS_JSON)


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
        
        if event == 'Stats':
            window.close()
            window = makeStatsWindow()
            CURRENT_WINDOW = 'Stats'

        if event == 'Skills':
            window.close()
            window = makeSkillsWindow()
            CURRENT_WINDOW = 'Skills'

        # logic for each window: Inventory, Enemies
        if event == 'Enter' and CURRENT_WINDOW == 'Inventory':
            invMenuAddLogic(values)
        elif event == 'Enter' and CURRENT_WINDOW == 'Enemies':
            enemiesMenuLogic(values)
        elif event == 'Roll' and CURRENT_WINDOW == 'Roller':
            diceMenuLogic(window, values)
        elif event == 'Enter' and CURRENT_WINDOW == 'Search':
            searchMenuInventoryLogic(values)
        elif event == 'Remove':
            invMenuRemoveLogic(values)
        
        # Insane event list for skills logic (Talk to Regan about a better solution to this)
        if event == '-+Lvl-':
            addStatsMenuLogic('-OutLvl-')
        elif event == '--Lvl-':
            subStatsMenuLogic('-OutLvl-')
        if event == '-+Hp-':
            addStatsMenuLogic('-OutHp-')
        elif event == '--Hp-':
            subStatsMenuLogic('-OutHp-')
        elif event == '-+Ac-':
            addStatsMenuLogic('-OutAc-')
        elif event == '--AC-':
            subStatsMenuLogic('-OutAc-')
        elif event == '-+Spd-':
            addStatsMenuLogic('-OutSpd-')
        elif event == '--Spd-':
            subStatsMenuLogic('-OutSpd-')
        elif event == '-+Str-':
            addStatsMenuLogic('-OutStr-')
        elif event == '--Str-':
            subStatsMenuLogic('-OutStr-')
        elif event == '-+Dex-':
            addStatsMenuLogic('-OutDex-')
        elif event == '--Dex-':
            subStatsMenuLogic('-OutDex-')
        elif event == '-+Con-':
            addStatsMenuLogic('-OutCon-')
        elif event == '--Con-':
            subStatsMenuLogic('-OutCon-')
        elif event == '-+Int-':
            addStatsMenuLogic('-OutInt-')
        elif event == '--Int-':
            subStatsMenuLogic('-OutInt-')
        elif event == '-+Wis-':
            addStatsMenuLogic('-OutWis-')
        elif event == '--Wis-':
            subStatsMenuLogic('-OutWis-')
        elif event == '-+Cha-':
            addStatsMenuLogic('-OutCha-')
        elif event == '--Cha-':
            subStatsMenuLogic('-OutCha-')



window = makeMainMenuWindow() # create the first initial window
runApplication(window) # start running program logic
window.close() # when the while loop in `runApplication` is broken, close the application

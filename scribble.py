import PySimpleGUI as sg # library needed for graphical elements, website: https://www.pysimplegui.org/en/latest/
import json # library needed for .json parsing and manipulation

'''
Create the 'window'
the window is the physical box containing the program. The layout is the 'elements' inside said window.
'''
def make_window():
    # create a 'list' containing elements, the list is later added to the window
    layout = [  [sg.Text('some text')],
                [sg.Button('a button')],
                [sg.InputText('write something here')]  ]

    # create a window and add list of elements to window as a parameter in it's constructor
    return sg.Window('Example Window', layout)

# create window using make_window() function
window = make_window()

'''
needed for closing program properly
runs indefinite 'action listener' that captures actions. Like clicking buttons, typing, etc.
actions that are made are set equal to the 'event' and 'values' variable.

if 'event' is clicking the X close button, while loop breaks and ends program
'''
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

window.close()

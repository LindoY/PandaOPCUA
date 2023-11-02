import sys
import time
from gpiozero import Button
from opcua import Client, ua
from opcua.common.type_dictionary_buider import get_ua_class
from signal import pause

taskName = sys.argv[1] if len(sys.argv) > 1 else "0_mahle"

print("Programm: " + taskName + " wird ausgeführt.")

# Configure and connect the client
client = Client("opc.tcp://192.168.0.1:4840/", timeout=30) # 4840 is the default
client.set_user("Franka_Emika")
client.set_password("Franka_Emika")
client.connect() # Connect our client to the robot
typedefs = client.load_type_definitions() # Load custom type definitions
print("OPCUA Client connected")

# Browse the server for relevant nodes
root = client.get_root_node()
robot = root.get_child("0:Objects").get_child("2:Robot")
executionControl = robot.get_child("2:ExecutionControl")
executionStatus = executionControl.get_child ("2:ExecutionStatus")
controlTokenActive = executionControl.get_child("2:ControlTokenActive")
brakesOpen = executionControl.get_child("2:BrakesOpen")
requestControlToken = executionControl.get_child("2:RequestControlToken")
openBrakes = executionControl.get_child("2:OpenBrakes")
#switchToExecution = executionControl.get_child("2:SwitchToExecution") # only for FX3
freeControlToken = executionControl.get_child("2:FreeControlToken")
startTask = executionControl.get_child("2:StartTask")
stopTask = executionControl.get_child("2:StopTask")
keyIntMapObject = robot.get_child("2:KeyValueMaps").get_child("2:KeyIntMap")
setKeyIntMethod = keyIntMapObject.get_child("2:Replace")
getKeyIntMapMethod = keyIntMapObject.get_child("2:ReadMap")

abl11 = get_ua_class("KeyIntPair")()
abl11.Key = "abl11"
abl11.Value = 1
abl12 = get_ua_class("KeyIntPair")()
abl12.Key = "abl12"
abl12.Value = 1
abl21 = get_ua_class("KeyIntPair")()
abl21.Key = "abl21"
abl21.Value = 1
abl22 = get_ua_class("KeyIntPair")()
abl22.Key = "abl22"
abl22.Value = 1

if len(keyIntMapObject.call_method(getKeyIntMapMethod)) < 5:
    keyIntMapObject.call_method(setKeyIntMethod, abl12)
    print("Alle Ablagezaehler wurden zurückgesetzt")

try:
    key_value_pairs = keyIntMapObject.call_method(getKeyIntMapMethod)
    for item in key_value_pairs:
        print(item)
except Exception as e:
    print("Fehler beim Abrufen der Key-Value-Paare: " + e)


def stopp():
    if executionStatus.get_value().IsRunning:
        print("Stopping the current task")
        executionControl.call_method(stopTask)
        executionControl.call_method(freeControlToken)
        time.sleep(1)
    else:
        print("No task is currently running")
def start():
    # Request SPOC token
    executionControl.call_method(requestControlToken, False)
    while not controlTokenActive.get_value():
        print("Waiting for SPOC Control Token")
        time.sleep(1)
    else:
        print("SPOC Control Token aquired")

    # Open brake
    if not brakesOpen.get_value():
        executionControl.call_method(openBrakes)
        print("Brakes opened")
    else:
        print("Brakes already open")
    time.sleep(1)

    #Switch to Execution mode (only for FX3)
    #executionControl.call_method(switchToExecution)
    #print("Execution mode")
    #time.sleep(2)

    # Start selected Task
    executionControl.call_method(startTask, taskName)  # give Task name here
    time.sleep(1)

    # Monitor execution
    print("The task is running")
    while executionStatus.get_value().IsRunning and not executionStatus.get_value().HasError:
        if button_stopp.is_pressed:
            stopp()  # Task stoppen, wenn der Stopp-Button gedrückt wurde
            break
        time.sleep(0.2)
    else:
        print("The task has stopped")
        time.sleep(1)

    if executionStatus.get_value().HasError:
        print("Error message: " + executionStatus.get_value().ErrorMessage)
        executionControl.call_method(stopTask)
        executionControl.call_method(freeControlToken)
        time.sleep(1)
    else:
        print("Success")
        time.sleep(1)

button_start = Button(18)
button_stopp = Button(17)

button_start.when_released = start
button_stopp.when_released = stopp

pause()
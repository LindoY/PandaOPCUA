import time
from opcua import Client, ua
from opcua.common.type_dictionary_buider import get_ua_class

time.sleep(5)

# Configure and connect the client
client = Client("opc.tcp://192.168.0.1:4840/", timeout=60) # 4840 is the default
client.set_user("Franka_Emika")
client.set_password("Franka_Emika")
client.connect() # Connect our client to the robot
typedefs = client.load_type_definitions() # Load custom type definitions
print ("OPCUA Client connected")

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
startTask = executionControl.get_child("2:StartTask")

# Request SPOC token
executionControl.call_method(requestControlToken, False)
while not controlTokenActive.get_value():
    print ("Waiting for SPOC Control Token")
    time.sleep(1)
else:
    print ("SPOC Control Token aquired")

# Open brakes
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
executionControl.call_method(startTask, "test2") # give Task name here
time.sleep(1)

# Monitor execution
while executionStatus.get_value().IsRunning and not executionStatus.get_value().HasError:
    print("The task is running")
    time.sleep(1)
else:
    print("The task has stopped")
    time.sleep(1)

if executionStatus.get_value().HasError:
    print("Error message: " + executionStatus.get_value().ErrorMessage)
    time.sleep(1)
else:
    print("Success")
    time.sleep(1)


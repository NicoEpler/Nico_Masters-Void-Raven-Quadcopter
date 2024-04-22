From [ROS2 Tutorial video](https://www.youtube.com/watch?v=Gg25GfA456o&list=PLLSegLrePWgJk6dfV-UXSh2TZ74wNntWt&index=1)


1. To see a graph of all running topics and nodes:
```Shell
rqt_graph
```


2. To enable colcon (For building nodes) autocomplete (TAb can be used for CLI autocomplete):
	1. Do and add the "source" line to the bottom of the bashrc file and save::
```Shell
gedit ~/.bashrc
```

```Shell
source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash
```


3. To create ROS2 Workspace:

```Shell
cd
mkdir ros2_ws
```
	1. cd and create workspace folder: 

```Shell
cd ros2_ws
mkdir src
```
	2. Inside of workspace folder, create src folder (src will contain the ros2 nodes we create):

```Shell
source ~/ros2_ws/install/setup.bash
```
	3. When using "colcon build", 3 new folders will be created. Insider the created install file, a setup.bash file is created, which has to be sourced before the custom ros2 nodes can be used. Therefore add the following line to your bashrc file aswell and save:

```Shell
cd
cd ros2_ws/src
ros2 pkg create NAME_Change_this --build-type ament_python --dependencies rclpy
```
	4. Create a package inside the src folder. Nodews are written in packages, which allow us to better organize code and the dependencies between packages. To crteate package, do (python package)(for c++ package use "ament_cmake"):
	Dependencies are all packages and functionalities that the package uses. rclpy is ros2 python library

```Shell
cd
cd ros2_ws
colcon build
```
	5. build your workspace:
	If everything works, good. If you get error, check 37:00 in the following video and rebuild
[following video](https://www.youtube.com/watch?v=Gg25GfA456o&list=PLLSegLrePWgJk6dfV-UXSh2TZ74wNntWt&index=1)


4.  To write an actual Node (The actual programs):

```Shel
cd
cd ros2_ws/src/NAME_Change_this/NAME_Change_this
touch my_first_node.py
chmod +x my_first_node.py
```
	1. Create node file and make it executable (after this, "ls" and confirm that "my_first_node.py" is green):

```Shell
cd 
cd ros2_ws/src
code .
```
	2. Open VSCode in source folder and open "src/NAME_Change_this/NAME_Change_this/my_first_node.py"
	3. Add following extensions in VSCode to make python coding easier:
			1. ROS (Microsoft verified)

```Python
#!/usr/bin/env python3     # Tells interpreter to use python3
import rclpy               # Python library for ROS2
from rclpy.node import Node


class MyNode(Node):         # Define a class MyNode that inherits from the node that is from rclpy.node. Class therefore has access to all functionalities of ROS2
	def __init__(self):
		super().__init__("first_node") # Define node name
		self.get_logger().info("Hello from ROS2") # Writing a log from ROS2


def main (args=None):      # Create main function
	rclpy.init(args=args)  # Initialize ROS2 communications and features. Arguments for init function are same as argusments from the main
	# Create
	# Node
	# Here
	# Node is created inside the file/program. Therefore, multiple nodes can be run from the same program.
	# Use object orientated programming. Therefore Create Node outside main and call it
	node = MyNode()
	rclpy.spin(node)        # Keeps node alive/running indefinitey, until ctrl+c
	rclpy.shotdown()        # Last Line, shutting down ROS2 communications

if __name__ == '__main__':
	main()
```
	4. Start editing the node and add the following lines:

```Shell
cd
cd ros2_ws/src/NAME_Change_this/NAME_Change_this
./ my_first_node.py
```
	5. To test node:

```Python
entry_points={
	'console_scripts': [
		"test_node = NAME_Change_this.my_first_node:main"     # 'test_node' is executable name
	],
},
```
	6. Install the node, such that it can be run with ros2 run. In VSCode go to ros2_ws/src/NAME_Change_this/setup.py and add following to entry_points

```Shell
cd
cd ros2_ws
colcon build
source ~/.bashrc
ros2 run NAME_Change_this test_node
```
	7. Colcon build your ros2_ws and source yourk workspace. Then run the node (Pay attention to node naming). However, executable name, file name and node name can also be same.

```Shell
cd
cd ros2_ws
colcon build ---symlink-install
source ~/.bashrc
```
	8. To prevent having to rebuild every time you change something in the node file, do (If errors do occur afterwards, just source the bashrc):

```Shell
ros2 node list
```
	9. See your ROS2 nodes using:

```Python
class MyNode(Node):
	def __init__(self):
		super().__init__("first_node") # Define node name
		self.counter_ =0
		self.create_timer(1.0, self.timer_callback)

	def timer_callback(self):
		self.get_logger().info("Hello " = str(self.counter_))
		self.counter_ += 1
```
	10. Add a timer and callback, to rerun code numerous times by editing the following in the my_first_node.py file:


5. Topics (Communication between nodes):




1:02:00
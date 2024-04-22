
4.  To write an actual Node:
	1. Create node file and make it executable (after this, "ls" and confirm that "my_first_node.py" is green):

```Bas
acdasdca
```




```Shell
cd
cd ros2_ws/src/NAME_Change_this/NAME_Change_this
touch my_first_node.py
chmod +x my_first_node.py
```
 

	2. Open VSCode in source folder and open 'src/NAME_Change_this/NAME_Change_this/my_first_node.py'


```Shell
cd 
cd ros2_ws/src
code .
```
	3. Add following extensions in VSCode to make python coding easier:
			1. ROS (Microsoft verified)

	4. Start editing the node and add the following lines:

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

	7. To test node:
```Shell
cd
cd ros2_ws/src/NAME_Change_this/NAME_Change_this
./ my_first_node.py
```

	8. Install the node, such that it can be run with ros2 run. In VSCode go to ros2_ws/src/NAME_Change_this/setup.py and add following to entry_points
```Python
entry_points={
	'console_scripts': [
		"test_node = NAME_Change_this.my_first_node:main"     # 'test_node' is executable name
	],
},
```

	9. Colcon build your ros2_ws and source yourk workspace. Then run the node (Pay attention to node naming). However, executable name, file name and node name can also be same.
```Shell
cd
cd ros2_ws
colcon build
source ~/.bashrc
ros2 run NAME_Change_this test_node
```

	10. To prevent having to rebuild every time you change something in the node file, do (If errors do occur afterwards, just source the bashrc):
```Shell
cd
cd ros2_ws
colcon build ---symlink-install
source ~/.bashrc
```

	11. See your ROS2 nodes using:
```Shell
ros2 node list
```

	12. Add a timer and callback, to rerun code numerous times by editing the following in the my_first_node.py file:

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





36:30

# From [ROS2 Tutorial video](https://www.youtube.com/watch?v=Gg25GfA456o&list=PLLSegLrePWgJk6dfV-UXSh2TZ74wNntWt&index=1)


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
	4. Create a package inside the src folder. Nodes are written in packages, which allow us to better organize code and the dependencies between packages. To crteate package, do (python package)(for c++ package use "ament_cmake"):
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
	8. To prevent having to rebuild every time you change something in the node file, do (If errors do occur afterwards, just source the bashrc). NOTE: You still have to colcon build whenever you add a nef file/executable.

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

```Shell
ros2 topic list
```
	1. See your ROS2 topics using:

```
ros2 topic info /chatter
```
	2. Get more info on the chatter topic

```Shell
ros2 topic echo /chatter
```
	3. To listen in to what the /chatter node is publishing

```Python
from geometry_msgs.msg import Twist     # Twist is the message type. This one is specific for controlling the turtble bot and was found using 'ros2 topic info /turtle1/cmd_vel' command  in CLI

class DrawCircleNode(Node):

	def __init__(self):
		super().__init__("draw_circle")
		self.cmd_vel_pub_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)     # command velocity publisher, publishing a Twist type message with the name '/turtle1/cmd_vel' found from 'ros2 topic list' in CLI. 10 is queue size/buffer(10 messages)
		self.get_logger().info("Draw circle node has been started")
```
	4. Creating a publisher node: Create node("draw_circle"), initialize and add main fucntion then add the above class and initializations

```Python
<depend>rclpy</depend>
<depend>geometry_msgs</depend>
<depend>turtlesim</depend>
```
	5.As you now use the geometry_msgs package aswell, you have to include this in the package.xml file. Include all other pacakge dependencies here. e.g. turtlesim



# Other Interesting Tutorials:

1. ROS2 Gazebo tutorias from "The Construct" explains everything abouth Creating and launching SDF and URDF models in Gazebo and how to visualize them in RVIS [here](https://www.youtube.com/watch?v=qi2A32WgRqI&list=PLK0b4e05LnzbHiGDGTgE_FIWpOCvndtYx&index=1) 
2. Very explanatory tutorial on robot_state_publisher and joint_state_publisher from "The Construct" ins [here](https://www.youtube.com/watch?v=9BdAkrX4Xkg) 37:00


# Setup ROS2 Workspace, Create package, Add Node, build packages, Running Nodes:

### Step 1: Set Up Your ROS 2 Workspace

If you haven't already set up a ROS 2 workspace, do so first. This workspace will house your node and its packages.
1. **Create a workspace directory (if not already existing):**
```bash
mkdir -p ~/ros2_ws/src
```
   This creates a folder named `ros2_ws` with a `src` subfolder for source code.
2. **Navigate to the workspace:**

```bash
cd ~/ros2_ws
```
1. **Initialize the workspace:**
```bash
colcon build
```
### Step 2: Create a Package
Now you'll create a ROS 2 package to contain your node.
1. **Navigate to the `src` folder:**
```bash
cd ~/ros2_ws/src
```
1. **Create a new ROS 2 package (replace `imu_position_pkg` with your preferred package name):**
```bash
ros2 pkg create imu_position_pkg --build-type ament_python --dependencies rclpy sensor_msgs geometry_msgs
```
   This command sets up a Python-based package with dependencies on `rclpy`, `sensor_msgs`, and `geometry_msgs`.
3. **Navigate to your package directory:**
```bash
cd imu_position_pkg
```
  
### Step 3: Add the Node Code
Add the provided Python code to your package.
1. **Create a `scripts` directory to store your node script:**
```bash
mkdir scripts
```
1. **Create the node script (e.g., `imu_position_node.py`):**
```bash
touch scripts/imu_position_node.py
```
1. **Open the script file in a text editor (e.g., `nano`):**
```bash
nano scripts/imu_position_node.py
```
   - Paste the provided code into this file.
   - Save and exit the editor (`CTRL+X`, then `Y`, then `Enter` for `nano`).
4. **Make the script executable:**
```bash
chmod +x scripts/imu_position_node.py
```
  

### Step 4: Update `setup.py`
Modify `setup.py` to include your node script.
1. Go to directory:
```bash
cd ~/ros2_ws/src/imu_position_pkg
```
3. **Open `setup.py` in an editor:**
```bash
nano setup.py
```
1. **Add the entry point for the node.** Update `setup.py` to look something like this:
```python
from setuptools import setup

package_name = 'imu_position_pkg'

setup(
	name=package_name,
	version='0.0.0',
	packages=[package_name],
	py_modules=[
		'scripts.imu_position_node'
	],
	install_requires=['setuptools'],
	zip_safe=True,
	maintainer='your_name',
	maintainer_email='your_email@example.com',
	description='IMU Position Node',
	license='Your License Here',
	tests_require=['pytest'],
	entry_points={
		'console_scripts': [
			'imu_position_node = scripts.imu_position_node:main'
		],
	},
)
```
   - Make sure `scripts.imu_position_node:main` matches the path to your script and its main function.
   - Save and exit the editor.

### Step 5: Build the Package
You need to build your package so ROS 2 can recognize it.
1. **Navigate to the root of your workspace:**
```bash
cd ~/ros2_ws
```
1. **Build the workspace:**
```bash
colcon build
```
1. **Source the workspace setup file to use your new package:**
```bash
source install/setup.bash
```
   Add the following command to your `source ~/.bashrc` file to source the workspace automatically each time you open a terminal:
```bash
source ~/ros2_ws/install/setup.bash
```
### Step 6: Run the Node
Now you can run your node!
1. **Run your node using `ros2 run`:**
```bash
ros2 run imu_position_pkg imu_position_node
```
   This command runs the `imu_position_node` from the `imu_position_pkg` package.

### Step 7: Monitor the Output
To verify that your node is working:
- **Check the logs**: The node will log position updates (in debug mode).
- **View the `/imu/calc/position` topic**: You can use `ros2 topic echo` to see the messages published to this topic:
```bash
ros2 topic echo /imu/calc/position --once
```
"--once" makes sure only a single instance is echoed



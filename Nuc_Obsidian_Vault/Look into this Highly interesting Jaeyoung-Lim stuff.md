

1. [Obstacle Detection and Avoidance](https://github.com/PX4/PX4-Avoidance):
	PX4 computer vision algorithms packaged as ROS nodes for depth sensor fusion and obstacle avoidance. This repository contains three different implementations:
	- _local_planner_ is a local VFH+* based planner that plans (including some history) in a vector field histogram
	- _global_planner_ is a global, graph based planner that plans in a traditional octomap occupancy grid
	- _safe_landing_planner_ is a local planner to find safe area to land

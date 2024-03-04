#!/bin/bash

get_robot_attr() {
	python3 -c "import sys, yaml; print(yaml.load(open(\"configs/multibot_env.yaml\"), yaml.FullLoader)[\"$1\"][\"$2\"])"
}
launch_robot.py robot_client=franka_hardware robot_client.executable_cfg.robot_ip=$(get_robot_attr $1 robot_ip) port=$(get_robot_attr $1 robot_port)
if [ $? -eq 0 ]; then
    echo "Command was successful"
else
    hash_line="##################################################################################"
    echo -e "\e[1;31m$hash_line\e[0m"
    echo "Command failed with exit code $?"
    echo "Make sure Panda 1 is in FCI mode and make sure no other server is by running:"
    echo "sudo pkill -9 run_server"
    echo -e "\e[1;31m$hash_line\e[0m"
fi
FROM ros:jazzy
RUN apt-get update && apt-get install -y \
    python3-pip \
    ros-jazzy-cv-bridge \
    python3-opencv \
    vim \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install colcon-common-extensions numpy opencv-python --break-system-packages
RUN mkdir -p /home/ros_ws/src
WORKDIR /home/ros_ws
RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && catkin init"
CMD ["/bin/bash"]
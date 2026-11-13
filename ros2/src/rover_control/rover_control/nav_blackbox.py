"""Navigation placeholder adapter: manually supplied Twist to /cmd_vel_nav.
Does not implement Nav2 planning, localization or action dispatch.
"""
from rclpy.node import Node
from geometry_msgs.msg import Twist
from .common import run
class NavBlackbox(Node):
    def __init__(self):
        super().__init__('nav_blackbox')
        self.pub=self.create_publisher(Twist,'/cmd_vel_nav',10)
        self.create_subscription(Twist,'/nav2_cmd_vel_sim',self.pub.publish,10)
def main(): run(NavBlackbox)

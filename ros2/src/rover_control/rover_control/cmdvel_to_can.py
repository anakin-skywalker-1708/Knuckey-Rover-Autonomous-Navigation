"""Dry-run wheel speed / CAN INTENT publisher. No CAN frames are transmitted.
CAN IDs, byte layout, gear ratio and axis mapping require original firmware verification.
"""
import json, math
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from .common import run
class CmdVelToCan(Node):
    def __init__(self):
        super().__init__('cmdvel_to_can')
        self.declare_parameter('wheel_radius_m',0.15)
        self.declare_parameter('track_width_m',0.6)
        self.declare_parameter('max_wheel_turns_per_sec',2.0)
        self.declare_parameter('stale_timeout_sec',0.25)
        self.cmd=Twist();self.last=None
        self.pub=self.create_publisher(String,'/odrive_can_intent_sim',10)
        self.create_subscription(Twist,'/cmd_vel',self.receive,10)
        self.create_timer(0.05,self.tick)
    def receive(self,m): self.cmd=m; self.last=self.get_clock().now()
    def tick(self):
        fresh=self.last is not None and (self.get_clock().now()-self.last).nanoseconds/1e9 <= self.get_parameter('stale_timeout_sec').value
        v=self.cmd.linear.x if fresh else 0.0; w=self.cmd.angular.z if fresh else 0.0
        radius=max(0.001,self.get_parameter('wheel_radius_m').value);track=self.get_parameter('track_width_m').value
        limit=self.get_parameter('max_wheel_turns_per_sec').value
        left=max(-limit,min(limit,(v-w*track/2)/(2*math.pi*radius)))
        right=max(-limit,min(limit,(v+w*track/2)/(2*math.pi*radius)))
        self.pub.publish(String(data=json.dumps({'left_turns_per_sec':left,'right_turns_per_sec':right,'fresh':fresh,'dry_run':True})))
def main(): run(CmdVelToCan)

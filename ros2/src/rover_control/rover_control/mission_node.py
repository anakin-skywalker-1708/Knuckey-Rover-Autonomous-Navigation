"""Mission waypoint storage/status mock. Nav2 action interface is NOT implemented."""
import json
from rclpy.node import Node
from std_msgs.msg import String,Float32
from .common import run
class MissionNode(Node):
    def __init__(self):
        super().__init__('mission_node')
        self.path=[];self.battery=None;self.bus=None
        self.pub=self.create_publisher(String,'/status',10)
        self.goal=self.create_publisher(String,'/next_waypoint_sim',10)
        self.create_subscription(String,'/path_plan',self.set_path,10)
        self.create_subscription(Float32,'/main_battery_voltage',lambda m:setattr(self,'battery',m.data),10)
        self.create_subscription(Float32,'/bus_voltage',lambda m:setattr(self,'bus',m.data),10)
        self.create_timer(0.5,self.tick)
    def set_path(self,m):
        try:
            x=json.loads(m.data)
            if isinstance(x,list):self.path=x
        except ValueError:pass
    def tick(self):
        self.pub.publish(String(data=json.dumps({'remaining_waypoints':len(self.path),'main_battery_voltage':self.battery,'bus_voltage':self.bus,'simulation_only':True})))
        if self.path:self.goal.publish(String(data=json.dumps(self.path[0])))
def main(): run(MissionNode)

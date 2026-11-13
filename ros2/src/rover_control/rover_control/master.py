"""Manual base-station command assembler, simulation only; no Excel parsing."""
import json
from rclpy.node import Node
from std_msgs.msg import String, Bool
from geometry_msgs.msg import Twist
from .common import run
class Master(Node):
    def __init__(self):
        super().__init__('master')
        self.mode='manual';self.arm=False;self.go=False;self.clear_pending=False
        self.tele=Twist();self.path=None
        self.pub=self.create_publisher(String,'/base_command_json',10)
        self.create_subscription(String,'/base_mode',lambda m:setattr(self,'mode',m.data),10)
        self.create_subscription(Bool,'/base_arm',lambda m:setattr(self,'arm',m.data),10)
        self.create_subscription(Bool,'/base_estop_go',lambda m:setattr(self,'go',m.data),10)
        self.create_subscription(Bool,'/base_clear_estop',self.clear,10)
        self.create_subscription(Twist,'/base_cmd_vel_tele',lambda m:setattr(self,'tele',m),10)
        self.create_subscription(String,'/base_path_plan',lambda m:setattr(self,'path',m.data),10)
        self.create_timer(0.1,self.tick)
    def clear(self,m):
        if m.data:self.clear_pending=True
    def tick(self):
        d={'kind':'command','mode':self.mode,'armed':self.arm,'e_stop_go':self.go,
           'linear_x':self.tele.linear.x,'angular_z':self.tele.angular.z,'clear_estop':self.clear_pending}
        if self.path is not None:
            try:d['path_plan']=json.loads(self.path)
            except ValueError:pass
            self.path=None
        self.pub.publish(String(data=json.dumps(d)));self.clear_pending=False

def main(): run(Master)

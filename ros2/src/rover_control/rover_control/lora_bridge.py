"""Rover-side logical LoRa bridge, using ROS JSON messages, NOT an RF driver."""
import json
from rclpy.node import Node
from std_msgs.msg import String, Bool
from geometry_msgs.msg import Twist
from .common import run, decode
class LoRaBridge(Node):
    def __init__(self):
        super().__init__('lora_bridge')
        self.declare_parameter('link_timeout_sec',0.5)
        self.last=None; self.connected=False
        self.armed=self.create_publisher(Bool,'/armed',10)
        self.estop=self.create_publisher(Bool,'/e-stop',10)
        self.clear=self.create_publisher(Bool,'/clear_estop',10)
        self.mode=self.create_publisher(String,'/command_mode',10)
        self.path=self.create_publisher(String,'/path_plan',10)
        self.tele=self.create_publisher(Twist,'/cmd_vel_tele',10)
        self.link=self.create_publisher(Bool,'/lora_link_alive_sim',10)
        self.out=self.create_publisher(String,'/lora_tx_sim',10)
        self.create_subscription(String,'/lora_rx_sim',self.receive,10)
        self.create_subscription(String,'/status',self.send_status,10)
        self.create_timer(0.1,self.tick)
    def receive(self,m):
        d=decode(m.data)
        if d.get('kind')!='command':return
        self.last=self.get_clock().now();self.connected=True
        if 'e_stop_go' in d: self.estop.publish(Bool(data=bool(d['e_stop_go'])))
        if 'armed' in d: self.armed.publish(Bool(data=bool(d['armed'])))
        if d.get('clear_estop') is True: self.clear.publish(Bool(data=True))
        if d.get('mode') in ('manual','autonomous'):self.mode.publish(String(data=d['mode']))
        if 'path_plan' in d:self.path.publish(String(data=json.dumps(d['path_plan'])))
        if 'linear_x' in d or 'angular_z' in d:
            t=Twist();t.linear.x=float(d.get('linear_x',0));t.angular.z=float(d.get('angular_z',0));self.tele.publish(t)
    def send_status(self,m): self.out.publish(String(data=json.dumps({'kind':'status','payload':decode(m.data)})))
    def tick(self):
        fresh=self.last is not None and (self.get_clock().now()-self.last).nanoseconds/1e9 <= self.get_parameter('link_timeout_sec').value
        self.link.publish(Bool(data=fresh))
        if not fresh:
            self.estop.publish(Bool(data=False));self.armed.publish(Bool(data=False));self.tele.publish(Twist())
            self.connected=False

def main(): run(LoRaBridge)

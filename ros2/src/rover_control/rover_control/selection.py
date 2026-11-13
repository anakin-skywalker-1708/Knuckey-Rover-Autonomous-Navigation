"""Mode selection; stale commands result in zero Twist, never a held last command."""
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from .common import run
class Selection(Node):
    def __init__(self):
        super().__init__('selection')
        self.declare_parameter('command_timeout_sec', 0.3)
        self.mode='e-stop'; self.tele=None; self.nav=None; self.tele_at=None; self.nav_at=None
        self.pub=self.create_publisher(Twist,'/cmd_vel',10)
        self.create_subscription(String,'/active_mode',self.set_mode,10)
        self.create_subscription(Twist,'/cmd_vel_tele',self.set_tele,10)
        self.create_subscription(Twist,'/cmd_vel_nav',self.set_nav,10)
        self.create_timer(0.05,self.tick)
    def set_mode(self,m): self.mode=m.data
    def set_tele(self,m): self.tele=m; self.tele_at=self.get_clock().now()
    def set_nav(self,m): self.nav=m; self.nav_at=self.get_clock().now()
    def tick(self):
        m,t=(self.tele,self.tele_at) if self.mode=='manual' else ((self.nav,self.nav_at) if self.mode in ('auto','autonomous') else (None,None))
        fresh=t is not None and (self.get_clock().now()-t).nanoseconds/1e9 < self.get_parameter('command_timeout_sec').value
        self.pub.publish(m if fresh and m is not None else Twist())
def main(): run(Selection)

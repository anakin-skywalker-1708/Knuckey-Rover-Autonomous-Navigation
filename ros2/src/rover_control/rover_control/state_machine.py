"""Reconstruction: software state machine ONLY; no GPIO/contactor control.
Architecture: 40.8V min, 2V precharge delta, 2s timeout, fresh arm edge.
Not suitable for real power electronics or safety-critical operation.
"""
from rclpy.node import Node
from std_msgs.msg import Bool, Float32, String
from .common import run

class StateMachine(Node):
    def __init__(self):
        super().__init__('state_machine')
        self.declare_parameter('min_battery_voltage', 40.8)
        self.declare_parameter('precharge_delta', 2.0)
        self.declare_parameter('precharge_timeout', 2.0)
        self.mode = 'manual'; self.state = 'disarmed'; self.arm = False
        self.estop_go = False; self.estop_latched = True; self.fresh_disarm = False
        self.battery = None; self.bus = None; self.start_time = None
        self.pub = self.create_publisher(String, '/active_mode', 10)
        self.state_pub = self.create_publisher(String, '/power_state_sim', 10)
        self.create_subscription(String, '/command_mode', self.set_mode, 10)
        self.create_subscription(Bool, '/armed', self.set_arm, 10)
        self.create_subscription(Bool, '/e-stop', self.set_estop, 10)
        self.create_subscription(Bool, '/clear_estop', self.clear, 10)
        self.create_subscription(Float32, '/main_battery_voltage', self.set_battery, 10)
        self.create_subscription(Float32, '/bus_voltage', self.set_bus, 10)
        self.create_timer(0.1, self.tick)
    def set_mode(self,m):
        if m.data in ('manual','autonomous'): self.mode=m.data
    def set_arm(self,m):
        rising = m.data and not self.arm
        if not m.data:
            self.fresh_disarm=True
            if self.state != 'fault': self.state='disarmed'
        self.arm=m.data
        if rising and self.fresh_disarm and self.estop_go and not self.estop_latched and self.state=='disarmed':
            if self.battery is not None and self.battery >= self.get_parameter('min_battery_voltage').value:
                self.state='precharge'; self.start_time=self.get_clock().now(); self.fresh_disarm=False
    def set_estop(self,m):
        self.estop_go=m.data
        if not m.data: self.estop_latched=True; self.state='fault'; self.fresh_disarm=False
    def clear(self,m):
        if m.data and self.estop_go and not self.arm:
            self.estop_latched=False; self.state='disarmed'; self.fresh_disarm=True
    def set_battery(self,m): self.battery=m.data
    def set_bus(self,m): self.bus=m.data
    def tick(self):
        threshold=self.get_parameter('min_battery_voltage').value
        if self.state in ('precharge','armed') and (self.battery is None or self.battery < threshold):
            self.state='fault'; self.estop_latched=True
        if self.state=='precharge':
            elapsed=(self.get_clock().now()-self.start_time).nanoseconds/1e9
            if self.bus is not None and self.battery is not None and 0 <= self.battery-self.bus <= self.get_parameter('precharge_delta').value:
                self.state='armed'
            elif elapsed > self.get_parameter('precharge_timeout').value:
                self.state='fault'; self.estop_latched=True
        active = self.mode if self.state=='armed' and self.estop_go and not self.estop_latched else 'e-stop'
        self.pub.publish(String(data='auto' if active=='autonomous' else active))
        self.state_pub.publish(String(data=self.state))

def main(): run(StateMachine)

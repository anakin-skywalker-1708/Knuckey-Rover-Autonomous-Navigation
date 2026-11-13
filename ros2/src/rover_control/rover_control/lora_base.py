"""Mock base-station radio bridge; wire transport intentionally omitted."""
from rclpy.node import Node
from std_msgs.msg import String
from .common import run,decode
class LoRaBase(Node):
    def __init__(self):
        super().__init__('lora_base')
        self.tx=self.create_publisher(String,'/radio_out_sim',10)
        self.status=self.create_publisher(String,'/status',10)
        self.create_subscription(String,'/base_command_json',self.tx.publish,10)
        self.create_subscription(String,'/base_radio_in_sim',self.receive,10)
    def receive(self,m):
        d=decode(m.data)
        if d.get('kind')=='status': self.status.publish(String(data=__import__('json').dumps(d.get('payload',{}))))
def main(): run(LoRaBase)

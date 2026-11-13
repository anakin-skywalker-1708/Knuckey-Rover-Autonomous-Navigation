"""Mock RF ingress: relays /radio_in_sim JSON to /lora_rx_sim. No hardware radio."""
from rclpy.node import Node
from std_msgs.msg import String
from .common import run
class LoRaRx(Node):
    def __init__(self):
        super().__init__('lora_rx')
        self.pub=self.create_publisher(String,'/lora_rx_sim',10)
        self.create_subscription(String,'/radio_in_sim',self.pub.publish,10)
def main(): run(LoRaRx)

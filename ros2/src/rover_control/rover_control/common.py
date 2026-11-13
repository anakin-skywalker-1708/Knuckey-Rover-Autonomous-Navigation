import json
import rclpy

def run(node_type):
    rclpy.init()
    node = node_type()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

def decode(s):
    try:
        value = json.loads(s)
        return value if isinstance(value, dict) else {}
    except (TypeError, ValueError):
        return {}

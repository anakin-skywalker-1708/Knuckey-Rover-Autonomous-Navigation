from setuptools import setup
package_name = 'rover_control'
setup(name=package_name, version='0.1.0', packages=[package_name],
      data_files=[('share/ament_index/resource_index/packages', ['resource/' + package_name]),
                  ('share/' + package_name, ['package.xml'])],
      install_requires=['setuptools'], zip_safe=True, maintainer='Manas Desai',
      maintainer_email='manasmd1726@gmail.com', description='Simulation-only reconstructed rover nodes',
      license='UNLICENSED', entry_points={'console_scripts': [
        'state_machine = rover_control.state_machine:main',
        'selection = rover_control.selection:main',
        'cmdvel_to_can = rover_control.cmdvel_to_can:main',
        'lora_bridge = rover_control.lora_bridge:main',
        'lora_rx = rover_control.lora_rx:main',
        'lora_base = rover_control.lora_base:main',
        'master = rover_control.master:main',
        'mission_node = rover_control.mission_node:main',
        'nav_blackbox = rover_control.nav_blackbox:main',
      ]})

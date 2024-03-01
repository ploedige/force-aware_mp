import hydra
import logging

from torchcontrol.policies import HybridJointImpedanceControl
from polymetis import RobotInterface

from controllers.human_controller import HumanController

class TeleoperationHandler:
    def __init__(self, 
                 demonstrator: RobotInterface,
                 imitator: RobotInterface):
        self.logger = logging.getLogger('teleoperation_handler')
        self.demonstrator = demonstrator
        self.imitator = imitator
        self.sync_robot_positions()

    def sync_robot_positions(self):
        """Sync the robot positions by moving the imitator to the current position of the demonstrator"""
        self.logger.info(f"Moving Imitator to Demonstrator's joint positions")
        demonstrator_pos = self.demonstrator.get_joint_positions()
        self.imitator.move_to_joint_positions(demonstrator_pos)

    def run_teleoperation(self):
        """teleoperate the robots until a Keyboard interrupt is received
        Note: this command is blocking
        """
        self.logger.info("Initializing Policies")
        demonstrator_policy = HumanController(self.demonstrator.robot_model.get_joint_angle_limits())
        self.demonstrator.send_torch_policy(demonstrator_policy, blocking=False)
        imitator_policy = HybridJointImpedanceControl(joint_pos_current=self.imitator.get_joint_positions(),
                                                      Kq=self.imitator.Kq_default, 
                                                      Kqd=self.imitator.Kqd_default, 
                                                      Kx=self.imitator.Kx_default, 
                                                      Kxd=self.imitator.Kxd_default, 
                                                      robot_model=self.imitator.robot_model,
                                                      ignore_gravity=self.imitator.use_grav_comp)
        self.imitator.send_torch_policy(imitator_policy, blocking=False)

        self.logger.info("Starting Teleoperation")
        try:
            while True:
                # update robot target position
                joint_pos_demonstrator = self.demonstrator.get_joint_positions()
                self.imitator.update_desired_joint_positions(joint_pos_demonstrator)

        except KeyboardInterrupt:
            self.logger.info("Received Interrupt Signal. Exiting teleoperation...")
        

@hydra.main(config_path="configs", config_name="multibot_env")
def main(cfg):
    # Initialize robot interfaces
    demonstrator = RobotInterface(ip_address = cfg.robot_1.server_ip,
                                  port = cfg.robot_1.robot_port)
    imitator = RobotInterface(ip_address = cfg.robot_2.server_ip,
                              port = cfg.robot_2.robot_port)

    handler = TeleoperationHandler(demonstrator, imitator)
    handler.run_teleoperation()

if __name__ == "__main__":
    main()
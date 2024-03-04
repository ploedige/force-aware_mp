import hydra
from omegaconf import OmegaConf
import logging
from typing import List

from torchcontrol.policies import HybridJointImpedanceControl
from polymetis import RobotInterface

from controllers.human_controller import HumanController

class TeleoperationHandler:
    def __init__(self, 
                 demonstrator: RobotInterface,
                 replicants: List[RobotInterface]):
        self.logger = logging.getLogger('teleoperation_handler')
        self.demonstrator = demonstrator
        self.replicants = replicants
        self.sync_robot_positions()

    def sync_robot_positions(self):
        """Sync the robot positions by moving the imitator to the current position of the demonstrator"""
        self.logger.info(f"Moving Imitator to Demonstrator's joint positions")
        demonstrator_pos = self.demonstrator.get_joint_positions()
        for replicant in self.replicants:
            replicant.move_to_joint_positions(demonstrator_pos)

    def run_teleoperation(self):
        """teleoperate the robots until a Keyboard interrupt is received
        Note: this command is blocking
        """
        self.logger.info("Initializing Policies")
        demonstrator_policy = HumanController(self.demonstrator.robot_model)
        self.demonstrator.send_torch_policy(demonstrator_policy, blocking=False)
        for replicant in self.replicants:
            replicant_policy = HybridJointImpedanceControl(joint_pos_current=replicant.get_joint_positions(),
                                                        Kq=replicant.Kq_default, 
                                                        Kqd=replicant.Kqd_default, 
                                                        Kx=replicant.Kx_default, 
                                                        Kxd=replicant.Kxd_default, 
                                                        robot_model=replicant.robot_model,
                                                        ignore_gravity=replicant.use_grav_comp)
            replicant.send_torch_policy(replicant_policy, blocking=False)

        self.logger.info("Starting Teleoperation")
        try:
            while True:
                joint_pos_demonstrator = self.demonstrator.get_joint_positions()
                for replicant in self.replicants:
                    replicant.update_desired_joint_positions(joint_pos_demonstrator)

        except KeyboardInterrupt:
            self.logger.info("Received Interrupt Signal. Exiting teleoperation...")
        

@hydra.main(config_path="configs", config_name="multibot_teleoperation")
def main(cfg):
    demonstrator = RobotInterface(ip_address = cfg.demonstrator.server_ip,
                                  port = cfg.demonstrator.robot_port)
    
    replicants = []
    for replicant_cfg in OmegaConf.to_container(cfg.replicants):
        replicants.append(RobotInterface(ip_address = replicant_cfg.server_ip,
                                         port = replicant_cfg.robot_port))

    handler = TeleoperationHandler(demonstrator, replicants)
    handler.run_teleoperation()

if __name__ == "__main__":
    main()
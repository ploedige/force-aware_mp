import hydra
import logging
from typing import List

from torchcontrol.policies import HybridJointImpedanceControl
from torchcontrol.utils import tensor_utils
from polymetis import RobotInterface

from controllers.force_feedback_controller import ForceFeedbackController

class TeleoperationHandler:
    def __init__(self, 
                 demonstrator: RobotInterface,
                 replicant: RobotInterface,
                 force_feedback: bool = True):
        self.logger = logging.getLogger('teleoperation_handler')
        self.demonstrator = demonstrator
        self.replicant = replicant
        self.force_feedback = force_feedback
        self.sync_robot_positions()

    def sync_robot_positions(self):
        """Sync the robot positions by moving the imitator to the current position of the demonstrator"""
        self.logger.info(f"Moving Imitator to Demonstrator's joint positions")
        demonstrator_pos = self.demonstrator.get_joint_positions()
        self.replicant.move_to_joint_positions(demonstrator_pos)

    def run_teleoperation(self):
        """teleoperate the robots until a Keyboard interrupt is received
        Note: this command is blocking
        """
        self.logger.info("Initializing Policies")
        replicant_policy = HybridJointImpedanceControl(joint_pos_current=self.replicant.get_joint_positions(),
                                                        Kq=self.replicant.Kq_default, 
                                                        Kqd=self.replicant.Kqd_default, 
                                                        Kx=self.replicant.Kx_default, 
                                                        Kxd=self.replicant.Kxd_default, 
                                                        robot_model=self.replicant.robot_model,
                                                        ignore_gravity=self.replicant.use_grav_comp)
        self.replicant.send_torch_policy(replicant_policy, blocking=False)
        initial_replica_load = self.replicant.get_robot_state().motor_torques_external
        initial_replica_load = tensor_utils.to_tensor(initial_replica_load)
        demonstrator_policy = ForceFeedbackController(self.demonstrator.robot_model, initial_replica_load, force_feedback=self.force_feedback)
        self.demonstrator.send_torch_policy(demonstrator_policy, blocking=False)
        self.logger.info("Starting Teleoperation")
        try:
            while True:
                joint_pos_demonstrator = self.demonstrator.get_joint_positions()
                self.replicant.update_desired_joint_positions(joint_pos_demonstrator)
                current_replication_torques = self.replicant.get_robot_state().motor_torques_external
                current_replication_torques = tensor_utils.to_tensor(current_replication_torques)
                self.demonstrator.update_current_policy({"replication_torques" : current_replication_torques})

        except KeyboardInterrupt:
            self.logger.info("Received Interrupt Signal. Exiting teleoperation...")
        

@hydra.main(config_path="configs", config_name="force_feedback_teleoperation")
def main(cfg):
    cfg
    demonstrator = RobotInterface(ip_address = cfg.demonstrator.server_ip,
                                  port = cfg.demonstrator.robot_port)
    replicant = RobotInterface(ip_address = cfg.replicant.server_ip,
                              port = cfg.replicant.robot_port)

    handler = TeleoperationHandler(demonstrator, replicant, cfg.force_feedback)
    handler.run_teleoperation()

if __name__ == "__main__":
    main()
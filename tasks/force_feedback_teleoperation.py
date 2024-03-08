from typing import List
from polymetis import RobotInterface
from tasks.base_tasks import TeleoperationBaseTask

from torchcontrol.policies import HybridJointImpedanceControl
from torchcontrol.utils import tensor_utils
from polymetis import RobotInterface

from controllers.force_feedback_controller import ForceFeedbackController

class ForceFeedbackTeleoperationTask(TeleoperationBaseTask):
    def __init__(self, robots: List[RobotInterface]) -> None:
        """Task for teleoperating one or more robots

        Args:
            robots (List[RobotInterface]):  First robot will be used as demonstrator.
                                            Second robot will replicat the movements and return force feedback to the demonstrator.
                                            All others will not do anything.
        """
        super().__init__(robots)
        if len(self.robots) < 2:
            self.logger.error("Not enough robots supplied as parameter. Teleoperation with force feedback requires two robots.")
            exit(1)
        self.demonstrator = self.robots[0]
        self.replicant = self.robots[1]
        if len(self.robots) > 2:
            self.logger.info("More than two robots supplied. Only the first two robots are used by this task.")

    def _initialize_policies(self):
        self.logger.info("Initializing policies...")
        initial_replication_torques = tensor_utils.to_tensor(self.replicant.get_robot_state().motor_torques_external)
        demonstrator_policy = ForceFeedbackController(self.demonstrator.robot_model,
                                                      initial_replication_torques)
        replicant_policy = HybridJointImpedanceControl(joint_pos_current=self.replicant.get_joint_positions(),
                                                        Kq=self.replicant.Kq_default, 
                                                        Kqd=self.replicant.Kqd_default, 
                                                        Kx=self.replicant.Kx_default, 
                                                        Kxd=self.replicant.Kxd_default, 
                                                        robot_model=self.replicant.robot_model,
                                                        ignore_gravity=self.replicant.use_grav_comp)
        self.demonstrator.send_torch_policy(demonstrator_policy)
        self.replicant.send_torch_policy(replicant_policy)
        self.logger.info("Policies initilized.")

    def run(self):
        self.sync_robot_positions
        self._initialize_policies(self)
        self.logger.info("Starting force feedback teleoperation...")
        while not self._stop_event.is_set():
            joint_pos_demonstrator = self.demonstrator.get_joint_positions()
            self.replicant.update_desired_joint_positions(joint_pos_demonstrator)
            current_replication_torques = self.replicant.get_robot_state().motor_torques_external
            current_replication_torques = tensor_utils.to_tensor(current_replication_torques)
            self.demonstrator.update_current_policy({"replication_torques" : current_replication_torques})
        self.logger.info("Teleoperation terminated successfully.")
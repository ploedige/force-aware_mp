from typing import List

from polymetis import RobotInterface
from torchcontrol.policies import HybridJointImpedanceControl

from controllers.human_controller import HumanController
from tasks.base_tasks import TeleoperationBaseTask

class MultibotTeleoperationTask(TeleoperationBaseTask):
    def __init__(self, robots: List[RobotInterface]) -> None:
        """Task for teleoperating one or more robots

        Args:
            robots (List[RobotInterface]):  First robot will be used as demonstrator.
                                            All others will replicate the movements.
        """
        super().__init__(robots)
        self.demonstrator = self.robots[0]
        self.replicants = self.robots[1:]

    def _initialize_policies(self):
        self.logger.info("Initializing policies...")
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
        self.logger.info("Policies initilized.")

    def run(self):
        self.sync_robot_positions()
        self._initialize_policies()
        self.logger.info("Starting multibot teleoperation...")
        while not self._stop_event.is_set():
            joint_pos_demonstrator = self.demonstrator.get_joint_positions()
            for replicant in self.replicants:
                replicant.update_desired_joint_positions(joint_pos_demonstrator)
        self.logger.info("Multibot teleoperation terminated successfully.")
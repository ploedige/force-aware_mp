from controllers.torque_trajectory_executor import TorqueTrajectoryExecutor
from tasks.base_tasks import ReplayBaseTask
from torchcontrol.utils.tensor_utils import to_tensor

from torchcontrol.policies.impedance import HybridJointImpedanceControl

class TorqueDemonstrationReplay(ReplayBaseTask):
    def __init__(self, robots, demonstrations):
        super().__init__(robots, demonstrations)
        self.demonstration = self.demonstrations[0]
        self.torque_trajectory = [tp.joint_torques_computed for tp in self.demonstration]
        self.torque_trajectory = [to_tensor(tp) for tp in self.torque_trajectory]
        self.pos_trajectory = [tp.joint_positions for tp in self.demonstration]
        self.pos_trajectory = [to_tensor(tp) for tp in self.pos_trajectory]
        for robot in self.robots:
            robot.move_to_joint_positions(self.pos_trajectory[0])

    def run(self):
        for robot in self.robots:
            policy = TorqueTrajectoryExecutor(self.torque_trajectory)
            robot.send_torch_policy(policy, blocking=False)
        self._stop_event.wait()
        for robot in self.robots:
            robot.send_torch_policy(None, blocking=True)



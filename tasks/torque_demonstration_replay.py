from controllers.torque_trajectory_executor import TorqueTrajectoryExecutor
from tasks.base_tasks import ReplayBaseTask
from torchcontrol.utils.tensor_utils import to_tensor

class TorqueDemonstrationReplay(ReplayBaseTask):
    def __init__(self, robots, demonstrations):
        super().__init__(robots, demonstrations)
        self.demonstration = self.demonstrations[0]
        self.torque_trajectory = [tp.motor_torques_measured for tp in self.demonstration]
        self.torque_trajectory = to_tensor(self.torque_trajectory)

    def run(self):
        for robot in self.robots:
            policy = TorqueTrajectoryExecutor(self.torque_trajectory)
            robot.send_torch_policy(policy, blocking=False)
        self._stop_event.wait()
        for robot in self.robots:
            robot.send_torch_policy(None, blocking=True)



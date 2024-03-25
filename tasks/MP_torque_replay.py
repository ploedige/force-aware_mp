from datetime import datetime, timedelta

from mp_pytorch.mp import MPFactory
import torchcontrol as toco

from controllers.torque_trajectory_executor import TorqueTrajectoryExecutor
from tasks.base_tasks import ReplayBaseTask
from torchcontrol.utils.tensor_utils import to_tensor

class MPTorqueReplay(ReplayBaseTask):
    def __init__(self, robots, demonstrations):
        super().__init__(robots, demonstrations)
        self.torque_trajectory = self._create_torques_from_mp(demonstrations)
        self.pos_trajectory = [tp.joint_positions for tp in self.demonstration]
        self.pos_trajectory = [to_tensor(tp) for tp in self.pos_trajectory]
        for robot in self.robots:
            robot.move_to_joint_positions(self.pos_trajectory[0])

    def _create_torques_from_mp(self, demonstrations):
        demonstration = demonstrations[0]
        demonstration = demonstration[::1000]
        start_time = datetime.fromtimestamp(demonstration[0].timestamp.seconds + demonstration[0].timestamp.nanos * 1e-9)
        times = [datetime.fromtimestamp(tp.timestamp.seconds + tp.timestamp.nanos * 1e-9) for tp in demonstration]
        times = [(t - start_time).total_seconds() for t in times]
        times = toco.utils.to_tensor(times)
        torques = [tp.joint_torques_computed for tp in demonstration]
        torques = toco.utils.to_tensor(torques)

        mp = MPFactory.init_mp(mp_type='prodmp', num_dof=7)
        mp_dict = mp.learn_mp_params_from_trajs(times, torques)

        torques, _ = mp.get_trajs()
        return torques

    def run(self):
        for robot in self.robots:
            policy = TorqueTrajectoryExecutor(self.torque_trajectory)
            robot.send_torch_policy(policy, blocking=False)
        self._stop_event.wait()
        for robot in self.robots:
            robot.send_torch_policy(None, blocking=True)



from typing import Dict

import torch
import torchcontrol as toco
import numpy as np

from human_controller import HumanController
from control_modules.kalman_filter import KalmanFilter

class ForceFeedbackController(HumanController):
    def __init__(self, robot_model:toco.models.RobotModelPinocchio, initial_replica_load: torch.Tensor, 
                 regularize:bool = True, force_feedback:bool = True):
        """Controller for human input with force feedback from a replicating robot

        Args:
            robot_model (toco.models.RobotModelPinocchio): model of the controlled robot
            initial_replica_load (torch.Tensor): initial load from the replicant
            regularize (bool, optional): Defaults to True.
            force_feedback (bool, optional): _description_. Defaults to True.
        """
        super().__init__(robot_model, regularize)
        # Force feedback parameters
        self.fb_gain = -1.0 * np.array(
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], dtype=np.float64
        )

        self.torque_dgain = 0.5 * np.array(
            [50.0, 50.0, 50.0, 50.0, 15.0, 8.0, 8.0], dtype=np.float64
        )
        self.tau_moving_average = np.zeros(7)
        self.alpha = 0.9


        self.replica_load = initial_replica_load
        self._replica_load_filter = KalmanFilter(self.replica_load)

        self._force_feedback = force_feedback

    def get_force_feedback(self):
        """
        General idea of this torque feedback:
        Have a D controller on the primary velocity which activates only when external forces are present. This feature
        combines the safety of the primary robot with its useabilty: if the
        D controller were always active the human would not be able to move the primary robot easily. However, without
        a D controller the primary robot (which is next to a human) can move very fast if the external forces are high.
        This needs to be prevented. This is the algorithm:
        1. Get the filtered external forces from the replica robot
        2. filter out small forces, this is crucial to filter out the inherent sensor noise.
           While we loose the feedback of small forces, this improves the general control of the primary robot.
           While this also clips the forces with 'max_force', the current D controller on the primary velocity handles
           too high forces acting on the primary robot as well by regularizing the primary velocity.
        3. Compute the D control feedback 'd_feedback' based on the primary joint velocities
        4. clip 'd_feedback' with the absolute value of the current external forces. However, for a safer
           environment, also include the latest external forces with a moving average.
        returns the force feedback - 'd_feedback'
        """
        # 1. get force feedback from replica
        replica_load = self._replica_load_filter(self.replica_load)
        # 2. total force clip filter
        # computes l1 norm of the replica load (maybe with incorporated d-gain control of the primary velocity).
        MIN_FORCE_THRESHOLD = 4.0 
        FORCE_INTERPOLATION_THRESHOLD = 4.66
        # If it is bigger than a: return replica_load
        MAX_FORCE  = 60.0# if the force is bigger than MAX_FORCE: scale it down

        total_force = np.sum(np.abs(self.fb_gain * replica_load))
        if total_force < MIN_FORCE_THRESHOLD:
            plain_feedback =  np.zeros(7)
        elif total_force < FORCE_INTERPOLATION_THRESHOLD:
            interpolation_area = FORCE_INTERPOLATION_THRESHOLD - MIN_FORCE_THRESHOLD
            plain_feedback = (1 / (interpolation_area) * total_force - FORCE_INTERPOLATION_THRESHOLD / (interpolation_area)) * replica_load
        elif total_force < MAX_FORCE:
            plain_feedback =  replica_load
        else:
            plain_feedback =  replica_load * (MAX_FORCE / total_force)

        # 3. get d control feedback from primary
        primary_j_vel = self.primary_robot.current_j_vel
        d_feedback = self.torque_dgain * primary_j_vel
        # update moving average of the latest external forces
        self.tau_moving_average = self.alpha * self.tau_moving_average + (
            1 - self.alpha
        ) * np.abs(plain_feedback)
        # 4. compute clipping boundaries for d_feedback
        m = np.maximum(np.abs(plain_feedback), self.tau_moving_average)
        # clip and return
        d_feedback = np.clip(d_feedback, -m, m)
        return plain_feedback - d_feedback

    def enable_force_feedback(self):
        print("Enabled Force Feedback!")
        self._active_force_feedback = True

    def disable_force_feedback(self):
        print("Disabled Force Feedback!")
        self._active_force_feedback = False

    def forward(self, state_dict: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        human_control_torques = super().forward(state_dict)["joint_torques"]
        force_feedback = self.get_force_feedback()
        if self._active_force_feedback:
            return {"joint_torques" : human_control_torques + force_feedback}
        else:
            return {"joint_torques" : human_control_torques}
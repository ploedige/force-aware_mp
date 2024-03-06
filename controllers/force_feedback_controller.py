from typing import Dict

import torch
import torchcontrol as toco
import numpy as np

from controllers.human_controller import HumanController
from control_modules.kalman_filter import KalmanFilter

class ForceFeedbackController(HumanController):
    def __init__(self, 
                 robot_model: toco.models.RobotModelPinocchio, 
                 assistive_gain:torch.Tensor = torch.Tensor([0.26, 0.44, 0.40, 1.11, 1.10, 1.20, 0.85]),
                 centering_gain:torch.Tensor = torch.Tensor([5.0, 2.2, 1.3, 0.3, 0.1, 0.1, 0.0]),
                 initial_replication_torques: torch.Tensor = torch.Tensor([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]), 
                 force_feedback_damping_gain: torch.Tensor = torch.Tensor([25.0, 25.0, 25.0, 25.0, 7.5, 4.0, 4.0]),
                 force_feedback:bool = True):
        """HumanController with capability to give force feedback to the user
        To reproduce a torque the torque has to be transmitted to this controller via the update_parameter({"replication_torque": <torques_to_be_reproduced>}) function

        Args:
            robot_model (toco.models.RobotModelPinocchio): physical model of the robot
            assistive_gain (torch.Tensor, optional): gain for assisting the movement of the robot. Defaults to torch.Tensor([0.26, 0.44, 0.40, 1.11, 1.10, 1.20, 0.85]).
            centering_gain (torch.Tensor, optional): this gain lightly forces the robot back into its idle position. Set all elements to 0 to disable. Defaults to torch.Tensor([5.0, 2.2, 1.3, 0.3, 0.1, 0.1, 0.0]).
            initial_replication_torques (torch.Tensor, optional): initialize the force feedback. Defaults to torch.Tensor([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]).
            force_feedback_damping_gain (torch.Tensor, optional): gain for damping the force feedback depending on the current velocity. Defaults to torch.Tensor([25.0, 25.0, 25.0, 25.0, 7.5, 4.0, 4.0]).
            force_feedback (bool, optional): enables/disables force feedback. Defaults to True.
        """
        super().__init__(robot_model, assistive_gain, centering_gain)
        self.replication_torques = torch.nn.Parameter(initial_replication_torques)
        self._force_feedback_damping_gain = force_feedback_damping_gain
        self._force_feedback = force_feedback

    def _get_force_feedback_torques(self, replication_torques: torch.Tensor, joint_vel_current: torch.Tensor) -> torch.Tensor:
        feedback_damping = self._force_feedback_damping_gain * joint_vel_current
        boundaries = torch.abs(replication_torques)
        feedback_damping = torch.clamp(feedback_damping, -boundaries, boundaries)
        return replication_torques - feedback_damping


    def forward(self, state_dict: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        assistive_torques = self._get_assistive_torques(state_dict["motor_torques_external"])
        centering_torques = self._get_centering_torques(state_dict["joint_positions"])
        # force_feedback_torques = self._get_force_feedback_torques(self.replication_torques, state_dict["joint_velocities"])
        force_feedback_torques = self.replication_torques

        if self._force_feedback:
            return {"joint_torques": assistive_torques + centering_torques - force_feedback_torques}
        else:
            return {"joint_torques": assistive_torques + centering_torques}
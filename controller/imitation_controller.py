import torchcontrol as toco

from polymetis import RobotInterface

class ImitationController(toco.policies.HybridJointImpedanceControl):
    def __init__(self, robot: RobotInterface):
        super().__init__(
            joint_pos_current=robot.get_joint_positions(),
            Kq=robot.Kq_default,
            Kqd=robot.Kqd_default,
            Kx=robot.Kx_default,
            Kxd=robot.Kxd_default,
            robot_model=robot.robot_model,
            ignore_gravity=robot.use_grav_comp,
        )

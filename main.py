import hydra
import time
import logging

from polymetis import RobotInterface

from tasks.force_feedback_teleoperation import ForceFeedbackTeleoperationTask
from tasks.multibot_teleoperation import MultibotTeleoperationTask

@hydra.main(config_path="configs", config_name="robots")
def main(cfg):
    logger = logging.Logger("MAIN")
    demonstrator = RobotInterface(ip_address = cfg.robot_1.server_ip,
                                  port = cfg.robot_1.robot_port)
    replicant = RobotInterface(ip_address = cfg.robot_2.server_ip,
                              port = cfg.robot_2.robot_port)

    # task = ForceFeedbackTeleoperationTask([demonstrator, replicant])
    task = MultibotTeleoperationTask([demonstrator, replicant])
    task.start()
    try:
        while True:
            time.sleep(10)
            print(demonstrator.get_robot_state)
    except KeyboardInterrupt:
        logger.info("Received Interrupt Signal. Exiting Task...")
        task.stop()

if __name__ == "__main__":
    main()
from hardware.txts import HBW1, MM1, OV1, SM1, VGR1, EC1
from multiprocessing import Process


def init_hbw1():
    HBW1.HighBayWarehouse1()


def init_mm1():
    MM1.MillingMachine1()


def init_ov1():
    OV1.OvenAndWTAndWT1()


def init_sm1():
    SM1.SortingMachine1()


def init_vgr1():
    VGR1.VacuumGripperRobot1()


def init_ec1():
    EC1.EnvironmentAndCamera1()


if __name__ == '__main__':
    process_list = [
        Process(target=init_hbw1),
        Process(target=init_mm1),
        Process(target=init_ov1),
        Process(target=init_sm1),
        Process(target=init_vgr1),
        Process(target=init_ec1),
    ]
    [process.start() for process in process_list]
    [process.join() for process in process_list]
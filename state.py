import redis
from enum import Enum

class Variables(Enum):
    batteryValues = 11              # "Battery JSON string"
    xtenderValues = 12              # "Xtender JSON string"
    powerLimit = 13                 # "powerLimit JSON string"
    currentOutValues = 14           # "currentOut JSON string"
    currentInValues = 15            # "currentIn JSON string"
    contactorValues = 16            # "contactors JSON string"
    
    XT_Imax = 17                    # "powerLimit [%d A]"
    XT_IL1max = 18                  # "Imax L1 [%d A]"
    XT_IL2max = 19                  # "Imax L2 [%d A]"
    XT_IL3max = 51                  # "Imax L2 [%d A]" - manglet
    XT_Imaxtarget = 20              # "Imax target [%d A]"
    XT_targetL1 = 21                # "ImaxL1 target [%d A]"
    XT_targetL2 = 22                # "ImaxL2 target [%d A]"
    XT_targetL3 = 52                # "ImaxL3 target [%d A]" - manglet

    XT1transfer = 23                # "XT#1 in transfer"
    XT2transfer = 24                # "XT#2 in transfer"

    XT_time = 25                    # "Tid: [%s]"
    XT_invVoltOutV12 = 26           # "AC voltage out V12[%d V]"
    XT_invVoltOutV31 = 27           # "AC voltage out V31[%d V]"
    XT_invVoltInV12 = 28            # "AC voltage in V12[%d V]"
    XT_invVoltInV31 = 29            # "AC voltage in V31[%d V]"

    XT_invCurrentInL1 = 30          # "AC current in L1[%d A]"
    XT_invCurrentInL2 = 31          # "AC current in L2[%d A]"
    XT_invCurrentOutL1 = 32         # "AC current out L1 [%d A]"
    XT_invCurrentOutL2 = 33         # "AC current out L2 [%d A]"

    CAN_batteryCurrent = 34         # "Battery Current[%2.1f A]"
    CAN_batteryVoltage = 35         # "Battery Voltage [%2.1f V]"
    CAN_batterySoC = 36             # "Battery SoC[%.1f %%]"
    CAN_batteryTemp = 37            # "Battery Temperature[%.1f C]"
    CAN_batterySoH = 38             # "Battery SoH[%.1f %%]"

    # Ikke-brukte items
    CAN_maxBatteryTemp = 39         # "Max battery temperature[%.1f C]"
    CAN_minBatteryVolt = 40         # "Min battery voltage[%.1f V]"
    XT_minVoltOutV12 = 41           # "AC out V12[%d V]"
    XT_maxVoltOutV12 = 42           # "AC out V12[%d V]"
    XT_minVoltOutV31 = 43           # "AC out V31[%d V]"
    XT_maxVoltOutV31 = 44           # "AC out V31[%d V]"
    XT_maxPowerOut = 45             # "Max power [%d V]"

    XT_Test_Auto = 46
    XT_Idelta = 47                  # "Margin from average load to Imax"
    XT_Ihyst = 48                   # "Hysteresis for changing Imax values"
    XT_avgNo = 49                   # "No of readings to calculate average load"

    # Items for tidsstyring
    last_notifications_sent = 50    # "Siste sendte varsler"

class State:
    def __init__(self, host="localhost", port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db)
        self.p = self.client.pubsub()

        self.p_thread = self.p.run_in_thread(sleep_time=0.001, exception_handler=print)

    def close(self):
        self.p_thread.stop()
        self.p.close()
        self.client.close()

    def get_variable(self, var: Variables) -> str:
        x = self.client.get(str(var.value))
        if x is None:
            return x
        return self.client.get(str(var.value)).decode("utf-8")

    def set_variable(self, var: Variables, val):
        pipe = self.client.pipeline()
        pipe.get(str(var.value))
        pipe.set(str(var.value), str(val))

        res = pipe.execute()

        if res[0] is None or res[0].decode("utf-8") != str(val):
            self.client.publish("ch" + str(var.value), str(val))

    def add_change_listener(self, var: Variables, func):
        def imm_func(data):
            func(data["data"].decode("utf-8"))

        self.p.subscribe(**{"ch" + str(var.value): imm_func})

if __name__ == "__main__":
    state_manager = State()
    
    print ("starter")

    #x = state_manager.get_variable(Variables.iEM_currentOutL1)
    # print(x)

    x = state_manager.get_variable(Variables.xtenderValues)
    print(x)
    
    def func(current_out_l1: str):
        print(current_out_l1)

    state_manager.add_change_listener(Variables.xtenderValues, func)

    state_manager.set_variable(Variables.xtenderValues, "HeiHei Hei")

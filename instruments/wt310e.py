# *******************************************
# Yokogawa WT310E Python Config Program
#
# Author: MTarvina
# Last Updated: 09.August.2022
# *******************************************

from numpy import False_
import pyvisa
import time


class WT310E_GPIB:
    CmdDelay = 0.05
    DefaultSetting = {
        ":INPUT:VOLTAGE": "AUTO ON",
        ":INPUT:CURRENT": "AUTO ON",
        ":MEASURE:AVERAGING:TYPE": "LINEAR",
        ":MEASURE:AVERAGING:COUNT": "64",
        ":MEASURE:AVERAGING:STATE": "ON",
        ":INPUT:MODE": "RMS",
        ":NUMERIC:FORMAT": "ASCII",
        ":NUMERIC:NORMAL:ITEM1": "U,1",
        ":NUMERIC:NORMAL:ITEM2": "I,1",
        ":NUMERIC:NORMAL:ITEM3": "P,1",
        ":NUMERIC:NORMAL:ITEM4": "LAMBDA,1"        
    }


    def __init__(self, resourceManager, gpibCard, gpibAddr, name="PowerMeter"):
        """Create an instance of WT310E object

        Args:
            resourceManager (ResourceManager): ResourceManager object from pyvisa module
            gpibCard (int): GPIB Card, use 0 by default.
            gpibAddr (int): GPIB Address of the physically connected WT310E power meter.
            name (str, optional): Custom name for power meter, for code prompt distinction. Defaults to "PowerMeter".
        """

        self.rm = resourceManager
        self.card = gpibCard
        self.addr = gpibAddr
        self.name = name
        self.connected = False
        self.defaultSetting = WT310E_GPIB.DefaultSetting
        self.param = {
            "volt": 0.0,
            "amp": 0.0,
            "watt": 0.0,
            "pf": 0.0
        }


    def Connect(self):
        """Connect to the power meter. Automatically loads default settings.
        """

        try:
            self.meter = self.rm.open_resource(f"GPIB{self.card}::{self.addr}::INSTR")
            self.Prompt("Successfully connected to WT310E Power Meter")
            self.connected = True
            self.LoadDefaultSetting()
        except:
            print(f"+ [ERROR]: Could not establish connection with WT310E Power Meter at Address: {self.addr}")
            self.connected = False
            return


    def Cmd(self, cmd):
        """Issue a specific GPIB command to the power meter, that is not included in this class definition

        Args:
            cmd (str): GPIB Command
        """

        if self.connected:
            self.meter.write(cmd)
            time.sleep(self.CmdDelay)


    def Prompt(self, msg):
        """Print out a formatted prompt which indicates this object's name and GPIB address

        Args:
            msg (str): Prompt
        """
        
        print(f"+ [{self.name} @ GPIB({self.addr})]: {msg}")


    def LoadDefaultSetting(self):
        """Loads the common use case setting for the power meter. Refer to WT310E_GPIB.DefaultSetting
        """

        if self.connected:
            self.Cmd("*RST")
            for (key, value) in self.defaultSetting.items():
                self.Cmd(f"{key} {value}")
                self.Prompt(f"Default setting loaded - {key} {value}")
                time.sleep(self.CmdDelay)

    def ReadVoltage(self):
        """Queries the voltage reading from the power meter and saves the data into self.param["volt"]
        """
        
        if self.connected:
            self.Cmd("HOLD ON")
            self.param["volt"] = float(self.meter.query("NUM:NORM:VAL? 1").strip())
            time.sleep(self.CmdDelay)
            self.Cmd("HOLD OFF")


    def ReadCurrent(self):
        """Queries the current reading from the power meter and saves the data into self.param["amp"]
        """

        if self.connected:
            self.Cmd("HOLD ON")
            self.param["amp"] = float(self.meter.query("NUM:NORM:VAL? 2").strip())
            time.sleep(self.CmdDelay)
            self.Cmd("HOLD OFF")


    def ReadPower(self):
        """Queries the power reading from the power meter and saves the data into self.param["watt"]
        """
        
        if self.connected:
            self.Cmd("HOLD ON")
            self.param["watt"] = float(self.meter.query("NUM:NORM:VAL? 3").strip())
            time.sleep(self.CmdDelay)
            self.Cmd("HOLD OFF")


    def ReadPowerFactor(self):
        """Queries the Power factor reading from the power meter and saves the data into self.param["pf"]
        """
        
        if self.connected:
            self.Cmd("HOLD ON")
            self.param["pf"]   = float(self.meter.query("NUM:NORM:VAL? 4").strip())    
            time.sleep(self.CmdDelay)
            self.Cmd("HOLD OFF")


    def ReadParams(self):
        """Queries all measurement readings from the power meter and saves the data into self.param
        """
        
        if self.connected:
            self.Cmd("HOLD ON") 
            self.param["volt"] = float(self.meter.query("NUM:NORM:VAL? 1").strip())
            time.sleep(self.CmdDelay)
            self.param["amp"]  = float(self.meter.query("NUM:NORM:VAL? 2").strip())
            time.sleep(self.CmdDelay)
            self.param["watt"] = float(self.meter.query("NUM:NORM:VAL? 3").strip())
            time.sleep(self.CmdDelay)
            self.param["pf"]   = float(self.meter.query("NUM:NORM:VAL? 4").strip())    
            time.sleep(self.CmdDelay)
            self.Cmd("HOLD OFF")


    def Disconnect(self):
        """Disconnect from the power meter
        """

        if self.connected:
            self.meter.close()
            self.connected = False
            self.Prompt("Disconnected")



# sample usage of WT310E_GPIB object
if __name__ == "__main__":

    bench = pyvisa.ResourceManager()
    instruments = bench.list_resources()
    # print(instruments)

    # Create object instance, it is encouraged to use the variable name as input to the "name" parameter
    inputPM = WT310E_GPIB(bench, gpibCard=0, gpibAddr=15, name="InputPM")    
    inputPM.Connect()

    if inputPM.connected:
        for i in range(20):
            inputPM.ReadParams()
            print("-------------------------------------------")
            print(f'{inputPM.name} Parameters....')
            print(f'Voltage: {inputPM.param["volt"]}')
            print(f'Current: {inputPM.param["amp"]}')
            print(f'Power: {inputPM.param["watt"]}')
            print(f'PF: {inputPM.param["pf"]}')
            time.sleep(2.0)
        inputPM.Disconnect()
    
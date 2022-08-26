# *******************************************
# Chroma 6314A Python Config Program
#
# Author: MTarvina
# Last Updated: 09.August.2022
# *******************************************

import pyvisa
import time


class CHROMA6314A_GPIB:
    CmdDelay = 0.05
    DefaultSetting = {
        "CONF:AUTO:LOAD": "OFF",
        "CONF:AUTO:MODE": "LOAD",               # LOAD or PROGRAM
        "CONF:REMOTE":  "OFF",                  # Effective only in RS232C
        
    }

    def __init__(self, resourceManager, gpibCard, gpibAddr, name="ELoad"):
        """Create an instance of Chroma6314A object 

        Args:
            resourceManager (ResourceManager): ResourceManager object from pyvis module
            gpibCard (int): GPIB Card, use 0 by default.
            gpibAddr (int): GPIB Address of the physically connected Chroma6314A Eload.
            name (str, optional): Custom name for Eload. Defaults to "ELoad".
        """

        self.rm = resourceManager
        self.card = gpibCard
        self.addr = gpibAddr
        self.name = name
        self.connected = False
        self.defaultSetting = CHROMA6314A_GPIB.DefaultSetting


    def Connect(self):
        """Connect to the eload. Automatically loads default settings.
        """

        try:
            self.eload = self.rm.open_resource(f"GPIB{self.card}::{self.addr}::INSTR")
            self.Prompt("Successfully connected to Chroma6314A Eload")
            self.connected = True
            self.LoadDefaultSettings()
        except:
            print(f"+ ERROR: Could not establish connection with Chroma6314A Eload at Address: {self.addr}")
            self.connected = False
            return


    def Cmd(self, cmd):
        """Issue a specific GPIB command to the eload, that is not included in this class definition

        Args:
            cmd (str): GPIB Command
        """

        if self.connected:
            self.eload.write(cmd)
            time.sleep(self.CmdDelay)


    def Prompt(self, msg):
        """Print out a formatted prompt which indicates this object's name and GPIB address

        Args:
            msg (str): Prompt
        """
        
        print(f"+ [{self.name} @ GPIB({self.addr})]: {msg}")


    def LoadDefaultSettings(self):
        """Loads the common use case setting for the power meter. Refer to WT310E_GPIB.DefaultSetting
        """

        if self.connected:
            self.Cmd("*RST")
            self.Cmd("ABOR")
            for (key, value) in self.defaultSetting.items():
                self.Cmd(f"{key} {value}")
                self.Prompt(f"Default setting loaded - {key} {value}")
                time.sleep(self.CmdDelay)
            time.sleep(0.5) # wait for instrument to settle


    def EnableChannel(self, chan, sync="ON"):
        """Enable a specific ELoad channel

        Args:
            chan (int): ELoad Channel
            sync (str, optional): Set the load module to receive synchronized command action. Defaults to "ON".
        """

        if self.connected:        
            self.Cmd(f"CHAN {chan}")
            self.Cmd("CHAN:ACT ON")
            self.Cmd(f"CHAN:SYNC {sync}")

    
    def ConfigureChannel(self, chan, voltage="ON", vRange="H", vLatch="OFF", sound="ON"):
        pass



    def Disconnect(self):
        """Disconnect from the eload
        """

        if self.connected:
            self.eload.close()




# this is a sample implementation of WT310E_GPIB object
if __name__ == "__main__":

    bench = pyvisa.ResourceManager()
    instruments = bench.list_resources()
    # # print(instruments)

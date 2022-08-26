# -*- coding: utf-8 -*-
"""
Created on Sat Mar 12 13:31:47 2022

@author: AMendoza
"""

import pyvisa as visa
import time

def main():
    integ_time = float(input("Integration Time (sec): "))
    acs = float(input("Input Voltage (Vac): "))
   
    # Equipment Init
    rm = visa.ResourceManager()
    ac_source = rm.open_resource("GPIB0::5::INSTR")
    input_pm = rm.open_resource("GPIB0::20::INSTR")

    # Power Meter Settingssssssss
    # input_pm.write("*RST")
    input_pm.write(":INPUT:VOLTAGE:RANGE 300")
    input_pm.write(":INPUT:CURRENT:RANGE 0.1")
    input_pm.write(":MEASURE:AVERAGING:STATE OFF")
    input_pm.write(":MATH AVW3")
    input_pm.write(":INPUT:MODE RMS")
    input_pm.write(":NUMERIC:FORMAT ASCII")
    input_pm.write(":NUMERIC:NORMAL:ITEM1 U,1")
    input_pm.write(":NUMERIC:NORMAL:ITEM2 I,1")
    input_pm.write(":NUMERIC:NORMAL:ITEM3 WH,1")
    input_pm.write(":NUMERIC:NORMAL:ITEM4 LAMBDA,1")

    # AC Source Settings
    ac_source.write("OUTP:COUP AC")
    ac_source.write("SOUR:VOLT %f" %(acs))
    ac_source.write("SOUR:FREQ 60")
    ac_source.write("OUTP ON")

    time.sleep(5)


    # Print headers
    print ("\n", "============================  START  ============================", "\n")
    print ("Vin", "     Iin", "      PF",  "    Energy", "    Pin")
    
    # Data Write
    input_pm.write(":INTEGRATE:RESET")
    input_pm.write(":INTEGRATE:START")
    input_pm.write(":INTEG:TIM 0,0,%s" %(integ_time))
        
    time.sleep(integ_time)
        
        # seconds_time = integ_time
        # seconds = 0
        
        # input_pm.write(":INTEGRATE:STOP")
                
    # Record values
    input_pm.write("HOLD ON")
    input_voltage = float(input_pm.query("NUM:NORM:VAL? 1").strip())
    input_current = float(input_pm.query("NUM:NORM:VAL? 2").strip())
    energy = float(input_pm.query("NUM:NORM:VAL? 3").strip())
    input_power = float(energy)*1000*60*(60/integ_time)
    input_pf = float(input_pm.query("NUM:NORM:VAL? 4").strip())
        
    print ("Energy =  ", energy)
    
    #Print values
    print ("%.2f" %input_voltage, " |", "%.2f" %input_current," |", "%.2f" %input_pf,"|", "%.5f" %energy,"|", "%.3f" %input_power)
    input_pm.write("HOLD OFF")


            
    ac_source.write("OUTP OFF")
    
    time.sleep(5)

    #ac_source.write("*RST")
    input_pm.write("*RST")

    ac_source.close()
    input_pm.close()
    

    print ("\n", "=============================  END  =============================", "\n")


if __name__ == "__main__":
    main()

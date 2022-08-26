import time
import pyvisa
import csv
from wt310e_config import WT310E_GPIB


def main():
    inputAddr = 1
    out1Addr = 2
    out2Addr = 3

    defSoakTime = 15.0              # default soak time in minutes
    defsamplingInterval = 15.0      # default sampling interval in seconds
    defNSamples = 30                # default number of samples to capture after soaking
    defFileName = "efficiency_data" # default filename of csv datalog file

    bench = pyvisa.ResourceManager()
    print(bench.list_resources())   

    inputPM = WT310E_GPIB(bench, gpibCard=0, gpibAddr=inputAddr)
    out1PM = WT310E_GPIB(bench, gpibCard=0, gpibAddr=out1Addr)
    out2PM = WT310E_GPIB(bench, gpibCard=0, gpibAddr=out2Addr)

    inputPM.connect()
    out1PM.connect()
    out2PM.connect()

    if inputPM.connected and out1PM.connected and out2PM.connected:
        inputPM.loadDefaultSettings()
        out1PM.loadDefaultSettings()
        out2PM.loadDefaultSettings()

        buf = input("Soak Time (in minutes): ")
        try:
            soakTime = float(buf)
            print(f"+++ Soak time = {soakTime} minutes\n")
        except:
            soakTime = defSoakTime
            print(f"+++ Invalid input, now using default soak time of {soakTime} minutes.\n")
        
        buf = input("Sampling Interval (in seconds): ")
        try:
            samplingInterval = float(buf)
            print(f"+++ Sampling Interval = {samplingInterval} seconds\n")
        except:
            samplingInterval = defsamplingInterval
            print(f"+++ Invalid input, now using default sampling interval of {samplingInterval} seconds\n")

        buf = input("Number of data samples: ")
        try:
            nSamples = int(buf)
            print(f"+++ Number of samples = {nSamples}")
        except:
            nSamples = defNSamples
            print(f"+++ Invalid input, now using default number of samples: {nSamples}")

        buf = input("Enter datalog filename: ")
        if buf:
            outputFile = buf
        else:
            outputFile = defFileName

        with open(f"{outputFile}.csv", 'w', newline='') as csvf:
            datalog = csv.writer(csvf)
            datalog.writerow(["*", "Vin", "Iin", "Pin", "PFin", "Vout1", "Iout1", "Pout1", "PFout1", "Vout2", "Iout2", "Pout2", "PFout2", "Eff"])

            bMeasurementDone = False
            bSoaking = True
            bMeasuring = False
            tickCounter = 0
            soakTimeOut = int((soakTime*60.0)/samplingInterval)
            dataSample = 0

            while (not bMeasurementDone):
                inputPower = 0.0        # reset temporary variable
                outputPower= 0.0        # reset temporary variable
                efficiency = 0.0        # reset temporary variable

                time.sleep(samplingInterval)
                tickCounter+=1

                if tickCounter > soakTimeOut:
                    bSoaking = False
                    bMeasuring = True

                if bSoaking:
                    print("+++ \tSoaking...")
                elif bMeasuring:
                    print("+++ \tMeasuring...")

                inputPM.getParams()
                out1PM.getParams()
                out2PM.getParams()

                inputPower = inputPM.params["watt"]
                outputPower = out1PM.params["watt"] + out2PM.params["watt"]
                efficiency = float(100*(outputPower/inputPM.params["watt"]))

                print(f"+++ \tPin={inputPower}, \tPout={outputPower}, \tEfficiency={efficiency}")

                if bMeasuring:
                    datalog.writerow([  "",
                                        inputPM.params["volt"], inputPM.params["amp"], inputPM.params["watt"], inputPM.params["pf"],
                                        out1PM.params["volt"], out1PM.params["amp"], out1PM.params["watt"], out1PM.params["pf"],
                                        out2PM.params["volt"], out2PM.params["amp"], out2PM.params["watt"], out2PM.params["pf"],
                                        efficiency
                                    ])    
                    dataSample+=1      
                    if dataSample == nSamples:
                        bMeasurementDone = True
        
        inputPM.disconnect()
        out1PM.disconnect()
        out2PM.disconnect()

    else:
        print("+++ ERROR: Could not connect to equipment. Please check your GPIB connection.")
        return



if __name__ == "__main__":
    main()

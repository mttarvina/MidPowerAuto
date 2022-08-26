import pyvisa
import time
import math

#Eload chan 3,
#input PM GPIB2,
#output PM GPIB1,
# Chroma AC source ac_source.write("SOUR:VOLT:LEV:DC %s" %(acs))

def main():

    #enter = raw_input("Place the ff probes:\nCh3:Cmp\n\nOK?")
    
    full_load = float(input("Enter Full load in (A): "))
    load_increment_pct = float(input("Enter decrement of load in (%): "))
    load_increment= full_load*load_increment_pct/100
    acs = float(input("Enter input voltage in (Vac): ")) #ac source input value
    soak_time = float(input("Enter soak time per LOAD condition in (sec): "))
    soak_line = float(input("Enter soak time per LINE condition in (sec): "))
    
#Equipment initialization
    rm = pyvisa.ResourceManager()
    ac_source = rm.open_resource("GPIB0::5::INSTR")
    eload = rm.open_resource("GPIB0::8::INSTR")
    input_pm = rm.open_resource("GPIB0::20::INSTR")
    output_pm = rm.open_resource("GPIB0::10::INSTR")
    #scope = rm.open_resource("TCPIP::169.254.97.96::INSTR")
##
##    
##    
##    
##
###SCope setting
##    scope.write("C1:TRACE ON") 
##    scope.write("C2:TRACE ON")
##    scope.write("C3:TRACE ON")
##    scope.write("C4:TRACE ON")
##    
##    #scope.write("C1:COUPLING D1M") 
##    #scope.write("C2:COUPLING D1M")
##    scope.write("C3:COUPLING D1M")
##    #cope.write("C4:COUPLING D1M")
##    
##    #scope.write("C1:VOLT_DIV 100")
##    #scope.write("C2:VOLT_DIV 5")
##    scope.write("C3:VOLT_DIV 1")
##    #scope.write("C4:VOLT_DIV 1")
##    
##    #scope.write("C1:OFFSET -100V")
##    #scope.write("C2:OFFSET -15V")
##    scope.write("C3:OFFSET -3V")
##    #scope.write("C4:OFFSET -2V")
##
##    
##    scope.write("TIME_DIV 50mS")
##    scope.write("PARM CUST")
##    scope.write("TRMD AUTO")
####    scope.write("PACU 1,DULEV,C1,POS,50 PCT,500E-3 DIV")
####    scope.write("PACU 2,DULEV,C2,POS,50 PCT,500E-3 DIV")
####    scope.write("PACU 3,DULEV,C3,POS,50 PCT,500E-3 DIV")
##    scope.write("PACU 3,MEAN,C3,OFF")
    
    
    
    
#Power meter settings
    input_pm.write("*RST")
    input_pm.write(":INPUT:VOLTAGE:AUTO ON")
    input_pm.write(":INPUT:CURRENT:AUTO ON")
    input_pm.write(":MEASURE:AVERAGING:TYPE LINEAR")
    input_pm.write(":MEASURE:AVERAGING:COUNT 8")
    input_pm.write(":MEASURE:AVERAGING:STATE ON")
    input_pm.write(":INPUT:MODE RMS")
    input_pm.write(":NUMERIC:FORMAT ASCII")
    input_pm.write(":NUMERIC:NORMAL:ITEM1 U,1")
    input_pm.write(":NUMERIC:NORMAL:ITEM2 I,1")
    input_pm.write(":NUMERIC:NORMAL:ITEM3 P,1")
    input_pm.write(":NUMERIC:NORMAL:ITEM4 LAMBDA,1")
    input_pm.write(":NUMERIC:NORMAL:ITEM5 ITHD,1")

    output_pm.write("*RST")
    output_pm.write(":INPUT:VOLTAGE:AUTO ON")
    output_pm.write(":INPUT:CURRENT:AUTO ON")
    output_pm.write(":MEASURE:AVERAGING:TYPE LINEAR")
    output_pm.write(":MEASURE:AVERAGING:COUNT 8")
    output_pm.write(":MEASURE:AVERAGING:STATE ON")
    output_pm.write(":INPUT:MODE DC")
    output_pm.write(":NUMERIC:FORMAT ASCII")
    output_pm.write(":NUMERIC:NORMAL:ITEM1 U,1")
    output_pm.write(":NUMERIC:NORMAL:ITEM2 I,1")
    output_pm.write(":NUMERIC:NORMAL:ITEM3 P,1")
    output_pm.write(":NUMERIC:NORMAL:ITEM4 LAMBDA,1")

    

#Eload setting
    eload.write("*RST")
    
    #eload.write("CHAN 1")
    #eload.write("CHAN:ACT 0")

    #eload.write("CHAN 7")
    #eload.write("CHAN:ACT 0")

    eload.write("MODE CCH")
    eload.write("CHAN 3")
    eload.write("CHAN:ACT 1")
    eload.write("CURR:STAT:L1 %f" %(load_increment))

#Eload ON
    eload.write("LOAD ON")

    time.sleep(2)

#AC ON
    ac_source.write("OUTP:COUP AC")
    ac_source.write("SOUR:VOLT %f" %(acs))
    ac_source.write("OUTP ON")

    time.sleep(5)

    f = open("ACDC Efficiency.csv", "w")

#Printing of headers
    headers = ["Vin", "Iin", "PF", "Vout", "Iout","Pout","Efficiency","Cmp mean", "THD", "\n"]
    f.write(",".join(headers))
    print ("\n", "============================  START  ============================", "\n")
    print ("Vin", "     Iin", "      PF", "    Vout", "    Iout", "  Pout", "    Eff", "  Cmp_mean", "THD")
    

#Load Increment with Power measurement

    z = [90, 115, 230, 265] #72,90,115,230,265
    # z = [90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 265]
    for x in z:
        Vin=x

        eload.write("LOAD ON")
        
        if Vin > 180:
            ac_source.write("SOUR:FREQ 50")
        else:
            ac_source.write("SOUR:FREQ 60")
            
        ac_source.write("SOUR:VOLT %f" %(Vin))
        time.sleep(2)

        load = full_load

        time.sleep(1)
        eload.write("CURR:STAT:L1 %f" %(load))
        time.sleep(soak_line)
        

        while load > 0:

            eload.write("CURR:STAT:L1 %f" %(load))
            
            load = load - load_increment

            if load <=0:
                load = 0
                eload.write("LOAD OFF")
                

            
    #soak time
            #scope.write("TRMD AUTO")
            #scope.write("CLEAR_SWEEPS")
            time.sleep(soak_time)

            input_pm.write("HOLD ON")
            output_pm.write("HOLD ON")
            input_voltage = float(input_pm.query("NUM:NORM:VAL? 1").strip())
            ####### nan check##########################
            while (1):
                if math.isnan (input_voltage):
                    input_pm.write("HOLD OFF")
                    time.sleep(0.5)
                    input_pm.write("HOLD ON")
                    input_voltage = float(input_pm.query("NUM:NORM:VAL? 1").strip())
                else:
                    break
            ####### nan check##############################               
            input_current = float(input_pm.query("NUM:NORM:VAL? 2").strip())
            pf = float(input_pm.query("NUM:NORM:VAL? 4").strip())
            output_voltage = float(output_pm.query("NUM:NORM:VAL? 1").strip())
           ####### nan check##########################
            while (1):
                if math.isnan (output_voltage):
                    output_pm.write("HOLD OFF")
                    time.sleep(0.5)
                    output_pm.write("HOLD ON")
                    output_voltage = float(output_pm.query("NUM:NORM:VAL? 1").strip())
                else:
                    break
            ####### nan check##############################

            output_current = float(output_pm.query("NUM:NORM:VAL? 2").strip())
            THD = float(input_pm.query("NUM:NORM:VAL? 5").strip())

            #scope.write("TRMD STOP")
            #time.sleep(2)

            #comp = float(scope.query("PARAMETER_STATISTICS? CUST, P3").split("AVG,",1)[1].split(" V")[0])
            comp = 0
            
            
            

    #Formulas:
            pout = output_voltage*output_current
            efficiency = (pout)*100/(input_voltage*input_current*pf)
            
    #printing of measured values
            

            row = [input_voltage, input_current, pf, output_voltage, output_current, pout, efficiency, comp, THD, "\n"]
            row = [str(r) for r in row]
            f.write(",".join(row))
            print ("%.2f" %input_voltage, " |", "%.2f" %input_current," |", "%.2f" %pf,"|", "%.2f" %output_voltage," |", "%.2f" %output_current," |", "%.2f" %pout," |", "%.2f" %efficiency, " |", "%.3f" %comp, " |", "%.2f" %THD) 
            input_pm.write("HOLD OFF")
            output_pm.write("HOLD OFF")

            if load == 0:
                break

#AC source off
    ac_source.write("OUTP OFF")
    eload.write("CURR:STAT:L1 %f" %(full_load))
    time.sleep(5)

    #ac_source.write("*RST")
    input_pm.write("*RST")
    eload.write("*RST")
    output_pm.write("*RST")
    
    ac_source.close()
    eload.close()
    input_pm.close()
    output_pm.close()

    
    f.close()


    print ("\n", "=============================  END  =============================", "\n")


if __name__ == "__main__":
    main()









##    while load < full_load:
##        load = load + load_increment
##        eload.write("CURR:STAT:L1 %s" %(load))
##        time.sleep(2)
        

#    ac_source.write("SOUR:VOLT 0")
##   ac_source.write("SOUR:FREQ 60")
#    
    
#    while acs <= 10:
#        ac_source.write("SOUR:VOLT:OFFset %s" %(acs))
#        acs = acs + 1
#        time.sleep(1)

    
#    print acs
#   time.sleep(2)

import numpy as np
import time

def my_pyvisa():
    # import pyvisa
    # rm = pyvisa.ResourceManager()
    # return rm
    return "pyvisa"

def my_smu(rm):
    # smu = rm.open_resource("GPIB0::10::INSTR")
    # return smu
    smu = {"query": rm}
    return smu

def my_smu_query(smu, start, stop, step):
    # del smu.timeout
    # start_command = f":source:voltage:start {start}"
    # stop_command = f":source:voltage:stop {stop}"
    # step_command = f":source:voltage:step {step}"

    # smu.write(":source:voltage:mode sweep")
    # smu.write(start_command)
    # smu.write(stop_command)
    # smu.write(step_command)      
    # # smu.write(":source:voltage:start 0")
    # # smu.write(":source:voltage:stop 2.0")
    # # smu.write(":source:voltage:step 0.01")
    # smu.write(":source:sweep:cabort never")
    # smu.write(":source:sweep:ranging auto")
    # smu.write(f":TRIG:COUN {smu.query(':SOUR:SWE:POIN?')}")
    # smu.write(":SOUR:DEL:auto on")
    #return this string
    smu["start"] = start
    smu["stop"] = stop
    smu["step"] = step
    smu["test"] = "test"
    return smu

#----------------------------------------------------------------#

def my_tec(rm):
    # tec = rm.open_resource("ASRL3::INSTR")
    # return tec
    tec = {"query": "tec!"}
    return tec

def my_acquire_current(thread, update_label, extra_param):  
    [button_name, temp_list, minutes, threshold, tec, smu, append_data] = extra_param
    currents = []
    for temp in temp_list:
        if not thread.running:  # Check if the loop should stop
            break
        # command = "TEC:T " + str(temp)
        # tec.write(command)
        # tec.write("TEC:OUT 1")
        
        N = 60 * minutes

        for i in range(N):
            if not thread.running:  # Check if the loop should stop
                break
            #current = float(smu.query(":read?").split(",")[1])
            current = np.random.rand()  # Generate one random value
            append_data(button_name, current)
            currents.append(current)          
              
            if current > threshold:             
                # smu.write(':OUTP OFF')
                my_str = f"set temp = {temp}; Avalanch happened!"
                update_label(button_name, my_str)
                break
            if i % 60 == 0:              
                my_str = f"set temp = {temp}; {i / 60} min"
                update_label(button_name, my_str)              
            time.sleep(1)      
    return currents

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

def my_search(thread, update_label, extra_param):
    [button_name, minutes, V_search, current_thres, filter_num, tec, smu, append_data] = extra_param
    N = 60 * minutes
    V_maxLimit_found = False
    while V_maxLimit_found is False:
        if not thread.running:  # Check if the loop should stop
            break
        # smu.write(':OUTP OFF')
        # command = ":source:voltage:level " + str(round(V_search, 2))
        # smu.write(command)
        # smu.write(':OUTP ON')
        currents = []
        drift_test_complete = True
        for i in range(N):
            if not thread.running:  # Check if the loop should stop
                break
            #current = float(smu.query(":read?").split(",")[1])
            current = i#np.random.rand()  # Generate one random value
            currents.append(current)
            print(current)
            append_data(button_name, current)
            if current >= current_thres:
                #smu.write(':OUTP OFF')
                my_str = 'Avalanch happened at V = '+ str(round(V_search, 2))
                update_label(button_name, my_str)  
                V_search = V_search - 0.01
                drift_test_complete = False
                break
            if i % 60 == 0:
                my_str = f"{i / 60} min at current = {current}"
                update_label(button_name, my_str) 
            time.sleep(1)
        if drift_test_complete is True:
            V_maxLimit_found = True
            #smu.write(':OUTP OFF')

    avg_currents = moving_average(np.array(currents), filter_num)
    return avg_currents
    # print(currents)
    
def my_continuous(thread, update_label, extra_param):
    [button_name, minutes, V_search, tec, smu, append_data] = extra_param
    N = 60 * minutes
    #smu.write(f":source:voltage:level {V_search}")
    #smu.write(':OUTP ON')
    currents = []
    for i in range(N):
        if not thread.running:  # Check if the loop should stop
            break
        #current = float(smu.query(":read?").split(",")[1])
        current = i#np.random.rand()  # Generate one random value
        currents.append(current)
        append_data(button_name, current)
        print(current)
        if current > 0.01:
            #smu.write(':OUTP OFF')
            my_str = 'Avalanch happened '
            update_label(button_name, my_str)
            break
        if i % 60 == 0:
            my_str = f"{i / 60} min at current = {current}"
            update_label(button_name, my_str) 
        time.sleep(1)
    #smu.write(':OUTP OFF')
    return currents
    
def my_switch(thread, update_label, extra_param):
    [button_name, N, V_search, filter_num, tec, smu, append_data] = extra_param
    #smu.write(':OUTP OFF')
    #smu.write(f":source:voltage:level {V_search}")
    #smu.write(':OUTP ON')
    currents = []
    for i in range(N):
        if not thread.running:  # Check if the loop should stop
            break
        #current = float(smu.query(":read?").split(",")[1])
        current = i#np.random.rand()
        currents.append(current)
        append_data(button_name, current)
        my_str = f"{i / 60} min at current = {current}"
        update_label(button_name, my_str) 
        time.sleep(0.1)
    #smu.write(':OUTP OFF')

    avg_currents = moving_average(np.array(currents), filter_num)
    return avg_currents

def my_close(rm, smu):
    # smu.close()
    # rm.close()
    return "closed"
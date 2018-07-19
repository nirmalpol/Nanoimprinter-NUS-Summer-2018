'''
    ********************************************************************************************
    *   FILE NAME:      controller.py
    *   AUTHOR:         Yu Dong (Peter) Feng, Dylan Vogel
    *   PURPOSE:        This file contains the code for setting up the center and edge PID values
    *********************************************************************************************
'''
# User functions
import PID

def pid_setup_center(work_temp, P, I, D): #change

    # Written as (Kp, Ki, Kd)
    pid_center = PID.PID(P, I, D)

    # Windup to prevent integral term from going too high/low.
    pid_center.setWindup(1)

    # Sample time, pretty self-explanatory.
    pid_center.setSampleTime(0.5)
    pid_center.SetPoint = work_temp

    return pid_center

def pid_setup_edge(work_temp, P, I, D): #change

    pid_edge = PID.PID(P, I, D)
    pid_edge.setWindup(1)
    pid_edge.setSampleTime(0.5)
    pid_edge.SetPoint = work_temp

    return pid_edge
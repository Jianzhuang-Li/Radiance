#!/bin/bash

dctimestep -h vmx/room2windows_window_east.vmx rad_files/xml/type25_anglenull.xml \
    dmx/room2windows_east.dmx rad_files/skv/temp.skv > results/room2windows_east.dat
echo "\n"
dctimestep -h vmx/room2windows_window_south.vmx rad_files/xml/type25_anglenull.xml \
    dmx/room2windows_south.dmx rad_files/skv/temp.skv > results/room2windows_south.dat

# rlam '!dctimestep vmx/room2windows_window_east.vmx rad_files/xml/type25_anglenull.xml \
#     dmx/room2windows_east.dmx rad_files/skv/temp.skv' \
#     '!dctimestep vmx/room2windows_window_south.vmx rad_files/xml/type25_anglenull.xml \
#     dmx/room2windows_south.dmx rad_files/skv/temp.skv' | \
#     rcalc -e '$1=179*(($1+$4)*0.265+($2+$5)*0.670+($3+$6)*0.065)' \
#     > results/illum_052113_clear-clear.dat
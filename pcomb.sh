#!/bin/bash
dctimestep -oc vmx/room2windows_window_east_%03d.hdr rad_files/xml/type25_angle60.xml \
	dmx/room2windows_east.dmx skies/5_21_07.skv > images/room2windows_east.hdr

dctimestep -oc vmx/room2windows_window_south_%03d.hdr rad_files/xml/type25_angle60.xml \
    dmx/room2windows_south.dmx skies/5_21_07.skv > images/room2windows_south.hdr

pcomb '!dctimestep vmx/room2windows_window_east_%03d.hdr rad_files/xml/type25_angle90.xml \
	dmx/room2windows_east.dmx skies/5_21_07.skv' \
	'!dctimestep vmx/room2windows_window_south_%03d.hdr rad_files/xml/type25_angle90.xml \
        dmx/room2windows_south.dmx skies/5_21_07.skv' \
	> images/room2window.hdr

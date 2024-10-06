#!/bin/bash
genklemsamp -vd 0 -1 0 objects/room2windows_south_window.rad | \
    rcontrib -c 1000 -e MF:4 -f reinhart.cal -b rbin -bn Nrbins -m sky_glow \
    -faf octrees/room2windows_dmx.oct > dmx/room2windows_south.dmx

genklemsamp -vd 1 0 0 objects/room2windows_east_window.rad | \
    rcontrib -c 1000 -e MF:4 -f reinhart.cal -b rbin -bn Nrbins -m sky_glow \
    -faf  octrees/room2windows_dmx.oct > dmx/room2windows_east.dmx

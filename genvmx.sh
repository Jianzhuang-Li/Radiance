#!/bin/bash
rcontrib -f klems_full.cal -bn Nkbins -fo -o vmx/room2windows_%s.vmx \
	-b kbinS -m window_south \
	-b kbinE -m window_east \
	-I+ -ab 12 -as 50000 -lw 2e-5 octrees/room2windows_vmx.oct < photocells/room2windows.pts


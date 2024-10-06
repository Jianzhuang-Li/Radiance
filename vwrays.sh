#!/bin/bash 
vwrays -ff -vf views/nice.vf -x 600 -y 600 | \
	rcontrib `vwrays -vf views/nice.vf -x 600 -y 600 -d` -ffc -fo -o vmx/room2windows_%s_%03d.hdr \
	-f klems_full.cal -bn Nkbins	\
	-b kbinS -m window_south \
	-b kbinE -m window_east \
	-ab 12 -ad 50000 -lw 2e-5 octrees/room2windows_vmx.oct

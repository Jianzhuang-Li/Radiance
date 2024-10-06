#!/bin/bash
pcond images/room2window.hdr | \
    pcompos -a 2 -'!falsecolor -s 2000 -log 2 -i images/room2window.hdr' | \
    ra_tiff -z - images/room2window.tif

pcond images/room2windows_south.hdr | \
    pcompos -a 2 -'!falsecolor -s 2000 -log 2 -i images/room2windows_south.hdr' | \
    ra_tiff -z - images/room2windows_south.tif
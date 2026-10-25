#!/bin/sh
# Render shiba_short_preview.mp4 from the master clip, freeze frame and caption PNGs.
# Run from the dog-short directory.
T=media/telop
ffmpeg -y -i media/shiba_bed_vertical_master.mp4 -loop 1 -framerate 60 -t 2 -i media/endcard_freeze.png \
 -framerate 60 -loop 1 -i $T/telop_00_header.png -framerate 60 -loop 1 -i $T/telop_01.png \
 -framerate 60 -loop 1 -i $T/telop_02.png -framerate 60 -loop 1 -i $T/telop_03.png \
 -framerate 60 -loop 1 -i $T/telop_04.png -framerate 60 -loop 1 -i $T/telop_05.png \
 -framerate 60 -loop 1 -i $T/telop_06.png -framerate 60 -loop 1 -i $T/telop_99_endcard.png \
 -filter_complex "[1:v]format=yuv420p,setsar=1[fz];[0:v][fz]concat=n=2:v=1:a=0,format=yuva420p[base];\
[base][2:v]overlay=enable='lt(t,11.515)':shortest=1[h];\
[h][3:v]overlay=enable='lt(t,2.5)':shortest=1[a1];[a1][4:v]overlay=enable='between(t,2.5,4.999)':shortest=1[a2];\
[a2][5:v]overlay=enable='between(t,5,7.499)':shortest=1[a3];[a3][6:v]overlay=enable='between(t,7.5,9.599)':shortest=1[a4];\
[a4][7:v]overlay=enable='between(t,9.6,10.599)':shortest=1[a5];[a5][8:v]overlay=enable='between(t,10.6,11.515)':shortest=1[a6];\
[a6][9:v]overlay=enable='gte(t,11.516)':shortest=1,format=yuv420p[v];[0:a]apad=whole_dur=13.5[a]" \
 -map "[v]" -map "[a]" -t 13.5 -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -r 60 \
 -c:a aac -b:a 192k -movflags +faststart shiba_short_preview.mp4

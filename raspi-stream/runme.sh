#! /bin/bash

i=0
while outfile=$(printf output%04i.flv $i) ; [ -e $outfile ] ; do
    let i++
done

set -ex

FFMPEG=${FFMPEG:-ffmpeg}
KEY=$(cat key)
SERVER=$(cat server)

./raspi-stream/ENV/bin/python raspi-stream/inputs.py "${SERVER}?${KEY}" | $FFMPEG -ar 22050 -ac 1 -thread_queue_size 2048 -f alsa -i hw:1,0 -r 30 -thread_queue_size 2048 -f h264 -i - -vcodec copy -acodec libmp3lame -ar 22050 -ac 1 -b:a 32k -g 60 -bufsize 600k -f tee -map 1:v -map 0:a "$outfile|[f=flv]rtmp://a.rtmp.youtube.com/live2/${KEY}"

#! /bin/bash

FFMPEG=${FFMPEG:-ffmpeg}
KEY=$(cat key)
SERVER=$(cat server)

i=0
while outfile=$(printf output%04i.avi $i) ; [ -e $outfile ] ; do
    let i++
done

python raspi-stream/inputs.py "${SERVER}?${KEY}" | $FFMPEG -f lavfi -i anullsrc -f h264 -i - -vcodec copy -acodec libmp3lame -ar 22050 -ac 1 -ab 32k -g 60 -f tee -map 1:v -map 0:a "$outfile|[f=flv]rtmp://a.rtmp.youtube.com/live2/${KEY}"

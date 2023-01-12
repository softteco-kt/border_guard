echo HOME=$(pwd)
echo URL="https://frame.pkpd.lt/lt/border/stream/checkpoint.sumskas/video.sumskas"
echo "*/20 * * * * $(which python3) $(pwd)/main.py >> $(pwd)/logs.log 2>&1"

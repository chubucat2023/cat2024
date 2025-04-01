import DF_15RSMG
import eye
import time

eye.init()
DF_15RSMG.init_servo()
time.sleep(1)
DF_15RSMG.forward()
# ここに超音波センサーでの距離測定による終了タイミングをディレイ
while True:
    distance = eye.main()
    if distance < 20:
        break
    time.sleep(0.05)
DF_15RSMG.stop()

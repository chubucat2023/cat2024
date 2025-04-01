import DF_15RSMG
import time


def init_servo():
    DF_15RSMG.init_servo()


def forward(t):
    DF_15RSMG.forward()
    time.sleep(t)
    DF_15RSMG.stop()


def turn_R(t):
    DF_15RSMG.turn_R()
    time.sleep(t)
    DF_15RSMG.stop()


def turn_L(t):
    DF_15RSMG.turn_L()
    time.sleep(t)
    DF_15RSMG.stop()


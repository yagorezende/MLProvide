from fuzzy.fls import FLSAction
import socket

CLIENT1_BW = 6 * 1000000        # bps
#CLIENT2_BW = 4000000000        # bps

#CLIENT3_BW = 5000000000        # bps
BW_STEP = 1 * 1000000
MAX_SERVER_LOAD = 70 * 1000000   # bps
STEP = 1                   # seconds

# Agent settings

SERVER_IP = 'localhost'
RYU_IP = 'localhost'

ALPHA = 0.3
LOCK_MODE = True
LOCK_ALPHA = 0.1
GAMMA = 1
EPSILON = 0.15
REPEAT_COUNT = 0
STATES = 26                 # Estados USADOS 5
ACTIONS = 2
MAIN_FILE = "/tmp/general_client_fql.txt"

LOG_LEVEL = "INFO"
PARALLEL = True
LOOP = 50  # 200

# POMDP Settings
POMDP = False               # Medir o tráfego da nuvem com processamento
INTERCALATE = False         # Intercalar entre MDP e POMDP
L_CONTROL = True
CORRECTION_RATE = 3

Q_INDEXES = dict(
    q_step={
        "CT": {'eep': 17, 'softmax': 6},
        "VT": {'eep': 17, 'softmax': 6}
    },
    sarsa_step={
        "CT": {'eep': 6, 'softmax': 6},
        "VT": {'eep': 17, 'softmax': 6}
    },
    fql_step={
        "CT": {'eep': 8, 'softmax': 9},
        "VT": {'eep': 8, 'softmax': 9}
    },
    fsl_step={
        "CT": {'eep': 8, 'softmax': 9},
        "VT": {'eep': 8, 'softmax': 9}
    },
    fuzzy_step={
        "CT": {'eep': 8, 'softmax': 9},
        "VT": {'eep': 8, 'softmax': 9}
    },
)

STRATEGY = 'fuzzy_step'  # fuzzy_step, fql_step, fsl_step, q_step,sarsa_step
TRAFFIC = "VT"
EXPLORATION = 'softmax'  # eep, softmax
TEMPERATURE = 1
STATE_FILE = f"results-states/states-{STRATEGY}"
#Q_TABLE_INDEX = Q_INDEXES[STRATEGY][TRAFFIC][EXPLORATION]
Q_TABLE_INDEX = False
Q_TABLE_UPDATE_EVERYSTEP = True
TEST_STATES_RANGE = False#range(3, 50)
ROOT_PATH = ""
OUTPUT_PATH = ROOT_PATH + "outputs/"
DATASETS_PATH = ROOT_PATH + "datasets/"

# Diff
if bool(STRATEGY.count("fuzzy")):
    STATE_TYPE = 'fuzzy'
else:
    STATE_TYPE = 'val' # val, diff

#fuzzy controller
FUZZY = bool(STRATEGY.count("fuzzy"))


FLS = FLSAction()

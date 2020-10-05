from .fls import FLSAction
import socket

CLIENT1_BW = 6000000        # bps
CLIENT2_BW = 4000000000        # bps
CLIENT3_BW = 5000000000        # bps
MAX_SERVER_LOAD = 70000000   # bps
STEP = 1                   # seconds

# Agent settings

if socket.gethostname() == 'EX-MACHINA':
    SERVER_IP = '172.16.100.18'
    RYU_IP = '127.0.0.1'
else:
    SERVER_IP = '172.17.10.102'
    RYU_IP = '172.17.10.102'
ALPHA = 0.3
LOCK_MODE = True
LOCK_ALPHA = 0.1
GAMMA = 1
EPSILON = 0.15
REPEAT_COUNT = 0
STATES = 5                 # Estados USADOS 5
ACTIONS = 4                # x2 + 1  USADAS 4
MAIN_FILE = "general_client_fql.txt"
STATE_FILE = "results-states_fql/states"
LOG_LEVEL = "INFO"
PARALLEL = True
LOOP = 200

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

STRATEGY = 'sarsa_step'  # fuzzy_step, fql_step, fsl_step, q_step,sarsa_step
TRAFFIC = "VT"
EXPLORATION = 'eep'  # eep, softmax
TEMPERATURE = 1
#Q_TABLE_INDEX = Q_INDEXES[STRATEGY][TRAFFIC][EXPLORATION]
Q_TABLE_INDEX = 1
Q_TABLE_UPDATE_EVERYSTEP = True
TEST_STATES_RANGE = range(5, 50)



# Diff
if bool(STRATEGY.count("fuzzy")):
    STATE_TYPE = 'fuzzy'
else:
    STATE_TYPE = 'val' # val, diff

#fuzzy controller
FUZZY = bool(STRATEGY.count("fuzzy"))


FLS = FLSAction()

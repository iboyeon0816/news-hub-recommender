import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

YAML_FILE = os.path.join(DATA_DIR, 'utils', 'lstur.yaml')
WORD_EMB_FILE = os.path.join(DATA_DIR, 'utils', 'embedding.npy')
WORD_DICT_FILE = os.path.join(DATA_DIR, 'utils', 'word_dict.pkl')
USER_DICT_FILE = os.path.join(DATA_DIR, 'utils', 'uid2index.pkl')
WEIGHTS_PATH = os.path.join(DATA_DIR, 'model', 'lstur_ckpt')
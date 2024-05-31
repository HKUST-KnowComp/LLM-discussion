from rules.algo import MessageSync
from bots.botsUtils import TurboBehaviors, PaLMBehaviors
from bots.turbo35.turbo import Turbo35Bot
from bots.palm2.palm import PaLMBot
from utils.utils import rule, conf_logger
import traceback
import threading
import json
import os
receiver_bots_map = {
    chr(ord('A')+i): TurboBehaviors() for i in range(26)
}
# receiver_bots_map = {
#     "A": PaLMBehaviors(),
#     "B": PaLMBehaviors(),
#     "C": PaLMBehaviors(),
# }
def palm_thread():
    LLM = PaLMBot()
    LLM.run()
def turbo_thread():
    LLM = Turbo35Bot()
    LLM.run()
def message_sync_thread():
    try:
        algo = MessageSync(receiver_bots_map)
        algo.launchMessageSync()
    except Exception as e:
        print(e)
        traceback.print_exc()
        exit(0)
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", type=int, help="index of data to access", default=None)
    args = parser.parse_args()
    data_name = ""
    data_path = os.path.join(os.getcwd(), "test.jsonl")
    with open(data_path, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]
    data = data[:100]
    i = args.i
    assert(i is not None), "Please specify the index of data to access"
    dpt = data[i]
    rule.set_premises_proposition(dpt, i) 
    rule.current_info["log"] = conf_logger.dir_name
    turbo_thread = threading.Thread(target=turbo_thread)
    # palm_thread = threading.Thread(target=palm_thread)
    message_sync_thread = threading.Thread(target=message_sync_thread)
    turbo_thread.start()
    # palm_thread.start()
    message_sync_thread.start()
    turbo_thread.join()
    # palm_thread.join()
    message_sync_thread.join()
    print("end")
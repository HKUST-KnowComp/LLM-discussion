from logger.logger import Logger
import threading
from rules.Debate.DebateRule import DebateRule
from rules.GroupDiscussionV1.GroupRule import GroupRule as GroupRuleV1
from rules.GroupDiscussionV2.GroupRule import GroupRule as GroupRuleV2
from rules.GroupDiscussionV3.GroupRule import GroupRule as GroupRuleV3
import queue

event_scheduler = threading.Event()
event_chatgpt35_turbo = threading.Event()
event_palm = threading.Event()
event_exception = threading.Event()

global_message_queue = queue.Queue()
global_return_message_queue = queue.Queue()

# premises = '''["Bernarda Bryson Shahn was a painter and lithographer.", "Bernarda Bryson Shahn was born in Athens, Ohio. ", "Bernarda Bryson Shahn was married to Ben Shahn.", "People born in Athens, Ohio are Americans."]'''
# proposition = '''"Bernarda Bryson Shahn was American."'''
conf_logger = Logger()
# rule = DebateRule(2)
# rule = GroupRuleV1(premises, proposition, 3)
# rule = GroupRuleV2(3)
rule = GroupRuleV3(6, True)

silence_str = '''=[silence]='''

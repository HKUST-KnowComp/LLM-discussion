import random
import queue
from utils.message import Message, UpcomingMessage
from utils.person import Participant
from utils.utils import rule, silence_str, event_exception, conf_logger
from bots.botsUtils import TurboBehaviors, PaLMBehaviors
random.seed(42)


messageQ = queue.Queue()
sendQ = queue.Queue()
class peekQueue:
    def __init__(self, queue) -> None:
        self.queue = queue
    def peek(self):
        if not self.queue:
            return None
        return self.queue[0]
    
class MessageSync:
    def __init__(self, receiver_bots_map):
        self.rule = rule
        self.receiver_bots_map = receiver_bots_map
        self.participants = self.rule.participants
        if not hasattr(self.rule, "getReceivers"):
            self.discussion_scope_map = self.rule.discussion_scope_map
        self.init = True
        self.current_bot = None
        self.isOver = False
        self.temp = 0
    def __push_silence(
        self, 
        depth:int
    ):
        '''
        When it is allowed to remain silent for a certain round in your designed rule,
        you can customize this function to do your own logic by pushing silence message
        to specific agents.
        '''
        ...
    def __editMessage(
        self,
        content: str,
        receiver_name: str,
    ):
        bot = self.receiver_bots_map[receiver_name]
        return bot.edit_input(content)
    def __regenOuput(
        self,
        receiver_name: str,
    ) -> str:
        bot = self.receiver_bots_map[receiver_name]
        return bot.regen()
    def __sendMessage(
        self,
        content: str,
        receiver_name: str,
        depth: int,
    ) -> str:
        bot = self.receiver_bots_map[receiver_name]
        maintain_silence = False
        if hasattr(self.rule, "maintainSilence"):
            maintain_silence = self.rule.maintainSilence(receiver_name, content, depth)
        if maintain_silence:
            content = silence_str + '\n' + content
        if 0 == depth:
            if isinstance(bot, TurboBehaviors):
                system_prompt = self.rule.getSystemPrompt(receiver_name)
                bot.new_session(name=receiver_name, system_content=system_prompt)
            elif isinstance(bot, PaLMBehaviors):
                system_prompt = self.rule.getSystemPrompt(receiver_name)
                bot.new_session(name=receiver_name, system_content=system_prompt)
            else:
                bot.new_session()
            output = bot.impose_input(content)
            bot.set_title(receiver_name)
            return output
        else:
            bot.switch_role(receiver_name)
            return bot.impose_input(content)
    def __done(self):
        bot = self.receiver_bots_map[self.current_bot]
        bot.done()

    def __init_messageQ(
        self,
        messags: list[Message],
    ):
        for message in messags:
            messageQ.put(message)            
    
    def __process_common_messages(
        self,
        depth: int,
        messageMap: dict[Participant, list[Message]],
        current_speakers: list[str],
    ):
        # print("##################Output MessageMap Info Start##################")
        # for person, messages in messageMap.items():
        #     print(f"person: {person.name}")
        #     for message in messages:
        #         print(f"\tmessage: {message.message_content}")
        # print("##################Output MessageMap Info End##################")
        isHoldList = []
        for person, messages in messageMap.items():
            isHold = False
            if len(messages) != 0:
                if person.name in current_speakers and hasattr(self.rule, "isHold"):
                    isHold = self.rule.isHold(person, messages)
                if not isHold:
                    if hasattr(self.rule, "mergeCommonMessage"):
                        merged_message = self.rule.mergeCommonMessage(person.name, depth, messages)
                    else:
                        messages2merge = [message.message_content for message in messages]
                        random.shuffle(messages2merge)
                        merged_message = "\n".join(messages2merge)
                    # print("merged_message:", merged_message)
                    if hasattr(self.rule, "insertSecretary"):
                        isInsert = False
                        isInsert, new_input = self.rule.insertSecretary(person.name, merged_message, depth)
                        if isInsert:
                            bot = self.receiver_bots_map[person.name]
                            if isinstance(bot, TurboBehaviors):
                                bot.new_session(name=person.name, system_content=merged_message)
                            merged_message = new_input
                    upcoming_message = UpcomingMessage(
                        message_content=merged_message,
                        receiver=person,
                        depth=depth,
                        hold=False
                    )
                    sendQ.put(upcoming_message)
                else:
                    isHoldList.append((person, messages))
        for person, messages in isHoldList:
            if hasattr(self.rule, "mergeCommonMessage"):
                merged_message = self.rule.mergeCommonMessage(person.name, depth, messages)
            else:
                messages2merge = [message.message_content for message in messages]
                random.shuffle(messages2merge)
                merged_message = "\n".join(messages2merge)
            upcoming_message = UpcomingMessage(
                message_content=merged_message,
                receiver=person,
                depth=depth,
                hold=True
            )
            sendQ.put(upcoming_message)
    def __get_receivers(
        self,
        sender_name,
        depth
    ) -> set[Participant]:
        if hasattr(self.rule, "getReceivers"):
            return self.rule.getReceivers(sender_name, depth)
        else:
            return {person for person in self.discussion_scope_map[sender_name]}
    def __process_output(
        self,
        input: str,
        output: str,
        receiver_name: str,
        depth: int
    ):
        validateCode, processed_output = self.rule.processOutputMessage(input, output, receiver_name)
        if validateCode == 0:
            self.isOver = self.rule.isOver
            return processed_output
        else:
            new_input = self.rule.dealAbnormaly(validateCode, input, output, receiver_name)
            output = self.__sendMessage(new_input, receiver_name, depth)
            return self.__process_output(new_input, output, receiver_name, depth)
        
    def __run(self):
        self.current_bot = self.rule.firstSpeaker
        depth = 0
        self.isOver = False
        if hasattr(self.rule, "isOver"):
            self.isOver = self.rule.isOver
        while not messageQ.empty() or not self.isOver:
            if messageQ.empty():
                self.__push_silence(depth)
                continue
            if True == self.init:
                message = peekQueue(messageQ.queue).peek()
                if message.depth == 0:
                    message = messageQ.get()
                    upcoming_message = UpcomingMessage(
                        message_content=message.message_content,
                        receiver=message.sender,
                        depth=0,
                        hold=False
                    )
                    sendQ.put(upcoming_message)
                else:
                    self.init = False
            else:
                peek_message = peekQueue(messageQ.queue).peek()
                depth = peek_message.depth if peek_message else depth
                current_depth_messages = [messageQ.get()]
                while not messageQ.empty():
                    peek_message = peekQueue(messageQ.queue).peek()
                    if peek_message.depth == depth:
                        current_depth_messages.append(messageQ.get())
                    else:
                        break
                # participant A will receive messages from participants Bs
                # in this round, the information is stored in the A_receive_messages_from_Bs_map
                sorted_participants = sorted(self.participants, key=lambda x: x.name)
                A_receive_messages_from_Bs_map = {person: [] for person in sorted_participants}
                for message in current_depth_messages:
                    for receiver in message.receivers:
                        A_receive_messages_from_Bs_map[receiver].append(message)
                current_speakers = [message.sender.name for message in current_depth_messages]
                self.__process_common_messages(depth, A_receive_messages_from_Bs_map, current_speakers)
            
            result = peekQueue(sendQ.queue).peek()
            if result is not None:
                next_depth = result.depth+2 if result.hold else result.depth+1
                is_first_hold = result.hold
                hold_messages = {}
                while ((result and result.depth <= next_depth-1 and result.hold | is_first_hold == False)
                    or (result and result.depth <= next_depth-1 and is_first_hold)):
                    if result.hold:
                        hold_messages[result.receiver.name] = sendQ.get().message_content
                    else:
                        result = sendQ.get()
                        receiver_name = result.receiver.name
                        self.current_bot = receiver_name
                        raw_input_messages = []
                        if receiver_name in hold_messages:
                            raw_input_messages.append(hold_messages[receiver_name])
                            del hold_messages[receiver_name]
                        raw_input_messages.append(result.message_content)
                        input_message = self.rule.modifyRawInputMessage(raw_input_messages)
                        output = self.__sendMessage(input_message, receiver_name, result.depth)
                        processed_output = self.__process_output(input_message, output, receiver_name, result.depth)
                        receivers = self.__get_receivers(receiver_name, next_depth) # 注意这里的depth，研究一下是next_depth还是result.depth
                        if processed_output != "":
                            #logger field
                            conf_logger.updateSpeaker(receiver_name)
                            conf_logger.log(input_message, processed_output)
                            conf_logger.save()
                            if receivers.__len__() != 0:
                                message = Message(
                                    message_content=processed_output,
                                    sender=result.receiver,
                                    receivers=receivers,
                                    depth=next_depth
                                )
                                messageQ.put(message)
                    result = peekQueue(sendQ.queue).peek()
                    if is_first_hold and result and result.hold == False:
                        is_first_hold = False
                    if self.isOver:
                        self.__done()
                        raise Exception("Discussion Over")
    
    def launchMessageSync(self):
        try:
            self.__init_messageQ(self.rule.initMessage())
            self.__run()
        except Exception as e:
            print(e)
            print("Discussion Over")
            import traceback
            traceback.print_exc()
            event_exception.clear()
            event_exception.set()

            
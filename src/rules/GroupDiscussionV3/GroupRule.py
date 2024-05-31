import os
import json
from utils.person import Participant
from utils.message import Message
from rules.GroupDiscussionV3.GroupPrompt import *
class GroupRule:
    def __init__(self, num_participants, use_secretary=False) -> None:
        assert num_participants % 3 == 0, "Number of participants must be a multiple of 3."
        assert num_participants == 3 or num_participants == 6 or num_participants == 9 or num_participants == 12 or num_participants == 18 or num_participants == 24, "Number of participants must be 3, 6, 9, 12, 18 or 24."
        assert num_participants <=25, "Number of participants must be less than 25."
        self.num_participants = num_participants
        self.participants_list = [Participant(chr(ord('A') + i)) for i in range(num_participants)]
        self.use_secretary = use_secretary
        self.current_speaking_num = self.num_participants
        self.hybrid = False # You can customize hybrid mode here
        self.secretary_name = ''
        if use_secretary:
            self.participants_list.append(Participant(chr(ord('A')+num_participants)))
            self.secretary_name = chr(ord('A')+num_participants)
        self.participants = {person for person in self.participants_list}
        self.current_level = 0
        self.level_shift = False
        self.groupNum = self.num_participants // 3
        self.groupMap = [{
                    i+1:[chr(ord('A')+i*3+j) for j in range(3)] for i in range(self.groupNum)
                }]
        self.wrongIter = 0
        if self.hybrid:
            ...
        else:
            if use_secretary:
                self.maxLevel = 1
                self.discussion_scope_map = [{
                    chr(ord('A')+i): [person for person in self.participants if person.name != chr(ord('A')+i) and person.name != chr(ord('A')+num_participants) ] for i in range(num_participants)
                }]
            else:
                self.discussion_scope_map = []
                self.discussion_scope_map.append({
                    chr(ord('A')+i): [person for person in self.participants if person.name != chr(ord('A')+i) ] for i in range(num_participants)
                })
                if self.num_participants == 6:
                    ...
                elif self.num_participants == 9:
                    ...
                elif self.num_participants == 12:
                    self.maxLevel = 2
                    self.groupMap.append({
                        1: ['A', 'E'],
                        2: ['I', 'K']
                    })
                    self.groupMap.append({
                        1: ['A', 'I']
                    })
                    self.discussion_scope_map.append({
                        'A': [person for person in self.participants if person.name == 'E' or person.name == 'I' or person.name == 'K'],
                        'E': [person for person in self.participants if person.name == 'A' or person.name == 'I' or person.name == 'K'],
                        'I': [person for person in self.participants if person.name == 'A' or person.name == 'E' or person.name == 'K'],
                        'K': [person for person in self.participants if person.name == 'A' or person.name == 'E' or person.name == 'I'],
                    })
                    self.discussion_scope_map.append({
                        'A': [person for person in self.participants if person.name == 'I'],
                        'I': [person for person in self.participants if person.name == 'A'],
                    })
                elif self.num_participants == 18:
                    ...
                elif self.num_participants == 24:
                    ...
        self.firstSpeaker = "A"
        self.isOver = False
        self.UserQuestionPrompt = UserQuestionPrompt
        self.MiddleSystem = MiddleSystem
        self.UserUpdatePrompt = UserUpdatePrompt
        self.maxRound = 3
        self.currentCount = 0
        self.isTie = False
        self.finalAnswerMap = [{
        }]*4
        self.current_info = {}
        self.save_file_name = "gsm8k.jsonl"
        self.save_file_path = os.path.join(os.getcwd(), "resultLog", self.save_file_name)
        # print(f"Max level: {self.maxLevel}")

    def printInit(self):
        print(f"Number of participants: {self.num_participants}")
        print(f"Use secretary: {self.use_secretary}")
        # print(f"Participants: {self.participants}")
        for person in self.participants_list:
            print(f"Participant {person.name}: {person}")
        print(f"len(participants): {len(self.participants)}")
        print(f"Current level: {self.current_level}")
        # print(f"Discussion scope map: {self.discussion_scope_map}")
        print(f"max level: {self.maxLevel}")
        for i in range(self.maxLevel+1):
            for name, persons in self.discussion_scope_map[i].items():
                print(f"Discussion scope map {name}: ", end='')
                for person in persons:
                    print(f"{person.name} ", end=' ')
                print()
        print(f"First speaker: {self.firstSpeaker}")
        print(f"Is over: {self.isOver}")
        # print(f"User question prompt: {self.UserQuestionPrompt}")
        # print(f"Middle system: {self.MiddleSystem}")
        # print(f"User update prompt: {self.UserUpdatePrompt}")
        print(f"Max round: {self.maxRound}")
        print(f"Current count: {self.currentCount}")
        print(f"Group number: {self.groupNum}")
        print(f"Is tie: {self.isTie}")
        print(f"Final answer map: {self.finalAnswerMap}")
        print(f"Group map: {self.groupMap}")
        print(f"Current info: {self.current_info}")
        print(f"Save file path: {self.save_file_path}")
    def set_premises_proposition(
        self,
        datacase: dict,
        id: int
    ):
        import re
        data = {}
        answer = re.sub(r"[^0-9.]", "", datacase["answer"].split("#### ")[1].strip())
        exp = re.sub('<<.*>>', '', datacase["answer"].split("#### ")[0].replace("\n\n", "\n").strip())
        exp_sents = exp.split("\n")
        exp_sents = [gold_explanation_sent + "." if gold_explanation_sent[-1] != "." else gold_explanation_sent for gold_explanation_sent in exp_sents]
        exp = " ".join(exp_sents)
        data["question"]  = datacase['question']
        data["answer"] = answer
        self.current_info = {}
        self.current_info['id'] = id
        self.current_info['question'] = data['question']
        self.current_info['label'] = data['answer']
        self.current_info['voteMap'] = []
        self.UserQuestionPrompt = self.UserQuestionPrompt.replace("<question>", data['question'])
    def filterAnswer(
        self,
        content: str,
    ) -> str:
        # filter the json part \{*\} from the content and update content with the first element of this part
        import re
        match = re.search(r"\{.*\}", content)
        if match == None:
            matches = re.findall(r"-?\d+(\.\d+)?", content)
            if matches:
                return matches[-1]
            else:
                return "Error"
        content = match.group()
        p1 = content.find("\"reasons\": \"")
        p2 = content.find("\"answer\": \"")
        content = content[:p1+12] + content[p1+12:p2-3].replace('"', '') + content[p2-3:]
        try:
            data = json.loads(content)
            return data['answer']
        except:
            try:
                p2 = content.find("\"answer\": \"")
                if p2 == -1:
                    raise Exception("No answer found.")
                answer = content[p2+11:-2]
                return answer
            except:
                matches = re.findall(r"-?\d+(\.\d+)?", content)
                if matches:
                    return matches[-1]
                return "Error"
    def processOutputMessage(
        self,
        input_content: str,
        output_content: str,
        receiver_name: str,
    )->tuple[int, str]:
        validateCode = 0
        if self.isTie == True:
            validateCode = 0
            ans = self.filterAnswer(output_content)
            if ans != "Error":
                self.wrongIter = 0
                self.current_info['answer'] = ans
            else:
                validateCode = 1
                self.wrongIter += 1
                return validateCode, ""
            self.current_info["isTie"] = "True"
            with open(self.save_file_path, 'a') as f:
                f.write(json.dumps(self.current_info, indent=4) + "\n")
            self.isOver = True
            return validateCode, output_content
        if validateCode == 0:
            self.currentCount += 1
            if self.currentCount > (self.maxRound-1) * self.current_speaking_num:
                ans = self.filterAnswer(output_content)
                if ans != "Error":
                    self.wrongIter = 0
                    if ans not in self.finalAnswerMap[self.current_level]:
                        self.finalAnswerMap[self.current_level][ans] = 1
                    else:
                        self.finalAnswerMap[self.current_level][ans] += 1
                else:
                    validateCode = 1
                    self.wrongIter += 1
                    return validateCode, ""
            if self.currentCount == self.maxRound * self.current_speaking_num:
                # #------------------------------------
                # self.finalAnswerMap[self.current_level]["Correct"] =6
                # self.finalAnswerMap[self.current_level]["Incorrect"] = 6
                # #------------------------------------
                print(f"\nLevel {self.current_level+1} Group Discussion Results:")
                for name, value in self.finalAnswerMap[self.current_level].items():
                    print(f"{name}: {value}")
                max_value = max(self.finalAnswerMap[self.current_level].values())
                most_label = [key for key, value in self.finalAnswerMap[self.current_level].items() if value == max_value]
                self.current_info['voteMap'].append(self.finalAnswerMap[self.current_level])
                if len(most_label) == 1 or self.current_level == self.maxLevel:
                    most_label = most_label[0]
                    self.current_info['answer'] = most_label
                    with open(self.save_file_path, 'a') as f:
                        f.write(json.dumps(self.current_info, indent=4) + "\n")
                    self.isOver = True
                elif self.use_secretary:
                    self.isTie = True
                else:
                    self.level_shift = True
        return validateCode, output_content
    def dealAbnormaly(
        self,
        validateCode: int,
        input_content: str,
        output_content: str,
        receiver_name: str,
    ) -> str:
        if self.wrongIter >= 2:
            raise Exception("Too many wrong iterations.")
        return input_content + "\n" + '(Hint: You must respond as required json format: "{\"reasons\": \"(a string of your reasoning process)\", \"answer\": \"(a pure numeric value without unit)\"}")'
    def modifyRawInputMessage(
        self,
        messages: list,
    ) -> str:
        return "\n".join(messages)
    def initMessage(
        self,
    ) -> list[Message]:
        messages = []
        p = sorted(self.participants, key=lambda x: x.name)
        for person in p:
            if person.name != self.secretary_name:
                plus_prompt = ''
                # plus_prompt = "(Your final answer must be [Correct])" if (ord(person.name)-ord('A')) % 3 == 0 else "(Your final answer must be [Incorrect])" if (ord(person.name)-ord('A')) % 3 == 1 else "(Your final answer must be [Unknown])"
                message = Message(
                    message_content=self.UserQuestionPrompt + "\n" + plus_prompt,
                    sender=person,
                    receivers={person},
                    depth=0,
                )
                messages.append(message)
        return messages
    def getSystemPrompt(
        self,
        receiver_name: str,
    ) -> str:
        return DebateMetaPrompt
    def maintainSilence(
        self,
        receiver_name: str,
        content: str,
        depth: int,
    ):
        ...
    def isHold(
        self,
        participant: Participant,
        messages: list
    ):
        ...
    def mergeCommonMessage(
        self,
        receiver_name: str,
        depth: int,
        messages: list,
    ) -> str:
        opinion_map = {
        }
        other_opinion_map = {
        }
        numMap = {
            2: 'Two',
            3: 'Three',
            4: 'Four',
            5: 'Five',
            6: 'Six',
            7: 'Seven',
            8: 'Eight',
            9: 'Nine',
            10: 'Ten',
            11: 'Eleven',
            12: 'Twelve',
            13: 'Thirteen',
            14: 'Fourteen',
            15: 'Fifteen',
            16: 'Sixteen',
            17: 'Seventeen',
            18: 'Eighteen',
            19: 'Nineteen',
            20: 'Twenty',
            21: 'Twenty-one',
            22: 'Twenty-two',
            23: 'Twenty-three',
            24: 'Twenty-four',
            25: 'Twenty-five',
        }
        if self.isTie == False:
            current_group_id = None
            for id, members in self.groupMap[self.current_level].items():
                if receiver_name in members:
                    current_group_id = id
                    break
            assert current_group_id != None, "Current group id is None."
            for message in messages:
                ans = self.filterAnswer(message.message_content)
                if message.sender.name in self.groupMap[self.current_level][current_group_id]:
                    if ans != "Error":
                        if ans not in opinion_map:
                            opinion_map[ans] = [message]
                        else:
                            opinion_map[ans].append(message)
                    else:
                        if "unknown" not in opinion_map:
                            opinion_map["unknown"] = [message]
                        else:
                            opinion_map["unknown"].append(message)
                else:
                    if ans != "Error":
                        if ans not in other_opinion_map:
                            other_opinion_map[ans] = 1
                        else:
                            other_opinion_map[ans] += 1
            groupNum = len(self.groupMap[self.current_level])
            final_str = self.MiddleSystem.replace( "<num>", str(groupNum) )  + "\n\n"
            if groupNum > 1:
                final_str += "Other group members' opinions:\n"
                other_one_str = "One agent thinks the answer is <ans>."
                other_many_str = "<num> agents think the answer is <ans>."
                for key, value in other_opinion_map.items():
                    if value != 0:
                        if value == 1:
                            final_str += other_one_str.replace("<ans>", key) + "\n"
                        else:
                            final_str += other_many_str.replace("<num>", numMap[value]).replace("<ans>", key) + "\n"
            final_str += "\nYour group's opinions:\n"
            one_str = "One agent thinks the answer is <ans>. Below is his response:\n"
            many_str = "<num> agents think the answer is <ans>. Below are their responses:\n"
            for key, value in opinion_map.items():
                list_len = len(value)
                if list_len == 1:
                    final_str += one_str.replace("<ans>", key)
                else:
                    final_str += many_str.replace("<num>", numMap[list_len]).replace("<ans>", key)
                for message in value:
                    final_str += message.message_content.strip().replace("\n\n", "\n") + "\n\n"
                ...
                # cur_message_list = correct_messages if key == "Correct" else incorrect_messages if key == "Incorrect" else unknown_messages
                # if value != 0:
                #     if value == 1:
                #         final_str += one_str.replace("<ans>", key)
                #     else:
                #         final_str += many_str.replace("<num>", numMap[value]).replace("<ans>", key)
                #     for message in cur_message_list:
                #         final_str += message.message_content.strip().replace("\n\n", "\n") + "\n\n"
            if self.level_shift == True:
                self.level_shift = False
                self.current_level += 1
                assert self.current_level < 3, "Current level is out of range."
                self.currentCount = 0
                self.current_speaking_num = 0
                for group in self.groupMap[self.current_level].values():
                    self.current_speaking_num += len(group)
            return final_str.strip()
        else:
            for message in messages:
                ans = self.filterAnswer(message.message_content)
                if ans != "Error":
                    if ans not in opinion_map:
                        opinion_map[ans] = [message]
                    else:
                        opinion_map[ans].append(message)
                else:
                    if "unknown" not in opinion_map:
                        opinion_map["unknown"] = [message]
                    else:
                        opinion_map["unknown"].append(message)
            SystemString = f'''{self.num_participants} agents are discussing the answer of a math word problem.\nThe given question is: {self.current_info['question']}.\n\nHowever, now there is a draw:\n'''
            one_str = "One agent thinks the answer is <ans>. Below is his response:\n"
            many_str = "<num> agents think the answer is <ans>. Below is one of their responses:\n"
            for key, value in opinion_map.items():
                list_len = len(value)
                if list_len == 1:
                    SystemString += one_str.replace("<ans>", key)
                else:
                    SystemString += many_str.replace("<num>", numMap[list_len]).replace("<ans>", key)
                SystemString += value[0].message_content.strip().replace("\n\n", "\n") + "\n\n"
                # cur_message_list = correct_messages if key == "Correct" else incorrect_messages if key == "Incorrect" else unknown_messages
                # if value != 0:
                #     if value == 1:
                #         SystemString += one_str.replace("<ans>", key)
                #     else:
                #         SystemString += many_str.replace("<num>", numMap[value]).replace("<ans>", key)
                #     SystemString += cur_message_list[0].message_content.strip().replace("\n\n", "\n") + "\n\n"
            return SystemString.strip()
    def getReceivers(
        self,
        sender_name: str,
        depth: int,
    ) -> set[Participant]:
        if self.use_secretary and self.currentCount > (self.maxRound-1) * self.current_speaking_num:
            return {person for person in self.participants if person.name == self.secretary_name}
        elif not self.use_secretary and self.currentCount > (self.maxRound-1) * self.current_speaking_num:
            receivers = {}
            if self.current_level < self.maxLevel:
                allowed_name = [name for sublist in self.groupMap[self.current_level+1].values() for name in sublist]
                receivers = {person for person in self.discussion_scope_map[self.current_level][sender_name] if person.name in allowed_name}
            else:
                receivers = {person for person in self.discussion_scope_map[self.current_level][sender_name]}
            # if self.level_shift == True:
            #     self.level_shift = False
            #     self.current_level += 1
            #     assert self.current_level < 3, "Current level is out of range."
            #     self.currentCount = 0
            #     self.current_speaking_num = 0
            #     for group in self.groupMap[self.current_level].values():
            #         self.current_speaking_num += len(group)
            return receivers
        else:
            return {person for person in self.discussion_scope_map[self.current_level][sender_name]}
    def insertSecretary(
        self,
        name: str,
        merged_message: str,
        depth: int
    ) -> tuple[bool, str]:
        if self.use_secretary and self.isTie and name == self.secretary_name:
            question_prompt = SecretaryQuestionPrompt
            return True, question_prompt
        else:
            return False, merged_message 

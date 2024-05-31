from rules.Debate.DebatePrompt import *
from utils.person import Participant
from utils.message import Message

import re
silence_str = '''=[silence]='''
class DebateRule:
    def __init__(self, num_participants) -> None:
        self.num_participants = num_participants
        self.participants = {Participant(chr(ord('A') + i)) for i in range(num_participants)}
        self.discussion_scope_map = {"A": [person for person in self.participants if person.name=='B' or person.name=='C'], 
                                     "B": [person for person in self.participants if person.name=='A'],
                                     "C": [person for person in self.participants if person.name=='A']}
        self.firstSpeaker = "A"
        self.isOver = False
        self.count = 0
    def processOutputMessage(
        self,
        input_content: str,
        output_content: str,
        receiver_name: str,
    ):
        validateCode= 0
        if input == "":
            validateCode = 0
        else:
            str1 = input("==[y or n]==")
            while str1 != "y" and str1 != "n":
                str1 = input("==[y or n]==")
            if str1 == 'n':
                validateCode = 1
        if validateCode == 0:
            self.count += 1
            if self.count == 6:
                self.isOver = True
        return validateCode, output_content if output_content != silence_str else ""
    def dealAbnormaly(
        self,
        validateCode: int,
        input_content: str,
        output_content: str,
        receiver_name: str,
    ):
        return "Rememer your standpoint!\n" + input_content
    def modifyRawInputMessage(
        self,
        messages: list,
    ):
        return "\n".join(messages)
    def initMessage(
        self,
    ):
        messages=[]
        p = sorted(self.participants, key=lambda x: x.name)
        for person in p:
            if person.name == self.firstSpeaker:
                message = Message(
                    message_content=player1InitPrompt,
                    sender=person,
                    receivers={person},
                    depth=0
                )
            else:
                message = Message(
                    message_content=player2InitPrompt,
                    sender=person,
                    receivers={person},
                    depth=0
                )
            messages.append(message)
        return messages
    def getSystemPrompt(
        self,
        name:str
    ) -> str:
        if name == "A":
            return player1SystemPrompt
        elif name == "B":
            return player2SystemPrompt
        else:
            raise Exception("Invalid name!")
    def maintainSilence(
        self,
        name: str,
        content: str,
        depth: int,
    ) -> bool:
        if depth == 0 and name == 'B':
            return True
        return False

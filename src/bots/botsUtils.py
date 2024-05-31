import time
from utils.utils import (
    # event_pandora, 
    event_scheduler, 
    event_chatgpt35_turbo,
    event_palm,
    event_exception,
    global_message_queue, 
    global_return_message_queue,
)
pandora_first_message = True
# All classes derived from Behaviors are called by the Scheduler
class Behaviors():
    def __init__(self):
        self.firstMessage = True
    def impose_input(
        self,
        content: str,
    ) -> str:
        ...
    def new_session(
        self,
    ) -> None:
        ...
    def switch_role(
        self,
        name: str,
    ) -> None:
        ...
    def set_title(
        self,
        title: str,
    ) -> None:
        ...
    def edit_input(
        self,
        content: str,
    ) -> str:
        ...
    def regen(
        self,

    ) -> str:
        ...
    def done(
        self
    ) -> None:
        ...


# class PandoraBehaviors(Behaviors):
#     def __init__(self):
#         super().__init__()
#     def impose_input(
#         self,
#         content: str,
#     ) -> str:
#         # print("we have content:", content)
#         global_message_queue.put(content)
#         # input()
#         time.sleep(0.5)
#         event_pandora.set()
#         while not event_scheduler.is_set():
#             event_scheduler.wait(1)
#             if event_exception.is_set():
#                 raise Exception("Another Thread Exception!")
#         if global_return_message_queue.empty():
#             raise Exception("global_return_message_queue is empty!")
#         message = global_return_message_queue.get()
#         event_scheduler.clear()
#         if message == "=[INTERNALSUCCESS]=":
#             return ""
#         elif message == "=[INTERNALERROR]=":
#             raise Exception("Bot Internal Error!")
#         return message
#     def new_session(
#         self,
#     ) -> None:
#         global pandora_first_message
#         if pandora_first_message:
#             self.impose_input("c")
#             pandora_first_message = False
#         else:
#             self.impose_input("/select")
#             self.impose_input("c")
#     def switch_role(
#         self,
#         name: str,
#     ) -> None:
#         self.impose_input("/select")
#         self.impose_input(name)
#     def set_title(
#         self, 
#         title: str
#     ) -> None:
#         self.impose_input("/title")
#         self.impose_input(title)
        
#     def edit_input(
#         self, 
#         content: str
#     ) -> str:
#         self.impose_input("/edit")
#         return self.impose_input(content)
#     def regen(
#         self,
#     ) -> str:
#         return self.impose_input("/regen")
#     def done(
#         self
#     ) -> None:
#         self.impose_input("/bye")

class TurboBehaviors(Behaviors):
    def __init__(self):
        super().__init__()
    def impose_input(
        self,
        content: str
    ) -> str:
        global_message_queue.put(content)
        # time.sleep(1)
        # print("we have content:", content)
        # input()
        event_chatgpt35_turbo.set()
        while not event_scheduler.is_set():
            event_scheduler.wait(1)
            if event_exception.is_set():
                raise Exception("Another Thread Exception!")
        if global_return_message_queue.empty():
            raise Exception("global_return_message_queue is empty!")
        message = global_return_message_queue.get()
        event_scheduler.clear()
        if message == "=[INTERNALSUCCESS]=":
            return ""
        elif message == "=[INTERNALERROR]=":
            raise Exception("Bot Internal Error!")
        return message
    def new_session(
        self,
        name:str,
        system_content: str,
    ) -> None:
        new_session = f'''/new\n{name}\n{system_content}'''
        self.impose_input(new_session)
    def switch_role(
        self,
        name: str,
    ) -> None:
        self.impose_input("/switch")
        self.impose_input(name)
    def set_title(
        self, 
        title: str
    ) -> None:
        self.impose_input("/title")
        self.impose_input(title)
    def edit_input(
        self,
        content: str
    ) -> str:
        self.impose_input("/edit")
        return self.impose_input(content)
    def regen(
        self,
    ) -> str:
        return self.impose_input("/regen")
    def done(
        self,
    ) -> None:
        self.impose_input("/done")

class PaLMBehaviors(Behaviors):
    def __init__(self):
        super().__init__()
    def impose_input(
        self,
        content: str
    ) -> str:
        global_message_queue.put(content)
        # time.sleep(0.1)
        input()
        # print("we have content:", content)
        # input()
        event_palm.set()
        while not event_scheduler.is_set():
            event_scheduler.wait(1)
            if event_exception.is_set():
                raise Exception("Another Thread Exception!")
        if global_return_message_queue.empty():
            raise Exception("global_return_message_queue is empty!")
        message = global_return_message_queue.get()
        event_scheduler.clear()
        if message == "=[INTERNALSUCCESS]=":
            return ""
        elif message == "=[INTERNALERROR]=":
            raise Exception("Bot Internal Error!")
        return message
    def new_session(
        self,
        name:str,
        system_content: str,
    ) -> None:
        new_session = f'''/new\n{name}\n{system_content}'''
        self.impose_input(new_session)
    def switch_role(
        self,
        name: str,
    ) -> None:
        self.impose_input("/switch")
        self.impose_input(name)
    def set_title(
        self, 
        title: str
    ) -> None:
        self.impose_input("/title")
        self.impose_input(title)
    def edit_input(
        self,
        content: str
    ) -> str:
        self.impose_input("/edit")
        return self.impose_input(content)
    def regen(
        self,
    ) -> str:
        return self.impose_input("/regen")
    def done(
        self,
    ) -> None:
        self.impose_input("/done")
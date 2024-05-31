import google.generativeai as palm
import os
import json
import time
import datetime
import traceback
from utils.utils import (
    silence_str,
    event_scheduler,
    event_palm,
    event_exception,
    global_message_queue, 
    global_return_message_queue,
)
from utils.utils import rule
from google.api_core.exceptions import GoogleAPICallError
palm.configure(api_key=os.getenv("PALM_API_KEY"))

class PaLMLogger:
    def __init__(self):
        self.log_path = ".\\src\\bots\\palm2\\palmLogs\\"
        current_time = datetime.datetime.now()
        dir_name = current_time.strftime("%Y-%m-%d_%H-%M-%S")
        self.log_path = os.path.join(self.log_path, dir_name)
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
    def createNewLog(self, system_content:str, name:str)->str:
        log_name = name + ".json"
        tmp = [{
            "author": "context",
            "content": system_content,
        }]
        print("Background Instructions:", system_content)
        with open(os.path.join(self.log_path, log_name), "w") as f:
            json.dump(tmp, f, indent=4)
        return log_name
    def changeLogName(self, old_name:str, new_name:str):
        os.rename(os.path.join(self.log_path, old_name), os.path.join(self.log_path, new_name))
        return
    def readLog(self, name:str) -> tuple[str, list]:
        with open(os.path.join(self.log_path, name), "r") as f:
            data = json.load(f)
        return data[0]["content"], data[1:]
    def writeLog(self, name:str, content:list):
        with open(os.path.join(self.log_path, name), "w") as f:
            json.dump(content, f, indent=4)
        return

class PaLMBot:
    def __init__(self) -> None:
        self.current_name = ""
        self.logger = PaLMLogger()
        self.defaults = {
            'model': 'models/chat-bison-001',
            'temperature': 0.2,
            'candidate_count': 2,
            'top_k': 40,
            'top_p': 0,
        }
        self.current_content = []
    
    def createAgent(self, name:str, system_content:str):
        self.current_name = self.logger.createNewLog(system_content, name)
        print("===========New Agent Created===========")
        return
    def switchAgent(self, name:str):
        name += ".json"
        print("============Current Agent name is %s============" % name)
        self.current_name = name
        return
    def setAgent(self, name:str):
        pass
    @staticmethod
    def __get_input():
        while not event_palm.is_set():
            event_palm.wait(1)
            if event_exception.is_set():
                raise Exception("Another Thread Exception!")
        if global_message_queue.empty():
            raise Exception("global_message_queue is empty!")
        message = global_message_queue.get()
        print("\nYou:")
        return message
    @staticmethod
    def __impose_output(content:str):
        global_return_message_queue.put(content)
        event_scheduler.set()
        event_palm.clear()
        return

    def get_messages(self) -> tuple[str, list]:
        return self.logger.readLog(self.current_name)
    def write_messages(self, context:str, messages:list):
        messages.insert(0, {"author": "context", "content": context})
        self.logger.writeLog(self.current_name, messages)
        return
    def generate_response(self, context: str, messages: list) -> str:
        print("PaLM2:")
        os.environ["HTTP_PROXY"] = "http://127.0.0.1:10809"
        os.environ["HTTPS_PROXY"] = "http://127.0.0.1:10809"
        try:
            response = palm.chat(
                **self.defaults,
                context=context,
                examples=[],
                messages=messages
            )
            respond_text = response.last
            print(respond_text)
        except GoogleAPICallError as e:
            retry_time = 10
            print(f"Got an error from Google API: {e}. Retry in {retry_time} seconds.")
            time.sleep(retry_time)
            return self.generate_response(context, messages)
        except Exception as e:
            print(f"Got an error: {e}.")
            event_exception.clear()
            event_exception.set()
            raise e
        os.environ.pop("HTTP_PROXY")
        os.environ.pop("HTTPS_PROXY")
        return respond_text
    def __process_special_command(self, input:str):
        input = input.strip()
        print(input)
        if input.startswith("/new"):
            input_lines = input.split("\n")
            assert len(input_lines) >= 3, "Input Format Error!"
            agent_name = input_lines[1]
            system_content = "\n".join(input_lines[2:])
            self.createAgent(agent_name, system_content)
            self.__impose_output("=[INTERNALSUCCESS]=")
        elif input == "/switch":
            self.__impose_output("=[INTERNALSUCCESS]=")
            agent_name = self.__get_input()
            self.switchAgent(agent_name)
            self.__impose_output("=[INTERNALSUCCESS]=")
            print(agent_name)
        elif input == "/title":
            self.__impose_output("=[INTERNALSUCCESS]=")
            title = self.__get_input()
            self.__impose_output("=[INTERNALSUCCESS]=")
            print(title)
        elif input == "/edit":
            self.__impose_output("=[INTERNALSUCCESS]=")
            modified_content = self.__get_input()
            context, messages = self.get_messages()
            messages[-1]["content"] = modified_content
            print(modified_content)
            response = self.generate_response(context, messages)
            self.__impose_output(response)
            messages.append({
                "author": '1',
                "content": response
            })
            self.write_messages(context, messages)
        elif input == "/regen":
            context, messages = self.get_messages()
            messages.pop()
            response = self.generate_response(context, messages)
            self.__impose_output(response)
            messages.append({
                "author": '1',
                "content": response
            })
            self.write_messages(context, messages)
        elif input == "/done":
            self.__impose_output("=[INTERNALSUCCESS]=")
            return True
        else:
            self.__impose_output("=[INTERNALERROR]=")
            raise Exception("Unknown Command!")
        return False
    def run(self):
        try:
            while True:
                input = self.__get_input()
                if input[0] == '/':
                    done = self.__process_special_command(input)
                    if done:
                        event_exception.clear()
                        event_exception.set()
                        raise Exception("Done!")
                elif input.startswith(silence_str):
                    context, messages = self.get_messages()
                    messages.append({
                        "author": '0',
                        "content": input[len(silence_str)+1:]
                    })
                    print(messages[-1]['content'])
                    messages.append({
                        "author": '1',
                        "content": ""
                    })
                    print(silence_str)
                    self.write_messages(context, messages)
                    self.__impose_output(silence_str) # This is customized field
                else:
                    context, messages = self.get_messages()
                    print(input)
                    ## maybe filter messages here
                    # messages.append({
                    #     "author": "0",
                    #     "content": input
                    # })
                    ##### Temporary Zone for Group Discussion #####
                    if len(messages) == 0:
                        prompt_str = '''You must make your answer in the format required in the provided context (including "First let's write down all the premises with labels:" and "Next, let's answer the question step by step with reference to the question and reasoning process:")\n'''
                        prompt_str += '''Also, you must captalize the first letter of every opinion label. For example, [Unknown], [Correct] and [Incorrect].'''
                        prompt_str += '''\nUse the knowledge only provided in the premises, do not hallucinate other knowledge not provided in the premises. Only do inference from the premises.\n'''
                        messages.append({
                            "author": "0",
                            "content": prompt_str + input
                        })
                        content = messages[0]['content'].strip().split("\n")
                        content = content[:-1]
                        messages[0]['content'] = "\n".join(content)
                    elif len(messages) == 2:
                        palm_str = messages[0]['content'] + "Use the knowledge only provided in the premises. Do not use your own knowledge. Give an updated answer in the required format to the question. Do not analyze your previous and other's opinoins. Your responding format must conform the requirement. You are forbidden to copy others' reasoning steps."
                        messages.append({
                            "author": "0", 
                            "content": input
                        })
                        messages.append({
                            "author": "1",
                            "content": "I see."
                        })
                        messages.append({
                            "author": "0",
                            # "content": rule.UserUpdatePrompt
                            "content": palm_str
                        })
                        print(f'{rule.UserUpdatePrompt}\n')
                    elif len(messages) == 5:
                        messages[2]['content'] = input
                        print(f'{rule.UserUpdatePrompt}\n')
                    ##### Temporary Zone for Group Discussion Ends####

                    response = self.generate_response(context, messages)
                    self.__impose_output(response)
                    ##### Temporary Zone for Group Discussion #####
                    if len(messages) < 2:
                        messages.append({
                            "author": "1",
                            "content": response
                        })
                        # content = messages[0]['content'].strip().split("\n")
                        # content = content[:-1]
                        # messages[0]['content'] = "\n".join(content)
                    else:
                        messages[1]['content'] = response
                    ##### Temporary Zone for Group Discussion Ends####
                    # messages.append({
                    #     "author": "1",
                    #     "content": response
                    # })
                    self.write_messages(context, messages)
        except Exception as e:
            print(f"Exception: {type(e).__name__} - {e}")
            traceback.print_exc()
            event_exception.clear()
            event_exception.set()
            # print(f'Input Tokens: {self.input_tokens}')
            # print(f'Output Tokens: {self.output_tokens}')
            exit()

                        



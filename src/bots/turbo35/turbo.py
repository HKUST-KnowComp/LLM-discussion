import openai
from openai.error import (
    RateLimitError,
    APIError,
    ServiceUnavailableError,
    APIConnectionError,
    Timeout
)
import tiktoken
import os
import json
import datetime
import time
import traceback
from utils.utils import (
    silence_str,
    event_scheduler,
    event_chatgpt35_turbo,
    event_exception,
    global_message_queue,
    global_return_message_queue
)
from utils.utils import rule, conf_logger
# from bots.turbo35.turboUtils import TurboGroupV1
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT_E")
openai.api_key = os.getenv("AZURE_OPENAI_KEY_E")
openai.api_version = "2023-07-01-preview"
print(f"Azure OpenAI Endpoint: {openai.api_base}")
print(f"Azure OpenAI Key: {openai.api_key}")

class TurboLogger:
    def __init__(self):
        self.log_path = ".\\src\\bots\\turbo35\\turboLogs\\"
        current_time = datetime.datetime.now()
        dir_name = current_time.strftime("%m-%d-%H-%M-%S")
        self.log_path = os.path.join(self.log_path, dir_name)
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
    def createNewLog(self, system_content:str, name:str)->str:
        current_time = datetime.datetime.now()
        log_name = name + ".json"
        tmp = [{
            "role": "system",
            "content": system_content
        }]
        print("Background Instructions:", system_content)
        with open(os.path.join(self.log_path, log_name), "w") as f:
            json.dump(tmp, f, indent=4)
        return log_name
    def changeLogName(self, old_name:str, new_name:str):
        os.rename(os.path.join(self.log_path, old_name), os.path.join(self.log_path, new_name))
        return
    def readLog(self, name:str) -> list:
        with open(os.path.join(self.log_path, name), "r") as f:
            return json.load(f)
    def writeLog(self, name:str, content:list):
        with open(os.path.join(self.log_path, name), "w") as f:
            json.dump(content, f, indent=4)
        return

class Turbo35Bot:
    def __init__(self) -> None:
        self.current_name = ''
        self.logger = TurboLogger()
        self.model = "gpt-3.5-turbo"
        self.engine = "turbo-4k"
        # self.engine = "planning"
        self.max_tokens = 4095
        self.temperature = 0.25
        self.stream = False
        self.input_tokens = 0
        self.output_tokens = 0

        # self.temp = 0

        self.delay_time = 0.00001
        self.current_content = []
        # self.turboRule = TurboGroupV1() 
    
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
        while not event_chatgpt35_turbo.is_set():
            event_chatgpt35_turbo.wait(1)
            if event_exception.is_set():
                raise Exception("Another Thread Finished or Exception!")
        if global_message_queue.empty():
            raise Exception("global_message_queue is empty!")
        message = global_message_queue.get()
        print("\nYou:")
        return message
    @staticmethod
    def __impose_output(content:str):
        global_return_message_queue.put(content)
        event_scheduler.set()
        event_chatgpt35_turbo.clear()
        return
    @staticmethod
    def messagesTokens(messages: list) -> int:
        num_tokens = 0
        tokens_per_message = 4
        tokens_per_name = -1
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-0613")
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3
        return num_tokens
    def get_messages(self) -> list:
        return self.logger.readLog(self.current_name)
    def write_messages(self, messages: list):
        self.logger.writeLog(self.current_name, messages)
        return
    
    def generate_response(self, messages: list) -> str:
        print("ChatGPT3.5:")
        # print("Valid Response!")
        # return "Valid Response!"
        # print(f"{self.temp}: [Correct]")
        # self.temp += 1
        # return f"{self.temp-1}: [Correct]"
        try:
            response = openai.ChatCompletion.create(
                # model=self.model,
                engine=self.engine,
                messages=messages,
                temperature=self.temperature,
                stream=self.stream,
            )
            if self.stream:
                respond_text = ''
                answer = ''
                self.input_tokens += self.messagesTokens(messages)
                for event in response:
                    self.output_tokens += 1
                    print(answer, end='', flush=True)
                    if len(event['choices']) != 0:
                        event_text = event['choices'][0]['delta']
                        answer = event_text.get('content', '')
                    if answer != '':
                        respond_text += answer
                    time.sleep(self.delay_time)
            else:
                respond_text = response['choices'][0]['message']['content']
                self.input_tokens += response['usage']['prompt_tokens']
                self.output_tokens += response['usage']['completion_tokens']
                print(respond_text)
                # print(self.rule.Acontent)
            return respond_text
        except RateLimitError as e:
            retry_time = e.retry_after if hasattr(e, 'retry_after') else 30
            print(f"Rate limit exceeded. Retrying in {retry_time} seconds...")
            time.sleep(retry_time)
            return self.generate_response(messages)
        except APIError as e:
            retry_time = e.retry_after if hasattr(e, 'retry_after') else 30
            print(f"API error occurred. Retrying in {retry_time} seconds...")
            time.sleep(retry_time)
            return self.generate_response(messages)
        except ServiceUnavailableError as e:
            retry_time = 30  # Adjust the retry time as needed
            print(f"Service is unavailable. Retrying in {retry_time} seconds...")
            time.sleep(retry_time)
            return self.generate_response(messages)
        except Timeout as e:
            retry_time = 10  # Adjust the retry time as needed
            print(f"Request timed out: {e}. Retrying in {retry_time} seconds...")
            time.sleep(retry_time)
            return self.generate_response(messages)
        except APIConnectionError as e:
            retry_time = 10
            print(f"API connection error occurred. Retrying in {retry_time} seconds...")
            time.sleep(retry_time)
            return self.generate_response(messages)
        except Exception as e:
            log_path = "error.log"
            print(f"Exception: {type(e).__name__} - {e}")
            with open(log_path, "a") as f:
                f.write(f"Exception: {type(e).__name__} - {e}\n")
                f.write(f"Messages: {messages}\n")
                f.write(f"Input Tokens: {self.input_tokens}\n")
                f.write(f"Output Tokens: {self.output_tokens}\n")
                f.write(f"Log File: {self.logger.log_path}\n\n")
            event_exception.clear()
            event_exception.set()
            exit()
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
            messages = self.get_messages()
            messages.pop()
            ## You can add customized part here
            messages[-1]["content"] = modified_content
            print(messages[-1]["content"])
            response = self.generate_response(messages)
            self.__impose_output(response)
            messages.append({
                "role": "assistant",
                "content": response
            })
            self.write_messages(messages)
        elif input == "/regen":
            messages = self.get_messages()
            messages.pop()
            response = self.generate_response(messages)
            self.__impose_output(response)
            messages.append({
                "role": "assistant",
                "content": response
            })
            self.write_messages(messages)
        elif input == "/done":
            return True
        else:
            self.__impose_output("=[INTERNALERROR]=")
            raise Exception("Internal Error!")
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
                    ## maybe filter messages here
                    messages = self.get_messages()
                    messages.append({
                        "role": "user",
                        "content": input[len(silence_str)+1:]
                    })
                    print(messages[-1]["content"])
                    messages.append({
                        "role": "assistant",
                        "content": ""
                    })
                    print(silence_str)
                    self.write_messages(messages)
                    self.__impose_output(silence_str)
                else:
                    messages = self.get_messages()
                    print(input)
                    ## maybe filter messages here
                    # messages.append({
                    #     "role": "user",
                    #     "content": input
                    # })
                    ##### Temporary Zone for Group Discussion V1 #####
                    if len(messages) == 1:
                        messages.append({
                            "role": "user",
                            "content": input
                        })
                    elif len(messages) == 3:
                        messages.append({
                            "role": "system",
                            "content": input
                        })
                        messages.append({
                            "role": "user",
                            "content": rule.UserUpdatePrompt
                        })
                        print(f'{rule.UserUpdatePrompt}\n')
                    elif len(messages) == 5:
                        messages[3]['content'] = input
                        print(f'\n{rule.UserUpdatePrompt}\n')
                    ##### Temporary Zone for Group Discussion V1 Ends####

                    response = self.generate_response(messages)
                    self.__impose_output(response)
                    #### Temporary Zone for Group Discussion V1 ####
                    if len(messages) < 3:
                        messages.append({
                            "role": "assistant",
                            "content": response
                        })
                        content = messages[1]['content'].strip().split("\n")
                        # content = content[:-1]
                        messages[1]['content'] = "\n".join(content)
                    else:
                        messages[2]['content'] = response

                    #### Temporary Zone for Group Discussion V1 Ends ####
                    # messages.append({
                    #     "role": "assistant",
                    #     "content": response
                    # })
                    self.write_messages(messages)
        except Exception as e:
            print(f"Exception: {type(e).__name__} - {e}")
            traceback.print_exc()
            event_exception.clear()
            event_exception.set()
            print(f'{self.engine} Input Tokens: {self.input_tokens}')
            print(f'{self.engine} Output Tokens: {self.output_tokens}')
            conf_logger.save_tokens_(self.input_tokens, self.output_tokens, self.engine, temperature=self.temperature)
            exit()

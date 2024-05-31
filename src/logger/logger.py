import json
import os
import datetime
class Logger:
    def __init__(self):
        current_time = datetime.datetime.now()
        dir_name = current_time.strftime("%m-%d-%H-%M-%S")
        self.dir_name = dir_name
        self.log_path = os.path.join(os.getcwd(), "logs", dir_name)
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
        self.speaker_records = {}
        self.current_speaker = None
    def updateSpeaker(self, speaker):
        self.current_speaker = speaker
    def log(self, input, output):
        if self.current_speaker == None:
            raise Exception("current speaker is None!")
        if self.current_speaker not in self.speaker_records:
            self.speaker_records[self.current_speaker] = []
        self.speaker_records[self.current_speaker].append({"role": "user", "content": input})
        self.speaker_records[self.current_speaker].append({"role": "assistant", "content": output})
    def save(self):
        for speaker in self.speaker_records:
            file_name = speaker + ".json"
            file_path = os.path.join(self.log_path, file_name)
            with open(file_path, "w") as f:
                json.dump(self.speaker_records[speaker], f, indent=4)
    def save_tokens_(self, input_tokens, output_tokens, model_name, **kwargs):
        file_name = "info.json"
        file_path = os.path.join(self.log_path, file_name)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                json.dump({}, f, indent=4)
        with open(file_path, "r") as f:
            model_info = json.load(f)
        with open(file_path, "w") as f:
            model_info[model_name] = {"input_tokens": input_tokens, "output_tokens": output_tokens, "total_tokens": input_tokens + output_tokens, **kwargs}
            json.dump(model_info, f, indent=4)
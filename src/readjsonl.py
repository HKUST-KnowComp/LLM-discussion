import random
import json
import random
random.seed(40)
jsonl_path = "F:\\Projects\\Research\\Reasoning\\IsolationField\\GroupDiscussion2\\folio-wiki-curated.jsonl"
output_path = "F:\\Projects\\Research\\Reasoning\\IsolationField\\GroupDiscussion2\\pure.jsonl"

# Open the jsonl file and read all lines into a list
with open(jsonl_path, 'r', encoding='utf-8') as f:
    data = [json.loads(line) for line in f]

# Randomly select 150 data points from the list
random_data = random.sample(data, 460)

# Extract the "premises", "conclusion", "label" keys from each data point and write them to a new JSONL file
with open(output_path, 'w') as f:
    for d in random_data:
        premises = d['premises']
        conclusion = d['conclusion']
        label = d['label']
        output_dict = {"premises": premises, "conclusion": conclusion, "label": label}
        output_json = json.dumps(output_dict)
        f.write(output_json + "\n")
# with open(output_path2, 'w') as f:
#     for d in random_data:
#         premises = d['premises']
#         conclusion = d['conclusion']
#         label = d['label']
#         output_dict = {"premises": premises, "conclusion": conclusion, "label": label, "answer": "", "voteMap": {"Correct": 0, "Incorrect": 0, "Unknown":0}, "log": ""}
#         output_json = json.dumps(output_dict, indent=4)
#         f.write(output_json + "\n")


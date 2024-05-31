# import json

# # jsonl_path = "F:\\Projects\\Research\\Reasoning\\IsolationField\\GroupDiscussion2\\resultLog\\groupV2(r3_Insist_150).jsonl"
# # jsonl_path = "F:\\Projects\\Research\\Reasoning\\IsolationField\\GroupDiscussion2\\resultLog\\groupV2(r3_Insist_200-460).jsonl"
# # jsonl_path = "F:\\Projects\\Research\\Reasoning\\IsolationField\\GroupDiscussion2\\resultLog\\groupV2(r3_Insist_wrong).jsonl"
# jsonl_path = "F:\\Projects\\Research\\Reasoning\\IsolationField\\GroupDiscussion19\\resultLog\\114.jsonl"


# with open(jsonl_path, "r", encoding="utf-8") as f:
#     data = []
#     json_data = []
#     all_lines = f.readlines()
#     id = 0
#     try:
#         for line in all_lines:
#             if line[0] == "{":
#                 json_data.append(line.strip())
#             elif line[0] == "}":
#                 json_data.append(line.strip())
#                 id += 1
#                 data.append(json.loads("".join(json_data)))
#                 json_data = []
#             else:
#                 json_data.append(line.strip())
#     except Exception as e:
#         print("Error: ", e)
#         print("id: ", id)
    

# total = len(data)
# correct = sum(1 for d in data if d["label"] == d["answer"])
# wrong_index = [id+1 for id, d in enumerate(data) if d["label"] != d["answer"]]
# percentage = correct / total * 100

# print(f"Total number of questions: {total}")
# print(f"Number of correct answers: {correct}")
# print(f"Percentage of correct answers: {percentage:.2f}%")

import json
import os
jsonl_path = os.path.join(os.getcwd(), "resultLog", "gsm8k.jsonl")
all_id = [i for i in range(0, 100)]
with open(jsonl_path, "r", encoding="utf-8") as f:
    data = []
    json_data = []
    all_lines = f.readlines()
    id = 0
    try:
        for line in all_lines:
            if line[0] == "{":
                json_data.append(line.strip())
            elif line[0] == "}":
                json_data.append(line.strip())
                id += 1
                json1 = json.loads("".join(json_data))
                if json1["id"] in all_id:
                    all_id.remove(json1["id"])
                data.append(json1)
                json_data = []
            else:
                json_data.append(line.strip())
    except Exception as e:
        print("Error: ", e)
        print("id: ", id)

total = len(data)
correct = sum(1 for d in data if d["label"] == d["answer"].replace(".00", "").replace(",", "").replace("-", "").replace("%", ""))
wrong_index = [id+1 for id, d in enumerate(data) if d["label"] != d["answer"]]
percentage = correct / total * 100
for d in data:
    if d["answer"].replace(".00", "").replace(",", "").replace("-", "").replace("%", "") != d["label"]:
        print(f"id: {d['id']} label: {d['label']}, answer: {d['answer']}")
print(f"Total number of questions: {total}")
print(f"failed id: {all_id}")
print(f"Number of correct answers: {correct}")
print(f"Percentage of correct answers: {percentage:.2f}%")

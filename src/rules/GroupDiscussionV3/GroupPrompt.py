DebateMetaPrompt = '''You are asked to solve a linguistically diverse grade school math word problem. Use basic arithmetic operations (+ - * /) to reach the final answer. It is guaranteed to have an answer.
Your response format should be first write down all the premises with labels, then answer the problem step by step with reference to the problem and reasoing process. Please strictly output your answer in the json format: "{\"reasons\": \"(a string of your reasoning process)\", \"answer\": \"(a pure numeric value without unit)\"}"'''

MiddleSystem = '''There are <num> groups of people discussing on the same math word question. I will provide you the detailed reasons and answers from your group member and answers from other group members. Use these opinions and your previous answer as additional advice, note that they maybe wrong. Do not copy other's entire answer, modify the part you believe is wrong.'''

UserQuestionPrompt = '''<question>
Now please strictly answer this question in the json format: "{\"reasons\": \"(a string of your reasoning process)\", \"answer\": \"(a pure numeric value without unit)\"}"'''

UserUpdatePrompt = '''Use the provided answers as additional advice critically, please provide an updated answer. Make sure to strictly state your response over proposition at the end of the response in the json format: "{\"reasons\": \"(a string of your reasoning process)\", \"answer\": \"(a pure numeric value without unit)\"}"'''

SecretaryQuestionPrompt = '''Your task is to carefully determine which answer is more plausible. Each provided answer is a numeric value. You should give your response in the required json format: "{\"reasons\": \"(a string of your reasoning process)\", \"answer\": \"(a pure numeric value without unit)\"}". You are forbidden to copy others' reasoning steps. '''
# from rules.GroupDiscussionV3.GroupRule import GroupRule

# rule = GroupRule(12, False)
# rule.printInit()
def find_last_occurrence(string):
    correct = string.rfind("[Correct]")
    incorrect = string.rfind("[Incorrect]")
    unknown = string.rfind("[Unknown]")
    return max(correct, incorrect, unknown)

string = "This is a [Correct] test [Incorrect] string [Unknown] [Correct] [Unknown]"
last_occurrence = find_last_occurrence(string)

print(string[last_occurrence:])
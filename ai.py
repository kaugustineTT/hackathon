#!/usr/bin/env python3
import os
import subprocess
import json
from openai import OpenAI
client = OpenAI(
    api_key="M76pPQMt4kEAHnkNPHvQ",
    base_url="https://vllm--tenstorrent.workload.tenstorrent.com/v1",
)
#print(f"URL: '{client.base_url}'")

# This API doesnt appear to work with the endpoint so I am just reading in the
# file. Need to improve the code to be able to load multiple files to do 
# proper failure analysis
# file = client.files.create(
#     file=open("/proj_soc/user_dev/kaugustine/execution_manager-refactor/ttem_it/compile.log", "rb"),
#     purpose="answers"  # You specify the purpose for querying
# )

# Getting the root of the git repository to find the compile.log file
git_root = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"],
    capture_output=True,
    text=True,
    check=True
).stdout.strip()

# Construct the path to compile.log. I had to reduce the logfile from its original
# size to be able to run the code. It used too many tokens. I need to figure out
# how to handle this. This is a real logfile and a real failure from simulation.
log_file_path = os.path.join(git_root, "compile.log")

# Open and read the file
with open(log_file_path, 'r') as file:
    log_file_contents = file.read()

# Print the file ID to use it later
# file_id = file['id']
# print(f"File ID: {file_id}")
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": f"My log file pasted below has multiple Error message. Analyze the logfile and create a NAME for each common type of failure. Then create a human readable DESCRIPTION that describes the failures. After that a COUNT that is the number of times the failure occurs in the log file. Followed by a HOW TO FIX section. Put a new line between each section. Do not reprint the question. Each error usually has the keyword Error- in front of it. This can be used to help figure out the count. {log_file_contents}",
        }
    ],
    model="tenstorrent/Meta-Llama-3.1-70B-Instruct",
    max_tokens=128,
)
#print(chat_completion.to_json(indent=4))

# Convert JSON response to Python dictionary
try:
	response_dict = json.loads(chat_completion.to_json(indent=4))
	#print("\nParsed JSON response:")
	#print(json.dumps(response_dict, indent=2))  # Pretty-print the result
	content = response_dict['choices'][0]['message']['content']
	print("\n========================================================")
	print(content)
	print("========================================================\n")
except json.JSONDecodeError:
    print("Failed to parse JSON response.")

### Need to figure out a method to keep a consistent response for errors especially if it is a known previous error. Need to figure out adding memory.
### Even after giving a hint on what to look at it still isn't getting the count right.

# EXAMPLE RESULT (Count is incorrect it should have been 5) This was first attempt.
# **Error: Module Previously Declared**

# *   **Name:** Duplicate Module Declaration
# *   **Description:** The module is previously declared in another file, causing a duplicate declaration error.
# *   **Count:** 29

# **How to Fix:**

# 1.  Identify the duplicate module declarations by analyzing the error messages.
# 2.  Determine which version of the module is correct and should be retained.
# 3.  Remove the duplicate module declaration from the other file(s).
# 4.  Verify that the module is only declared once in the entire design.

# **Example Fix:**

# Suppose the error message indicates that the module `TTOverlay


#EXAMPLE BASED ON CURRENT SEARCH

# NAME: Duplicate Module Declaration

# DESCRIPTION: The Verilog compiler has detected duplicate declarations of the same module. This occurs when a module is declared multiple times in the design, which is not allowed.

# COUNT: 29

# HOW TO FIX: To fix this error, remove one of the duplicate declarations and recompile the design. Make sure to remove the duplicate module declaration from the file where it is redeclared later.


# FINAL RUN
# (kaugustine@yyzc-soc06) /proj_soc/user_dev/kaugustine/hackathon: ./ai.py 

# ========================================================
# NAME: Duplicate Module Declaration

# DESCRIPTION: The error occurs when_dependency tracker encounters multiple declarations of the same module, which is not allowed in Verilog. This can happen due to incorrect naming of modules, incorrect inclusion of files, or duplicate definitions in the same file.

# COUNT: 29

# HOW TO FIX: To resolve this issue, you need to identify and remove the duplicate declarations of the modules. Make sure that each module has a unique name, and there are no duplicate definitions in the same file. You can also check the inclusion of files to ensure that the same module is not being included multiple times.
# ========================================================

#Ran one last time with the additiona of providing a hint on the error keywod to help figure out the count. Still didn't get the count right. Need to figure out how to improve the count.
# ========================================================
# NAME: Duplicate Module Declaration

# DESCRIPTION: The error occurs when the same module is declared multiple times in the design. This can happen when a module is defined in multiple files or when a module is instantiated multiple times with the same name.

# COUNT: 29

# HOW TO FIX: To fix this error, you need to remove one of the duplicate module declarations. You can do this by:

# 1. Identifying the duplicate module declarations: Look for the module names that are declared multiple times in the error messages.
# 2. Removing the duplicate declaration: Remove one of the duplicate module declarations from the design. You can do this by deleting the module
# ========================================================
from functions_pool import *

# while True:
query="""
帮我做一个西红柿炒鸡蛋, 要色香味俱全，时间合理，用料讲究
"""
messages = messages_initial_template(prompt_main, query)
round_num=0
while True:
    round_num+=1
    response_chat = chat_single(messages)
    if '做好啦' in response_chat:
        break
    print(response_chat)
    code_py = extract_code_blocks(response_chat)
    run_response = execute_and_display(code_py, globals())
    messages.append(message_template('assistant',response_chat))
    messages.append(message_template('user',run_response))

    print(run_response)
    print("==========%s============"%round_num)
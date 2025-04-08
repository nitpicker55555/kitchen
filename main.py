from functions_pool import *

# while True:
def execute_main():
    query="""
    帮我做一个西红柿炒鸡蛋, 和葱爆羊肉，要色香味俱全，时间合理，用料讲究
    
    """
    messages = messages_initial_template(prompt_main, query)
    round_num=0
    while True:
        round_num+=1
        if round_num>=100:
            break
        response_chat = chat_single(messages)
        if '都做好啦' in response_chat:
            break
        print(response_chat)
        code_py = extract_code_blocks(response_chat)
        run_response = execute_and_display(code_py, globals())
        messages.append(message_template('assistant',response_chat))
        messages.append(message_template('user',run_response))
        print()
        print("------------SYSTEM RESPONSE------------")
        print(run_response)
        print()

        var_global=get_global()
        print("==========ROUND:%s,TIME:%s s, REGION: %s============"%(round_num,var_global['global_time'],var_global['region']))
    var_global=get_global()
    print("==========TIME:%s============"%var_global['global_time'])
    print()
    print("------------pre_locations------------")
    print(pre_locations)
    print()

    print("------------objects_in_hand_history------------")
    print(objects_in_hand_history)
    print()

    print("------------objects_properties------------")
    print(objects_properties)
def exper():
    print(global_time)

    move_to((0.5, 1.35))
    look_objects()
    var_global=get_global()
    print(var_global['global_time'])
    print(var_global['pre_locations'])
    move_to((0.5, 0.35))
    look_objects()
    var_global=get_global()
    print(var_global['global_time'])
    print(var_global['region'])
execute_main()
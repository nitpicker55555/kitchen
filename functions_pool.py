import math

from fake_api import *
from prompt import *
from generate_objects_location import *
agent_location_now=[0.0,0.0]
pre_locations=[]
global_time=0
objects_properties={
    key: {'location': value,  'properties': []
    }
    for key, value in objects.items()
}
objects_properties['手']={}
objects_properties['手']['properties']=[]
objects_properties['手']['location']="in hands"

objects_in_hand=[]
objects_in_hand_history={}
print(objects_properties)

def calculate_movement(start, end, speed=0.8):
    """
    计算从 start 到 end 的距离与时间
    :param start: 起点坐标 (x, z)
    :param end: 终点坐标 (x, z)
    :param speed: 移动速度（单位：米/秒），默认 0.8 m/s
    :return: 字典，包含距离（米）与时间（秒）
    """
    x1, z1 = start
    x2, z2 = end
    distance = math.sqrt((x2 - x1)**2 + (z2 - z1)**2)
    time = distance / speed if speed > 0 else float('inf')
    return {
        "distance_m": round(distance, 3),
        "time_s": round(time, 2)
    }
def find_nearest_region(x, z,mode='normal'):
    min_distance = float('inf')
    nearest_region = None

    for region, coords in regions.items():
        x_range, _, z_range = coords
        center_x = (x_range[0] + x_range[1]) / 2
        center_z = (z_range[0] + z_range[1]) / 2
        dist = math.hypot(center_x - x, center_z - z)
        if dist < min_distance:
            min_distance = dist
            nearest_region = region

    # 找出该区域内的物体
    region_x, region_y, region_z = regions[nearest_region]
    region_objects = []
    obj_names=[]
    for name in objects_properties:
        if objects_properties[name]['location'] !='in hands':
            ox, oy, oz =objects_properties[name]['location']
            if (region_x[0] <= ox <= region_x[1] and
                region_y[0] <= oy <= region_y[1] and
                region_z[0] <= oz <= region_z[1]):
                region_objects.append((name, "No property" if not objects_properties[name]['properties'] else
                objects_properties[name]['properties']))
                obj_names.append(name)
    if mode=='normal':
        return nearest_region, region_objects
    else:
        return obj_names


def move_to(input_location=None):
    if input_location is None:
        input_location = [0, 0]
    global agent_location_now,pre_locations,global_time
    took_time=calculate_movement(agent_location_now,input_location)['time_s']
    agent_location_now=input_location


    pre_region=find_nearest_region(agent_location_now[0],agent_location_now[1])[0]
    pre_locations.append({"location":input_location,'region':pre_region,'time':global_time})
    global_time+=took_time
    return "Moved to %s. Took %s s."%(str(input_location),took_time)
def look_objects():
    global agent_location_now,pre_locations,global_time

    global_time+=2
    return find_nearest_region(agent_location_now[0],agent_location_now[1])

def take_action(with_object,action_name,to_object=None):
    global global_time
    # if with_object not in objects_in_hand and with_object!='手':
    #     return ("Error! %s not in your hand."%with_object)

    objs=find_nearest_region(agent_location_now[0], agent_location_now[1],mode='sys')

    if with_object not in objects_in_hand and  with_object not in objs  and with_object!='手':
        return ("Error! %s not in this region and not in hands."%with_object)
    if to_object not in objects_in_hand and  to_object not in objs  and to_object!='手':
        return ("Error! %s not in this region and not in hands."%to_object)

    query_str="with_object: "+with_object+ "action_name: "+action_name +'to_object: '+to_object


    judge_query="with_object: "+with_object+str(objects_properties[with_object]['properties'])+ "action_name: "+action_name +'to_object: '+to_object+str(objects_properties[to_object]['properties'])
    print(judge_query)
    judge_json=general_gpt_without_memory(judge_query,json_mode='json',system_prompt=prompt_judge_action)
    return_judge_json=json.loads(judge_json)
    print("ACTION JUDGE: ")
    print(judge_json)
    if not return_judge_json['actionable']:
        return "ACTION ERROR! %s"% return_judge_json['reasoning']
    return_json=general_gpt_without_memory(query_str,json_mode='json',system_prompt=prompt_action)
    return_json_result=json.loads(return_json)
    for object_name in return_json_result:
        if object_name!='took_time':
            objects_properties[object_name]['properties'].append({"property":return_json_result[object_name],'timestamp':global_time})
            if return_json_result[object_name]=='disappear': #Action导致物品消失

                objects_in_hand.remove(object_name)
                objects_in_hand_history[object_name][0]['drop_time'] = global_time

    global_time+=return_json_result['took_time']
    return "动作完成结果：%s, 花费时间：%s秒"%(str(return_json_result),return_json_result['took_time'])
def take_object(object_name):
    global global_time
    objs=find_nearest_region(agent_location_now[0], agent_location_now[1],mode='sys')

    if object_name not in objs:
        return ("Error! %s not in this region."%object_name)

    objects_in_hand.append(object_name)
    if object_name not in objects_in_hand_history:
        objects_in_hand_history[object_name]=[]
    objects_in_hand_history[object_name].append({"take_time":global_time})
    if len(objects_in_hand)>=3: #丢弃多余物品到拾取物品的地点
        objects_in_hand_history[object_name][0]['drop_time']=global_time
        objects_properties[objects_in_hand[2]]['location']=objects_properties[object_name]['location']
    objects_properties[object_name]['location']="in hands"

    global_time+=2
    return object_name+" 被拿起来了"

def drop_object(object_name,container_name=None):
    global global_time
    if container_name:
        objs = find_nearest_region(agent_location_now[0], agent_location_now[1], mode='sys')

        if object_name not in objects_in_hand and object_name not in objs:
            return ("Error! %s not in this region and not in hands." % object_name)
        if container_name not in objects_in_hand and container_name not in objs:
            return ("Error! %s not in this region and not in hands." % container_name)


        objects_properties[object_name]['location']=objects_properties[container_name]['location']
        return_info="%s 被放在了 %s 上面/里面" %(object_name,container_name)
        objects_properties[object_name]['properties'].append({'in container':container_name,'timestamp':global_time})
    else:

        temp_location=list(agent_location_now)
        temp_location.insert(1,0.1)
        objects_properties[object_name]['location']=temp_location
        objects_in_hand.remove(object_name)
        objects_in_hand_history[object_name][0]['drop_time'] = global_time
        return_info="%s 被放下了，位置：%s" %(object_name,str(objects_properties[object_name]['location']))

    global_time+=2
    return return_info
# Example call (uncomment to run)
def wait_time(int_time):
    global global_time
    global_time+=int_time
    return str(int_time)+"秒过去了，现在时间为:"+ str(global_time)


def get_global():
    return_json={
        "global_time":round(global_time,2),
        "pre_locations":pre_locations,
        "objects_in_hand_history":objects_in_hand_history,
        "objects_properties":objects_properties,
        "region":find_nearest_region(agent_location_now[0],agent_location_now[1])[0]

    }


    return return_json
# move_to((0.55, 4.95))
# print(take_object('油瓶'))
#
# move_to((0.55, 4.05))
# print(drop_object('平底锅', '炉灶'))
# print(take_action('手', '打开', '5级炉灶开关'))
# print(move_to((0.55, 5.85)))
# move_to((0.55, 0.1))
# print(take_object("番茄"))
# # move_to((0.0, 1.0))
# # print(move_to((0.55, 0.45)))
# print(look_objects())
#

# print(move_to((0.55, 5.85)))
# print(agent_location_now)
# print(drop_object("番茄"))
# print(objects_properties)
# print(look_objects())

# take_action("5级炉灶开关",'开到小火')
# print(objects_properties)
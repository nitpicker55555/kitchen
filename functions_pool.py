from locations import *
from fake_api import *
from prompt import *
agent_location_now=[0.0,0.0]
pre_locations=[]
global_time=0
objects_properties={
    key: {'location': value,  'properties': []
    }
    for key, value in objects.items()
}
objects_in_hand=[]
objects_in_hand_history={}
print(objects_properties)
def find_nearest_region(current_x, current_y, objects=objects, relationship=relationship, regions=regions):
    """
    Find the nearest region and its contained objects based on current coordinates.

    Args:
        current_x (float): Current x coordinate
        current_y (float): Current y coordinate
        objects (dict): Dictionary of objects with their 3D coordinates [x, y, z]
        relationship (dict): Dictionary mapping regions to their contained objects
        regions (dict): Dictionary mapping regions to their boundaries [[x_min, x_max], [y_min, y_max], [z_min, z_max]]

    Returns:
        dict: A dictionary containing:
            - 'region_name': The name of the nearest region
            - 'objects': A list of objects in the region with their names, coordinates, and distances
    """
    # Calculate distance to each region
    distances = {}
    for region_name, bounds in regions.items():
        x_bounds, y_bounds, z_bounds = bounds

        # Calculate the nearest point in the region to the current position
        nearest_x = max(x_bounds[0], min(current_x, x_bounds[1]))
        nearest_y = max(y_bounds[0], min(current_y, y_bounds[1]))

        # Calculate Euclidean distance in 2D (x-y plane)
        distance = ((current_x - nearest_x) ** 2 + (current_y - nearest_y) ** 2) ** 0.5
        distances[region_name] = distance

    # Find the nearest region
    nearest_region = min(distances, key=distances.get)

    # Get objects in the nearest region and calculate distance to each object
    region_objects = []
    for obj_name in relationship.get(nearest_region, []):
        if obj_name in objects:
            obj_coords = objects[obj_name]
            # Calculate distance from current position to the object (in 2D, x-y plane)
            obj_distance = ((current_x - obj_coords[0]) ** 2 + (current_y - obj_coords[1]) ** 2) ** 0.5
            region_objects.append({
                'name': obj_name,
                'coordinates': obj_coords,
                'distance': obj_distance
            })

    # Sort objects by distance
    region_objects.sort(key=lambda x: x['distance'])

    return {
        'region_name': nearest_region,
        'objects': region_objects
    }


def move_to(input_location=None):
    if input_location is None:
        input_location = [0, 0]
    global agent_location_now,pre_locations,global_time
    agent_location_now=input_location
    pre_locations.append({"location":input_location,'time':global_time})

    return "Moved to "+ str(input_location)
def look_objects():
    global agent_location_now,pre_locations,global_time

    return find_nearest_region(agent_location_now[0],agent_location_now[1])

def take_action(with_object,action_name,to_object=None):


    query_str="with_object: "+with_object+ "action_name: "+action_name
    if to_object:
        query_str+='to_object: '+to_object
    return_json=general_gpt_without_memory(query_str,json_mode='json',system_prompt=prompt_action)
    return_json_result=json.loads(return_json)
    for obj_name in return_json_result:

        objects_properties[obj_name]['properties'].append({"property":return_json_result[obj_name],'timestamp':global_time})

    return "动作完成结果："+str(return_json_result)
def take_object(object_name):
    objects_in_hand.append(object_name)
    if object_name not in objects_in_hand_history:
        objects_in_hand_history[object_name]=[]
    objects_in_hand_history[object_name].append({"take_time":global_time})
    if len(objects_in_hand)>=3: #丢弃多余物品到拾取物品的地点
        objects_in_hand_history[object_name][0]['drop_time']=global_time
        objects_properties[objects_in_hand[2]]['location']=objects_properties[object_name]['location']
    objects_properties[object_name]['location']="in hands"

    return object_name+" 被拿起来了"
def drop_object(object_name):
    objects_properties[object_name]['location']=agent_location_now.append(2.0)
    objects_in_hand.remove(object_name)
    objects_in_hand_history[object_name][0]['drop_time'] = global_time

    return object_name+" 被放下了，位置："+str(objects_properties[object_name]['location'])
# Example call (uncomment to run)
take_action("刀_2",'切菜','番茄')
print(objects_properties)
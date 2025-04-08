import random
from locations import *

def generate_object_coordinates(relationship, regions):
    """
    为每个物品生成随机坐标

    Args:
        relationship: 字典，键为区域名称，值为该区域包含的物品列表
        regions: 字典，键为区域名称，值为该区域的坐标范围 [[x_min, x_max], [y_min, y_max], [z_min, z_max]]

    Returns:
        字典，键为物品名称，值为该物品的随机坐标 [x, y, z]
    """
    objects = {}

    for region, items in relationship.items():
        # 获取该区域的坐标范围
        if region not in regions:
            continue

        x_range, y_range, z_range = regions[region]

        for item in items:
            # 在该区域范围内随机生成坐标
            x = random.uniform(x_range[0], x_range[1])
            y = random.uniform(y_range[0], y_range[1])
            z = random.uniform(z_range[0], z_range[1])

            # 将该物品及其坐标添加到结果字典中
            objects[item] = [round(x, 3), round(y, 3), round(z, 3)]

    return objects



# 生成物品坐标
objects = generate_object_coordinates(relationship, regions)


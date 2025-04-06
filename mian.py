from locations import *


def find_nearest_region(current_x, current_y, objects, relationship, regions):
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


# Example usage
def example():
    # Sample coordinates
    current_x, current_y = 1.9, 0.9

    result = find_nearest_region(current_x, current_y, objects, relationship, regions)

    print(f"距离最近区域名称: {result['region_name']}")
    print("\n区域中的物品 (按距离排序):")
    for obj in result['objects']:
        print(f"  - {obj['name']}: 坐标{obj['coordinates']}, 距离: {obj['distance']:.2f}")

# Example call (uncomment to run)
example()
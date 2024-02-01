def get_element_cecentroid(verteies_coordinates_list):
    sum_x = float(0)
    sum_y = float(0)
    sum_z = float(0)
    
    for point_i in verteies_coordinates_list:
        sum_x += point_i[0]
        sum_y += point_i[1]
        sum_z += point_i[2]

    centroid_x = sum_x/len(verteies_coordinates_list)
    centroid_y = sum_y/len(verteies_coordinates_list)
    centroid_z = sum_z/len(verteies_coordinates_list)

    return (centroid_x, centroid_y, centroid_z)

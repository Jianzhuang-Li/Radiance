import os
import numpy as np
import json
import pandas as pd
import typing
from typing import List
from matplotlib import pyplot as plt
from loguru import logger
from matplotlib import cm
from matplotlib import axes
from mpl_toolkits.mplot3d import Axes3D

# 定义转换公式的常量
FACTOR_R = 0.265
FACTOR_G = 0.670
FACTOR_B = 0.065
MULTIPLIER = 179

def dc_timestep(view, transmission, daylight, sky, save_path, option="", if_print=True):
    """compute annual simulation time-step(s) via matrix multiplication

    Args:
        view (string): view matrix, relating outgoing directions on window to desired results at interior.
        transmission (string): transmission matrix, relating incident window directions to exiting directions (BSDF).
        daylight (string): daylight matrix, relating sky patches to incident directions on window.
        sky (string): sky vector/matrix, assigning luminance values to patches representing sky directions.
        save_path (string): the path to save the RGB data.
        option (str, optional): "-n 8760" when do manual simulation.
        if_print (bool, optional): if print the command.
    """

    command = "dctimestep -h " + option + " " + view + " " + transmission + " " + daylight + " " + sky + " > " \
              + save_path
    if if_print:
        logger.info(command)
    os.system(command)

def view_matrix(octree, photocells, window_material):
    """compute the view matrix by the view file.There may be some wrongs in native-windows.

    Args:
        octree (string): the window must be replaced by a glazing material.
        photocells (string): points in time illuminance or luminance result.
        window_material (string): the glazing materials of the window.

    Returns:
        _type_: view_matrix
    """
    # rcontrib -f klems_full.cal -b kbinS -bn Nkbins -m glazing_mat -I+ -ab 12 -ad 50000 -lw 2e-5 
    command = "rcontrib -f klems_full.cal -b kbinS -bn Nkbins -m "+window_material + " -I+ \
    -ab 12 -ad 50000 -lw 2e-5 " + octree + " < " + photocells
    logger.info(command)
    matrix = os.system(command)
    return matrix

def gen_skv_p(altitude, azimuth, epsilon, delta, path_save_skv):
    """gen sky vector by Perez parameters. \
        Deriving the epsilon and delta parameters for use with the -P invocation is quite complicated,\
        and you are unlikely to need this.

    Args:
        altitude (float): the altitude is measured in degrees above the horizon.
        azimuth (float): the azimuth is measured in degrees west of South.
        epsilon (int): Epsilon variations express the transition from a totally overcast sky (epsilon=1) \
            to a low turbidity clear sky (epsilon>6).
        delta (float):  Delta can vary from 0.05 representing a dark sky to 0.5 for a very bright sky.
        path_save_skv (string):the path to save the sky vector.
    """

    command = "gendaylit -ang " + str(altitude) + " " + str(azimuth) + " -P " + " " + str(epsilon) + " " + str(delta) +\
              " " + " |genskyvec -m 4 -c 1 1 1 > " + path_save_skv
    logger.info(command)
    os.system(command)

def gen_skv_W(altitude, azimuth, direct_normal_irradiance, diffuse_horizontal_irradiance, path_save_skv):
    """gen sky vector by irradiance.

    Args:
        altitude (float): the altitude is measured in degrees above the horizon.
        azimuth (float): the azimuth is measured in degrees west of South.
        direct_normal_irradiance (float): the radiant flux coming from the sun and an area of approximately 3 degrees round the sun.
        diffuse_horizontal_irradiance (float): diffuse horizontal irradiance.
        path_save_skv (string): the path to save the sky vector.
    """
    command = "gendaylit -ang " + str(altitude) + " " + str(azimuth) + " -W " + " " + str(direct_normal_irradiance) + \
              " " + str(diffuse_horizontal_irradiance) + " " + " |genskyvec -m 4 -c 1 1 1 > " + path_save_skv
    logger.info(command)
    os.system(command)

def gen_dmx(octree, x, y, z, sky_mat, window_path, dmx_output_path):
    """compute contribution coefficients from sky divisions.

    Args:
        octree (string): the path of octree.
        x(float): x of the normal of the exterior surface of the fenestration.
        y(float): y of the the normal of the exterior surface of the fenestration,.
        z(float): z of the normal of the exterior surface of the fenestration.
        sky_material(string): sky material
        window_path(string): the path of window object.
        dmx_output_path (string): the path to save daylight matrix.
    """
    command = f"genklemsamp -vd {x} {y} {z} {window_path} | rcontrib -c 1000 -e MF:4 -f reinhart.cal -b rbin \
        -bn Nrbins -m {sky_mat} -faf {octree} > {dmx_output_path}"
    logger.info(command)
    os.system(command) 

def rgb2lux(rgb_path):
    """ The dctimestep result is RGB irradiance values the rcalc command above converts to lux.

    Args:
        rgb_path (string): the address of the rgb data, which were split by space.

    Returns:
        list: the illumination list.
    """
    rgb_read = open(rgb_path, "r")
    lux_list = []
    for rgb_line in rgb_read.readlines():
        rgb_data = rgb_line.split()
        lux_num = MULTIPLIER*(float(rgb_data[0])*FACTOR_R+float(rgb_data[1])*FACTOR_G \
                              +float(rgb_data[2])*FACTOR_B)
        lux_list.append(lux_num)
    return lux_list

def read_rgb_file(filename:str):
    """Read RGB file and transform it to numpy array

    Args:
        filename (string): RGB file.

    Returns:
        np.array: rgb array.
    """
    data = []
    with open(filename, 'r') as file:
        for line in file:
            values = list(map(float, line.split()))
            data.append(values)
    return np.array(data)

def rgb2lux_multi(files:List):
    """It is used in multi-windows.

    Args:
        rgb_path (List):  the list of address of the rgb data, which were split by space.
    
    Returns:
        list: the illumination list.
    """
    combined_rgb = None
    for file in files:
        rgb_data = read_rgb_file(file)
        if combined_rgb is None:
            combined_rgb = rgb_data
        else:
            combined_rgb += rgb_data
    
    # 计算lux
    lux_values = MULTIPLIER * (
        combined_rgb[:, 0] * FACTOR_R +
        combined_rgb[:, 1] * FACTOR_G +
        combined_rgb[:, 2] * FACTOR_B
    )
    
    return lux_values


def drawHotMap3D(lux_t, height, weight, add=None, bias=1):
    """draw hot map.

    Args:
        lux_t (list): list of illuminance.
        height (int): height.
        weight (int): weight.
        add (string, optional): the folder to save the hot map. Defaults to None.
        bias (int, optional): bias. Defaults to 1.
    """
    y = np.arange(0, weight, 1)
    x = np.arange(0, height-bias, 1)
    X, Y = np.meshgrid(x, y)
    lux_len = len(lux_t)
    temp = []
    for i in range(0, lux_len, height):
        temp.append(lux_t[i:i + height-bias])
    Z = np.array(temp)
    sort_temp = Z.flatten()
    sort_temp.sort()
    temp_mean = np.mean(sort_temp)
    min_list = sort_temp[0:100]
    temp_min = np.mean(min_list)
    average_degree = temp_min/temp_mean
    ax = plt.axes(projection='3d')
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap='viridis', edgecolor='none', vmax=2000)
    ax.set_zlim(0, 2000)
    ax.set_title('average degree: %.3f, mean=%.2f, min=%.2f' % (average_degree, temp_mean, temp_min))
    if add != None:
        plt.savefig(add)
        plt.clf()
    else:
        plt.show()


def date_draw(first_date):
    # 查找某时间对应的气候数据，并计算照度分布
    original_data = "data/angle_null.xlsx"
    all_data = pd.read_excel(original_data)
    date_list = all_data["Date/Time"]

    vmx_d = "rad_files/vmx/room_s_photocells_7.vmx"
    dmx_d = "rad_files/dmx/room_S.dmx"
    skv_d = "rad_files/skv/radiance_temp.skv"
    path_d = "rad_files/results/room_s_radiance_temp.dat"

    first_index = 0

    for i, item in enumerate(date_list):
        if item == first_date:
            first_index = i
            logger.info(f"Find data of {first_date}")
            break
    if first_index == 0:
        logger.error(f"No data of {first_date}")
        exit(0)
    input_data = all_data.iloc[first_index]
    diffuse_rate = input_data[3]
    direct_rate = input_data[4]
    azimuth_d = input_data[5]
    altitude_d = input_data[6]
    gen_skv_W(altitude_d, azimuth_d, direct_rate, diffuse_rate, skv_d)
    for i in range(5, 180, 5):
        xml_d = "rad_files/xml/type25_angle%s.xml" % str(i)
        dc_timestep(vmx_d, xml_d, dmx_d, skv_d, path_d)
        lux = rgb2lux(path_d)
        save_add = "results/%s.jpg" % i
        drawHotMap3D(lux, 81, 35, add=save_add, bias=0)


def radiance_test():
    # vmx = "rad_files/vmx/room_s_photocells_7.vmx"
    # xml = "rad_files/xml/type25_angle%s.xml" % ang
    # dmx = "rad_files/dmx/room_S.dmx"
    # skv = "rad_files/skv/temp.skv"
    # path = "rad_files/results/room_s_d063014_p7_a%s.dat" % ang
    ang = "null"
    vmx = ".//vmx//room.vmx"
    xml = ".//rad_files//xml//type25_angle%s.xml" % ang
    dmx = ".//dmx//room.dmx"
    skv = ".//rad_files//skv//temp.skv"
    path = ".//results/room_%s.dat" % ang
    dc_timestep(vmx, xml, dmx, skv, path)
    print("****")

    lux = rgb2lux(path)
    print(lux)
    print(len(lux))
    drawHotMap3D(lux, 2, 3, bias=0)


# dmx: daylight matrix
# vmx: view matrix
# skv: sky vector
# xml: transmission matrix
if __name__ == "__main__":
    # date = " 08/16  16:00:00"
    # date_draw(date)
    # gen_dmx("E://lijianzhuang//NewResarch//projects//new_radfiles//octrees//room.oct", 0, -1, 0, \
    #         "E://lijianzhuang//NewResarch//projects//radiance//rad_files//dmx//room.dmx")
    # gen_dmx(".\\octrees\\room.oct", 0, -1, 0, ".\\objects\\window.rad", ".\\dmx\\room.dmx")
    # a = view_matrix("./octrees/room_vmx.oct", "./rad_files/photocells/room_photocells.pts", "glazing_mat")
    # print(a)
    # radiance_test()
    dat_list = ["results\\room2windows_east.dat", "results\\room2windows_south.dat"]
    lux = rgb2lux_multi(dat_list)
    drawHotMap3D(lux, 7, 9, None, 0)
   #  print(lux)


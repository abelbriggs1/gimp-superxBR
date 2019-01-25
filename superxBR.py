#!/usr/bin/env python

from array import array
import math
from gimpfu import *

# The below code is an adaptation of Hyllian's C++ code
# from https://pastebin.com/cbH8ZQQT.

# ******* Super xBR Scaler *******
# Copyright (c) 2016 Hyllian - sergiogdb@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Absolute difference. Used for edge detection.
def abs_diff(val1, val2):
    return abs(val1 - val2)

# Clamps x to a value between floor and ceiling.
def clamp(x, floor, ceiling):
    return max(min(x, ceiling), floor)

# Easy way to return an empty 4D matrix list.
def matrix_4D():
    return [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

# Transforms an array of RGB or RGBA values into an array of single integer RGBA values.
# Since the input is RGB, alpha is assumed to be 255.
# Inputs: integer width of the picture, integer height of the picture, an RGB or RGBA pic array,
# and a flag for RGBA: true if the input is RGBA, false if RGB.
# Returns: an integer array containing RGBA values for each pixel, of size width * height
#
# (note: the following values in these examples are arbitrary)
#
# pic_arr, if RGB, is formatted in the following way:
# Indices: 0   1   2  |  3   4   5  |  6
# Values:  235 127 0  |  221 67  95 |  ...
# where the | indicates a split between pixels, and the size of the pic_arr is
# width * height * 3.
#
# pic_arr, if RGBA, is formatted in the following way:
# Indices: 0   1   2   3  |  4   5   6   7  |  8
# Values:  235 127 0   94 |  221 67  95  255|  ...
# where the | indicates a split between pixels, and the size of the pic_arr is
# width * height * 4. Note that each pixel includes a alpha value now, in 
# indices 3, 7, 11, ... etc.
def rgba_to_int(width, height, pic_arr, rgba_flag):

    int_arr_length = width * height
    # 'L' denotes a unsigned 32bit integer (rather, a long in Python)
    int_arr = array("L", [0] * int_arr_length)

    for i in range(0, int_arr_length):

        # i is where we're inserting in the new array, but we need to access
        # the old array in different places.
        if rgba_flag == True:
            # equivalent to multiplying i by 4, but this is faster.
            old_index = i << 2

            # we need to take the alpha into account.
            int_arr[i] = (pic_arr[old_index + 3] << 24) + (pic_arr[old_index + 2] << 16) + \
            (pic_arr[old_index + 1] << 8) + pic_arr[old_index]
        else:
            old_index = i * 3

            # it's RGB, so we can fudge the alpha to 255.
            int_arr[i] = (255 << 24) + (pic_arr[old_index + 2] << 16) + (pic_arr[old_index + 1] << 8) + \
            (pic_arr[old_index])
    # we have our array of single 32 bit integers, so we can just return it now.
    return int_arr

# Does the opposite of rgba_to_int - transforms the integer into an RGBA array.
# See above for the format of the RGBA array.
# The integer format is clearly defined, so this one is pretty easy.
def int_to_rgba(width, height, pic_arr):

    int_arr_length = width * height
    int_arr = array("B", "\x00" * (int_arr_length * 4))

    for i in range(0, int_arr_length):
        # we want an RGBA array, so just the bitshift this time.
        old_index = i << 2
        int_arr[old_index] = pic_arr[i] & 255
        int_arr[old_index + 1] = (pic_arr[i] >> 8) & 255
        int_arr[old_index + 2] = (pic_arr[i] >> 16) & 255
        int_arr[old_index + 3] = (pic_arr[i] >> 24) & 255
    
    return int_arr

# Pixel matrices for a given subpixel A.
#                          P1
# |P0|B |C |P1|         C     F4          |a0|b1|c2|d3|
# |D |E |F |F4|      B     F     I4       |b0|c1|d2|e3|   |e1|i1|i2|e2|
# |G |H |I |I4|   P0    E  A  I     P3    |c0|d1|e2|f3|   |e3|i3|i4|e4|
# |P2|H5|I5|P3|      D     H     I5       |d0|e1|f2|g3|
#                       G     H5
#                          P2
#
# sx, sy  
# -1  -1 | -2  0   (x+y) (x-y)    -3  1  (x+y-1)  (x-y+1)
# -1   0 | -1 -1                  -2  0
# -1   1 |  0 -2                  -1 -1
# -1   2 |  1 -3                   0 -2
#
#  0  -1 | -1  1   (x+y) (x-y)      ...     ...     ...
#  0   0 |  0  0
#  0   1 |  1 -1
#  0   2 |  2 -2
#
#  1  -1 |  0  2   ...
#  1   0 |  1  1
#  1   1 |  2  0
#  1   2 |  3 -1
#
#  2  -1 |  1  3   ...
#  2   0 |  2  2
#  2   1 |  3  1
#  2   2 |  4  0

# Calculates diagonal edge value from pixel matrix (mat) and pixel weightings (wp)
def diagonal_edge(mat, wp):
    diagonal_weight1 = wp[0] * (abs_diff(mat[0][2], mat[1][1]) + abs_diff(mat[1][1], mat[2][0]) + \
    abs_diff(mat[1][3], mat[2][2]) + abs_diff(mat[2][2], mat[3][1])) + \
    wp[1] * (abs_diff(mat[0][3], mat[1][2]) + abs_diff(mat[2][1], mat[3][0])) + \
    wp[2] * (abs_diff(mat[0][3], mat[2][1]) + abs_diff(mat[1][2], mat[3][0])) + \
    wp[3] * (abs_diff(mat[1][2], mat[2][1])) + \
    wp[4] * (abs_diff(mat[0][2], mat[2][0]) + abs_diff(mat[1][3], mat[3][1])) + \
    wp[5] * (abs_diff(mat[0][1], mat[1][0]) + abs_diff(mat[2][3], mat[3][2]))

    diagonal_weight2 = wp[0] * (abs_diff(mat[0][1], mat[1][2]) + abs_diff(mat[1][2], mat[2][3]) + \
    abs_diff(mat[1][0], mat[2][1]) + abs_diff(mat[2][1], mat[3][2])) + \
    wp[1] * (abs_diff(mat[0][0], mat[1][1]) + abs_diff(mat[2][2], mat[3][3])) + \
    wp[2] * (abs_diff(mat[0][0], mat[2][2]) + abs_diff(mat[1][1], mat[3][3])) + \
    wp[3] * (abs_diff(mat[1][1], mat[2][2])) + \
    wp[4] * (abs_diff(mat[1][0], mat[3][2]) + abs_diff(mat[0][1], mat[2][3])) + \
    wp[5] * (abs_diff(mat[0][2], mat[1][3]) + abs_diff(mat[2][0], mat[3][1]))

    return (diagonal_weight1 - diagonal_weight2)

def python_superxBR(timg, tdrawable, scale_factor = 2):

    # don't bother if the scale factor isn't a power of 2.
    if scale_factor == 0 or (scale_factor & (scale_factor - 1)) != 0:
        gimp.progress_init("Error: scale factor not a power of 2. Exiting...")
        return

    # constants for the algorithm
    WEIGHT1 = 0.129633
    WEIGHT2 = 0.175068
    w1 = -WEIGHT1
    w2 = WEIGHT1 + 0.500000
    w3 = -WEIGHT2
    w4 = WEIGHT2 + 0.500000

    # Relative luminance coefficients: https://en.wikipedia.org/wiki/Luma_(video)
    LUMA_R = 0.2126
    LUMA_G = 0.7152
    LUMA_B = 0.0722 

    gimp.context_push()
    timg.undo_group_start()

    original_width = tdrawable.width
    original_height = tdrawable.height

    out_width = original_width * scale_factor
    out_height = original_height * scale_factor

    original_pixel_region = tdrawable.get_pixel_rgn(0, 0, original_width, original_height, False, False)
    
    original_pixel_data = array("B", original_pixel_region[0:original_width, 0:original_height])

    # True if the pixel data is RGBA, false if it's RGB and needs alpha to be fudged.
    rgba_flag = (tdrawable.type == RGBA_IMAGE) 
    
    original_pixel_data = rgba_to_int(original_width, original_height, original_pixel_data, rgba_flag)

    dest_drawable = gimp.Layer(timg, "scaled", out_width, out_height, RGBA_IMAGE, 100, NORMAL_MODE)
    dest_region = dest_drawable.get_pixel_rgn(0, 0, out_width, out_height, True, True)
    
    output_data = array("L", [0L] * (out_width * out_height))

    # - - - - - Super-xBR Scaling - - - - -
    # First pass begins here
    # Pixel weightings for pass 1.
    gimp.progress_init("Running first pass of Super-xBR on " + tdrawable.name + "...")

    weight_pixel = [2.0, 1.0, -1.0, 4.0, -1.0, 1.0]

    red = matrix_4D()
    green = matrix_4D()
    blue = matrix_4D()
    alpha = matrix_4D()
    Y_luma = matrix_4D()

    # "f" variables are floating point, while "i" variables are meant to be integers.
    # r/g/b/a correspond to red, green, blue, and alpha values respectively.
    rf, gf, bf, af, ri, gi, bi, ai = (None,) * 8
    d_edge = None
    min_r_sample, max_r_sample = None, None
    min_g_sample, max_g_sample = None, None
    min_b_sample, max_b_sample = None, None
    min_a_sample, max_a_sample = None, None

    for y in range(0, out_height, 2):
        for x in range(0, out_width, 2):

            # central pixels on original image: cx and cy
            cx = x / scale_factor
            cy = y / scale_factor

            # sample supporting pixels on original image: sx and sy
            for sx in range(-1, 3):
                for sy in range(-1, 3):

                    # clamp the pixel locations.
                    csy = clamp(sy + cy, 0, original_height - 1)
                    csx = clamp(sx + cx, 0, original_width - 1)

                    # sample and add weighted components
                    sample = original_pixel_data[csy * original_width + csx]
                    red[sx + 1][sy + 1] = ((sample) >> 0) & 0xFF
                    green[sx + 1][sy + 1] = ((sample) >> 8) & 0xFF
                    blue[sx + 1][sy + 1] = ((sample) >> 16) & 0xFF
                    alpha[sx + 1][sy + 1] = ((sample) >> 24) & 0xFF
                    Y_luma[sx + 1][sy + 1] = (LUMA_R * red[sx + 1][sy + 1] + \
                    LUMA_G * green[sx + 1][sy + 1] + LUMA_B * blue[sx + 1][sy + 1])
            
            min_r_sample = min(red[1][1], red[2][1], red[1][2], red[2][2])
            min_g_sample = min(green[1][1], green[2][1], green[1][2], green[2][2])
            min_b_sample = min(blue[1][1], blue[2][1], blue[1][2], blue[2][2])
            min_a_sample = min(alpha[1][1], alpha[2][1], alpha[1][2], alpha[2][2])

            max_r_sample = max(red[1][1], red[2][1], red[1][2], red[2][2])
            max_g_sample = max(green[1][1], green[2][1], green[1][2], green[2][2])
            max_b_sample = max(blue[1][1], blue[2][1], blue[1][2], blue[2][2])
            max_a_sample = max(alpha[1][1], alpha[2][1], alpha[1][2], alpha[2][2])

            d_edge = diagonal_edge(Y_luma, weight_pixel)
            
            if d_edge <= 0:
                rf = w1 * (red[0][3] + red[3][0]) + w2 * (red[1][2] + red[2][1])
                gf = w1 * (green[0][3] + green[3][0]) + w2 * (green[1][2] + green[2][1])
                bf = w1 * (blue[0][3] + blue[3][0]) + w2 * (blue[1][2] + blue[2][1])
                af = w1 * (alpha[0][3] + alpha[3][0]) + w2 * (alpha[1][2] + alpha[2][1])
            else:
                rf = w1 * (red[0][0] + red[3][3]) + w2 * (red[1][1] + red[2][2])
                gf = w1 * (green[0][0] + green[3][3]) + w2 * (green[1][1] + green[2][2])
                bf = w1 * (blue[0][0] + blue[3][3]) + w2 * (blue[1][1] + blue[2][2])
                af = w1 * (alpha[0][0] + alpha[3][3]) + w2 * (alpha[1][1] + alpha[2][2])

            # clamp to prevent ringing artifacts: https://en.wikipedia.org/wiki/Ringing_artifacts
            rf = clamp(rf, min_r_sample, max_r_sample)
            gf = clamp(gf, min_g_sample, max_g_sample)
            bf = clamp(bf, min_b_sample, max_b_sample)
            af = clamp(af, min_a_sample, max_a_sample)
            # need to be integers so we can do bitwise operations on these variables later
            ri = int(clamp(math.ceil(rf), 0, 255))
            gi = int(clamp(math.ceil(gf), 0, 255))
            bi = int(clamp(math.ceil(bf), 0, 255))
            ai = int(clamp(math.ceil(af), 0, 255))

            # write to data
            output_data[y * out_width + x] = output_data[y * out_width + x + 1] = \
            output_data[(y + 1) * out_width + x] = original_pixel_data[cy * original_width + cx]
            output_data[(y + 1) * out_width + x + 1] = (ai << 24) | (bi << 16) | (gi << 8) | ri
        gimp.progress_update(float(y)/out_height)
    
    # Second pass
    gimp.progress_init("Running second pass of Super-xBR on " + tdrawable.name + "...")

    weight_pixel[0] = 2.0
    weight_pixel[1] = 0.0
    weight_pixel[2] = 0.0
    weight_pixel[3] = 0.0
    weight_pixel[4] = 0.0
    weight_pixel[5] = 0.0

    for y in range(0, out_height, 2):
        for x in range(0, out_width, 2):
            # sample supporting pixels in original image
            for sx in range(-1, 3):
                for sy in range(-1, 3):

                    # clamp pixel locations
                    csy = clamp(sx - sy + y, 0, scale_factor * original_height - 1)
                    csx = clamp(sx + sy + x, 0, scale_factor * original_width - 1)

                    # sample and add weighted components
                    sample = output_data[csy * out_width + csx]
                    red[sx + 1][sy + 1] = ((sample) >> 0) & 0xFF
                    green[sx + 1][sy + 1] = ((sample) >> 8) & 0xFF
                    blue[sx + 1][sy + 1] = ((sample) >> 16) & 0xFF
                    alpha[sx + 1][sy + 1] = ((sample) >> 24) & 0xFF
                    Y_luma[sx + 1][sy + 1] = (LUMA_R * red[sx + 1][sy + 1] + \
                    LUMA_G * green[sx + 1][sy + 1] + LUMA_B * blue[sx + 1][sy + 1])
            
            min_r_sample = min(red[1][1], red[2][1], red[1][2], red[2][2])
            min_g_sample = min(green[1][1], green[2][1], green[1][2], green[2][2])
            min_b_sample = min(blue[1][1], blue[2][1], blue[1][2], blue[2][2])
            min_a_sample = min(alpha[1][1], alpha[2][1], alpha[1][2], alpha[2][2])

            max_r_sample = max(red[1][1], red[2][1], red[1][2], red[2][2])
            max_g_sample = max(green[1][1], green[2][1], green[1][2], green[2][2])
            max_b_sample = max(blue[1][1], blue[2][1], blue[1][2], blue[2][2])
            max_a_sample = max(alpha[1][1], alpha[2][1], alpha[1][2], alpha[2][2])

            d_edge = diagonal_edge(Y_luma, weight_pixel)

            if d_edge <= 0:
                rf = w3 * (red[0][3] + red[3][0]) + w4 * (red[1][2] + red[2][1])
                gf = w3 * (green[0][3] + green[3][0]) + w4 * (green[1][2] + green[2][1])
                bf = w3 * (blue[0][3] + blue[3][0]) + w4 * (blue[1][2] + blue[2][1])
                af = w3 * (alpha[0][3] + alpha[3][0]) + w4 * (alpha[1][2] + alpha[2][1])
            else:
                rf = w3 * (red[0][0] + red[3][3]) + w4 * (red[1][1] + red[2][2])
                gf = w3 * (green[0][0] + green[3][3]) + w4 * (green[1][1] + green[2][2])
                bf = w3 * (blue[0][0] + blue[3][3]) + w4 * (blue[1][1] + blue[2][2])
                af = w3 * (alpha[0][0] + alpha[3][3]) + w4 * (alpha[1][1] + alpha[2][2])
            
            # clamp to prevent ringing artifacts: https://en.wikipedia.org/wiki/Ringing_artifacts
            rf = clamp(rf, min_r_sample, max_r_sample)
            gf = clamp(gf, min_g_sample, max_g_sample)
            bf = clamp(bf, min_b_sample, max_b_sample)
            af = clamp(af, min_a_sample, max_a_sample)
            # need to be integers so we can do bitwise operations on these variables later
            ri = int(clamp(math.ceil(rf), 0, 255))
            gi = int(clamp(math.ceil(gf), 0, 255))
            bi = int(clamp(math.ceil(bf), 0, 255))
            ai = int(clamp(math.ceil(af), 0, 255))
            output_data[y * out_width + x + 1] = (ai << 24) | (bi << 16) | (gi << 8) | ri

            for sx in range(-1, 3):
                for sy in range(-1, 3):

                    # clamp pixel locations
                    csy = clamp(sx - sy + 1 + y, 0, scale_factor * original_height - 1)
                    csx = clamp(sx + sy - 1 + x, 0, scale_factor * original_width - 1)

                    # sample and add weighted components
                    sample = output_data[csy * out_width + csx]
                    red[sx + 1][sy + 1] = ((sample) >> 0) & 0xFF
                    green[sx + 1][sy + 1] = ((sample) >> 8) & 0xFF
                    blue[sx + 1][sy + 1] = ((sample) >> 16) & 0xFF
                    alpha[sx + 1][sy + 1] = ((sample) >> 24) & 0xFF
                    Y_luma[sx + 1][sy + 1] = (LUMA_R * red[sx + 1][sy + 1] + \
                    LUMA_G * green[sx + 1][sy + 1] + LUMA_B * blue[sx + 1][sy + 1])
            
            d_edge = diagonal_edge(Y_luma, weight_pixel)

            if d_edge <= 0:
                rf = w3 * (red[0][3] + red[3][0]) + w4 * (red[1][2] + red[2][1])
                gf = w3 * (green[0][3] + green[3][0]) + w4 * (green[1][2] + green[2][1])
                bf = w3 * (blue[0][3] + blue[3][0]) + w4 * (blue[1][2] + blue[2][1])
                af = w3 * (alpha[0][3] + alpha[3][0]) + w4 * (alpha[1][2] + alpha[2][1])
            else:
                rf = w3 * (red[0][0] + red[3][3]) + w4 * (red[1][1] + red[2][2])
                gf = w3 * (green[0][0] + green[3][3]) + w4 * (green[1][1] + green[2][2])
                bf = w3 * (blue[0][0] + blue[3][3]) + w4 * (blue[1][1] + blue[2][2])
                af = w3 * (alpha[0][0] + alpha[3][3]) + w4 * (alpha[1][1] + alpha[2][2])
            
            # clamp to prevent ringing artifacts: https://en.wikipedia.org/wiki/Ringing_artifacts
            rf = clamp(rf, min_r_sample, max_r_sample)
            gf = clamp(gf, min_g_sample, max_g_sample)
            bf = clamp(bf, min_b_sample, max_b_sample)
            af = clamp(af, min_a_sample, max_a_sample)
            # need to be integers so we can do bitwise operations on these variables later
            ri = int(clamp(math.ceil(rf), 0, 255))
            gi = int(clamp(math.ceil(gf), 0, 255))
            bi = int(clamp(math.ceil(bf), 0, 255))
            ai = int(clamp(math.ceil(af), 0, 255))
            output_data[(y + 1) * out_width + x] = (ai << 24) | (bi << 16) | (gi << 8) | ri
        gimp.progress_update(float(y)/out_height)

    
    # Third pass
    gimp.progress_init("Running third pass of Super-xBR on " + tdrawable.name + "...")

    weight_pixel[0] = 2.0
    weight_pixel[1] = 1.0
    weight_pixel[2] = -1.0
    weight_pixel[3] = 4.0
    weight_pixel[4] = -1.0
    weight_pixel[5] = 1.0

    for y in range(out_height - 1, -1, -1):
        for x in range(out_width - 1, -1, -1):
            for sx in range(-2, 2):
                for sy in range(-2, 2):
                    
                    # clamp pixel locations
                    csy = clamp(sy + y, 0, scale_factor * original_height - 1)
                    csx = clamp(sx + x, 0, scale_factor * original_width - 1)
                    
                    # sample and add weighted components
                    sample = output_data[csy * out_width + csx]
                    red[sx + 2][sy + 2] = ((sample) >> 0) & 0xFF
                    green[sx + 2][sy + 2] = ((sample) >> 8) & 0xFF
                    blue[sx + 2][sy + 2] = ((sample) >> 16) & 0xFF
                    alpha[sx + 2][sy + 2] = ((sample) >> 24) & 0xFF
                    Y_luma[sx + 2][sy + 2] = (LUMA_R * red[sx + 2][sy + 2] + \
                    LUMA_G * green[sx + 2][sy + 2] + LUMA_B * blue[sx + 2][sy + 2])
            
            min_r_sample = min(red[1][1], red[2][1], red[1][2], red[2][2])
            min_g_sample = min(green[1][1], green[2][1], green[1][2], green[2][2])
            min_b_sample = min(blue[1][1], blue[2][1], blue[1][2], blue[2][2])
            min_a_sample = min(alpha[1][1], alpha[2][1], alpha[1][2], alpha[2][2])

            max_r_sample = max(red[1][1], red[2][1], red[1][2], red[2][2])
            max_g_sample = max(green[1][1], green[2][1], green[1][2], green[2][2])
            max_b_sample = max(blue[1][1], blue[2][1], blue[1][2], blue[2][2])
            max_a_sample = max(alpha[1][1], alpha[2][1], alpha[1][2], alpha[2][2])

            d_edge = diagonal_edge(Y_luma, weight_pixel)

            if d_edge <= 0:
                rf = w1 * (red[0][3] + red[3][0]) + w2 * (red[1][2] + red[2][1])
                gf = w1 * (green[0][3] + green[3][0]) + w2 * (green[1][2] + green[2][1])
                bf = w1 * (blue[0][3] + blue[3][0]) + w2 * (blue[1][2] + blue[2][1])
                af = w1 * (alpha[0][3] + alpha[3][0]) + w2 * (alpha[1][2] + alpha[2][1])
            else:
                rf = w1 * (red[0][0] + red[3][3]) + w2 * (red[1][1] + red[2][2])
                gf = w1 * (green[0][0] + green[3][3]) + w2 * (green[1][1] + green[2][2])
                bf = w1 * (blue[0][0] + blue[3][3]) + w2 * (blue[1][1] + blue[2][2])
                af = w1 * (alpha[0][0] + alpha[3][3]) + w2 * (alpha[1][1] + alpha[2][2])
            
            # clamp to prevent ringing artifacts: https://en.wikipedia.org/wiki/Ringing_artifacts
            rf = clamp(rf, min_r_sample, max_r_sample)
            gf = clamp(gf, min_g_sample, max_g_sample)
            bf = clamp(bf, min_b_sample, max_b_sample)
            af = clamp(af, min_a_sample, max_a_sample)
            # need to be integers so we can do bitwise operations on these variables later
            ri = int(clamp(math.ceil(rf), 0, 255))
            gi = int(clamp(math.ceil(gf), 0, 255))
            bi = int(clamp(math.ceil(bf), 0, 255))
            ai = int(clamp(math.ceil(af), 0, 255))
            output_data[y * out_width + x] = (ai << 24) | (bi << 16) | (gi << 8) | ri
        gimp.progress_update(float((out_height - 1) - y)/out_height)

    # --- end super-XBR code ---
    output_data = int_to_rgba(out_width, out_height, output_data)

    pdb.gimp_image_resize(timg, out_width, out_height, 0, 0)

    timg.add_layer(dest_drawable, 0)
    dest_region[0:out_width, 0:out_height] = output_data.tostring()

    dest_drawable.flush()
    dest_drawable.merge_shadow(True)
    dest_drawable.update(0, 0, out_width, out_height)

    timg.flatten()

    timg.undo_group_end()
    gimp.context_pop()

register(
    "python_superxBR",
    "Integer scales an image by a power of 2 using Hyllian's Super-xBR",
    "Integer scales an image by a power of 2 using Hyllian's Super-xBR",
    "Abel Briggs",
    "Hyllian",
    "2019",
    "<Image>/Filters/Enhance/Super-xBR(py)...",
    "RGB, RGBA",
    [
        (PF_INT, "scale_factor", "Scale factor(2, 4, 8, 16, etc.)", 2)
    ],
    [],
    python_superxBR)

main()

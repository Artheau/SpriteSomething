import math  # for gcd
import itertools
import os
import struct
import re

try:
    import numpy as np
    from PIL import Image, ImageChops
except ModuleNotFoundError as e:
    print(e)


def equal(image1, image2):
    # are these images the same?
    return ImageChops.difference(image1, image2).getbbox() is None


def lcm(x, y):
    # least common multiple
    return x * y // math.gcd(x, y)


def filename_scrub(filename):
    # clean filenames
    # prevents untowards things like spaces in filenames,
    #  to improve compatibility
    new_filename = str(filename).lower()
    new_filename = re.sub(r" ", "-", new_filename)  # no spaces
    # no weird things in the name
    new_filename = re.sub(r"[\%\$\^\:\']", "", new_filename)
    # no weird things at beginning of name
    new_filename = re.sub(r"^[^A-Za-z0-9]+", "", new_filename)

    return new_filename


def get_all_resources(subdir=None, desired_filename=None):
    # get all resources from app folder & user folder
    file_list = []

    if subdir is not None and desired_filename is None:
        desired_filename = subdir
        subdir = "./"

    if isinstance(subdir, list):
        subdir = os.path.join(*subdir)

    # gets the file from user_resources AND app_resources
    #  (returns a list of filenames)
    for directory in [
        os.path.join("resources", "user"),
        os.path.join("resources", "app")
    ]:
        if subdir:
            directory = os.path.join(directory, subdir)
        if os.path.isdir(directory):
            for filename in os.listdir(directory):
                if filename == desired_filename:
                    file_list.append(os.path.join(directory, filename))

    return file_list


def get_resource(subdir=None, desired_filename=None):
    # gets the file from overrides.  If not there, then from resources.
    if subdir is not None and desired_filename is None:
        desired_filename = subdir
        subdir = "./"

    if isinstance(subdir, list):
        subdir = os.path.join(*subdir)

    file_list = get_all_resources(subdir, desired_filename)
    if not file_list and "arrow-" not in desired_filename and "-thing" not in desired_filename:
        print(subdir, desired_filename, "not found!")
    return file_list[0] if file_list else None


def gather_all_from_resource_subdirectory(subdir):
    # gathers all the filenames from a subdirectory in resources,
    # and then also throws in all the filenames from the same
    #  subdirectory in overrides
    # does not recurse
    file_list = []
    for directory in [
        os.path.join("resources", "app"),
        os.path.join("resources", "user")
    ]:
        directory = os.path.join(directory, subdir)
        if os.path.isdir(directory):
            for filename in os.listdir(directory):
                if os.path.isfile(os.path.join(directory, filename)):
                    # just the filename, not the path,
                    #  so that this overrrides correctly
                    file_list.append(filename)
    return file_list


def apply_palette(image, palette):
    # apply a palette to an image
    if image is None:
        pass
        # print("Not a valid image to apply palette to!")
    if palette:
        if len(palette) < 1:
            image = image.convert('RGBA')
            return image
            # print("Not a valid palette to apply!")
        if image.mode == "P":
            flat_palette = [0 for _ in range(3 * 256)]
            flat_palette[3:3 * len(palette) +
                         3] = [x for color in palette for x in color]
            alpha_mask = image.point(lambda x: 0 if x == 0 else 1, mode="1")
            image.putpalette(flat_palette)
            image = image.convert('RGBA')
            image.putalpha(alpha_mask)
    return image


def reduce_to_nearest_eighth(val):
    # take a value, divide by 8, floor it
    return int(val) // 8


def snescolor_eighth(val):
    # take a value, divide by 8, floor it, constrain it
    return max(0, min(31, reduce_to_nearest_eighth(val)))


def round_to_nearest_eight(val):
    # take a value, divide by 8, floor it, contrain it, mult by 8
    return snescolor_eighth(val) * 8


def convert_555_to_rgb(color, recurse=True):
    # converts either a single color or a list of colors in 555 format to
    #  their RGB 3-tuple equivalents
    try:
        iter(color)
    except TypeError:
        FIVE_BITS = 0b100000
        red = 8 * (color % FIVE_BITS)
        green = 8 * ((color // FIVE_BITS) % FIVE_BITS)
        blue = 8 * ((color // (FIVE_BITS * FIVE_BITS)) % FIVE_BITS)
        return (red, green, blue)
    # else it is iterable
    if recurse:
        return [convert_555_to_rgb(x, recurse=False) for x in color]
    # FIXME: English
    raise AssertionError(
        "convert_555_to_rgb() called with doubly-iterable argument")


def convert_to_555(palette):
    # expects (r,g,b) tuples in a list, returns big endian 2-byte colors in a list
    return [single_convert_to_555(color) for color in palette]


def single_convert_to_555(color):
    # expects an (r,g,b) tuple, returns a big endian 2-byte value
    red, green, blue = [snescolor_eighth(x) for x in color]
    return (blue * 1024) + \
        (green * 32) + \
        (red)


def image_from_raw_data(tilemaps, DMA_writes, bounding_box):
    # expects:
    #  a list of tilemaps in the 5 byte format: essentially [
    #                                                        X position,
    #                                                        size + Xmsb,
    #                                                        Y,
    #                                                        index,
    #                                                        palette + indexmsb
    #                                                       ]
    #  a dictionary consisting of writes to the DMA and what should be there

    canvas = {}

    for tilemap in tilemaps:
        # tilemap[0] and the 0th bit of tilemap[1] encode the X offset
        x_offset = tilemap[0] - (0x100 if (tilemap[1] & 0x01) else 0)

        # tilemap[1] also contains information about whether the tile is
        #  8x8 or 16x16
        big_tile = (tilemap[1] & 0x80 == 0x80)

        # tilemap[2] contains the Y offset
        y_offset = (tilemap[2] & 0x7F) - (0x80 if (tilemap[2] & 0x80) else 0)

        # tilemap[3] contains the index of which tile to grab
        #  (or tiles in the case of a 16x16)
        # tilemap[4] also contains one bit of the same index,
        #  used to reference deep in OAM
        index = tilemap[3] + (0x100 if tilemap[4] & 0x01 else 0)

        # tilemap[4] contains palette info, priority info, and flip info
        v_flip = tilemap[4] & 0x80
        h_flip = tilemap[4] & 0x40
        # priority = (tilemap[4] //0x10) % 0b100  # TODO: implement a priority
        # palette = (tilemap[4] //2) % 0b1000     #  system in theory, the
        #                                            palette index here could
        #                                            be used to render if we
        #                                            wanted a ROM-dependent
        #                                            implementation

        def draw_tile_to_canvas(new_x_offset, new_y_offset, new_index):
            tile_to_write = convert_tile_from_bitplanes(DMA_writes[new_index])
            if h_flip:
                tile_to_write = np.flipud(tile_to_write)
            if v_flip:
                tile_to_write = np.fliplr(tile_to_write)
            for (i, j), value in np.ndenumerate(tile_to_write):
                if value != 0:  # if not transparent
                    canvas[(new_x_offset + i, new_y_offset + j)] = int(value)

        if big_tile:  # draw all four 8x8 tiles
            draw_tile_to_canvas(x_offset + (8 if h_flip else 0),
                                y_offset + (8 if v_flip else 0), index)
            draw_tile_to_canvas(x_offset + (0 if h_flip else 8),
                                y_offset + (8 if v_flip else 0), index + 0x01)
            draw_tile_to_canvas(x_offset + (8 if h_flip else 0),
                                y_offset + (0 if v_flip else 8), index + 0x10)
            draw_tile_to_canvas(x_offset + (0 if h_flip else 8),
                                y_offset + (0 if v_flip else 8), index + 0x11)
        else:
            draw_tile_to_canvas(x_offset, y_offset, index)

    tight_image, (x0, y0) = to_image(canvas)
    cropped_image = tight_image.crop(
        (
            bounding_box[0] + x0,
            bounding_box[1] + y0,
            bounding_box[2] + x0,
            bounding_box[3] + y0
        )
    )

    return cropped_image


def to_image(canvas):

    if canvas.keys():
        x_min = min([x for (x, y) in canvas.keys()])
        y_min = min([y for (x, y) in canvas.keys()])
        x_max = max([x for (x, y) in canvas.keys()])
        y_max = max([y for (x, y) in canvas.keys()])

        x_min = min(x_min, 0)
        y_min = min(y_min, 0)
        x_max = max(x_max, 0)
        y_max = max(y_max, 0)

        width = x_max - x_min + 1
        height = y_max - y_min + 1

        image = Image.new("P", (width, height), 0)

        pixels = image.load()

        for (i, j), value in canvas.items():
            pixels[(i - x_min, j - y_min)] = value

    else:  # the canvas is empty
        image = Image.new("P", (1, 1), 0)
        x_min, y_min = 0, 0

    return image, (-x_min, -y_min)


def convert_tile_from_bitplanes(raw_tile):
    # an attempt to make this ugly process mildly efficient
    tile = np.zeros((8, 8), dtype=np.uint8)

    tile[:, 4] = raw_tile[31:15:-2]
    tile[:, 5] = raw_tile[30:14:-2]
    tile[:, 6] = raw_tile[15::-2]
    tile[:, 7] = raw_tile[14::-2]

    shaped_tile = tile.reshape(8, 8, 1)

    tile_bits = np.unpackbits(shaped_tile, axis=2)
    fixed_bits = np.packbits(tile_bits, axis=1)
    returnvalue = fixed_bits.reshape(8, 8)
    returnvalue = returnvalue.swapaxes(0, 1)
    returnvalue = np.fliplr(returnvalue)
    return returnvalue


def image_from_bitplanes(raw_tile):
    # fromarray expects column major format, so have to switch the axes
    if raw_tile:
        return Image.fromarray(
            convert_tile_from_bitplanes(raw_tile).swapaxes(0, 1),
            'P'
        )


def convert_to_4bpp(image, offset, dimensions, extra_area):
    # have to process these differently so that 16x16 tiles canbe correctly
    #  reconstructed
    # print(image.mode, image.name, image.size)
    if image.mode != "P":
        image = image.convert('P')
    top_row = []
    bottom_row = []
    small_tiles = []
    for bounding_box in itertools.chain(
        [dimensions], extra_area if extra_area else []
    ):
        xmin, ymin, xmax, ymax = bounding_box
        xmin += offset[0]
        ymin += offset[1]
        xmax += offset[0]
        ymax += offset[1]
        w = image.size[0]
        h = image.size[1]
        # print(f"({w},{h})")
        x_chad_length = (xmax - xmin) % 16
        y_chad_length = (ymax - ymin) % 16
        for y in range(ymin, ymax - 15, 16):
            for x in range(xmin, xmax - 15, 16):
                # make a 16x16 tile from (x,y)
                # tuples in left-up-right-bottom format
                #  (it's ok if this crops an area not completely in the image)
                top_row.extend(get_single_raw_tile(
                    image.crop((x, y, x + 8, y + 8))))
                top_row.extend(get_single_raw_tile(
                    image.crop((x + 8, y, x + 16, y + 8))))
                bottom_row.extend(get_single_raw_tile(
                    image.crop((x, y + 8, x + 8, y + 16))))
                bottom_row.extend(get_single_raw_tile(
                    image.crop((x + 8, y + 8, x + 16, y + 16))))
            # check to see if xmax-xmin has a hanging chad
            if x_chad_length == 0:
                pass  # no chad
            elif x_chad_length == 8:
                # make two 8x8 tiles from (chad,y), (chad,y+8)
                small_tiles.extend(get_single_raw_tile(
                    image.crop((xmax - 8, y, xmax, y + 8))))
                small_tiles.extend(get_single_raw_tile(
                    image.crop((xmax - 8, y + 8, xmax, y + 16))))
            else:
                # FIXME: English
                raise AssertionError(
                    f"received call to get_raw_pose() for image" + " " +
                    f"'{image.name}' but the dimensions for x" + " " +
                    f"({xmin},{xmax}) are not divisible by 8")
        # check to see if ymax-ymin has hanging chads
        if y_chad_length == 0:
            pass  # cool
        elif y_chad_length == 8:
            for x in range(xmin, xmax - 15, 16):
                # construct the big chads first from (x,chad), (x+8,chad)
                small_tiles.extend(get_single_raw_tile(
                    image.crop((x, ymax - 8, x + 8, ymax))))
                small_tiles.extend(get_single_raw_tile(
                    image.crop((x + 8, ymax - 8, x + 16, ymax))))
            # now check for the bottom right chad
            y_chad_length = ymax - ymin % 16
            if x_chad_length == 0:
                pass  # cool
            elif x_chad_length == 8:
                # make the final chad
                small_tiles.extend(get_single_raw_tile(
                    image.crop((xmax - 8, ymax - 8, xmax, ymax))))
            else:
                # FIXME: English
                raise AssertionError(
                    f"received call to get_raw_pose() for image" + ' ' +
                    f"'{image.name}' but the dimensions for x" + ' ' +
                    f"({xmin},{xmax}) are not divisible by 8")
        else:
            raise AssertionError(
                f"received call to get_raw_pose() for image" + ' ' +
                f"'{image.name}' but the dimensions for y" + ' ' +
                f"({xmin},{xmax}) are not divisible by 8")

    # even out the small tiles into the rest of the space
    for pos in range(0, len(small_tiles), 0x40):
        top_row.extend(small_tiles[pos:pos + 0x20])
        bottom_row.extend(small_tiles[pos + 0x20:pos + 0x40])

    return top_row + bottom_row


def get_single_raw_tile(image):
    # Here transpose() is used because otherwise we get column-major
    #  format in getdata(), which is not helpful
    return convert_indexed_tile_to_bitplanes(
        image.transpose(Image.TRANSPOSE).getdata()
    )


def convert_indexed_tile_to_bitplanes(indexed_tile):
    # this should literally just be the inverse of
    #  convert_tile_from_bitplanes(), and so it was written in this way
    indexed_tile = np.array(indexed_tile, dtype=np.uint8).reshape(8, 8)
    indexed_tile = np.fliplr(indexed_tile)
    indexed_tile = indexed_tile.swapaxes(0, 1)
    # in the opposite direction, this had axis=1 collapsed
    fixed_bits = indexed_tile.reshape(8, 1, 8)
    tile_bits = np.unpackbits(fixed_bits, axis=1)
    shaped_tile = np.packbits(tile_bits, axis=2)
    tile = shaped_tile.reshape(8, 8)
    low_bitplanes = np.ravel(tile[:, 6:8])[::-1]
    high_bitplanes = np.ravel(tile[:, 4:6])[::-1]
    return np.append(low_bitplanes, high_bitplanes)


def pretty_hex(x, digits=2):
    # displays a hex number with a specified number of digits
    return '0x' + hex(x)[2:].upper().zfill(digits)


def palette_pull_towards_color(palette, pull_color, bias):
    # pull palette colors toward specified color
    return [
        tuple(
            x * (1 - bias) + (y * bias) for x, y in zip(color, pull_color)
        ) for color in palette
    ]


def palette_shift(palette, shift_delta):
    # shift palette by number
    return [
        tuple(
            x + y for x, y in zip(color, shift_delta)
        ) for color in palette
    ]


def grayscale(palette):
    # grayscale a palette
    gray_palette = []
    for (r, g, b) in palette:
        # x = 0.21 * r + 0.72 * g + 0.07 * b  # luminosity formula attempt
        x = 0.31 * r + 0.52 * g + 0.17 * b    # modified luminosity
        # x = (r + g + b) // 3                # rote averaging
        gray_palette.append((x, x, x))
    max_visor = max(palette[3])
    # visor should be essentially white (as bright as the brightest color)
    gray_palette[3] = (max_visor, max_visor, max_visor)
    return gray_palette


def sepia(palette):
    # grayscale and sepia
    return [(r, g, b * 13.0 / 16.0) for (r, g, b) in grayscale(palette)]


def as_u8(value):
    # return unsigned 8bit
    return struct.pack('B', value)


def as_u16(value):
    # return unsigned 16bit
    return struct.pack('<H', value)


def as_u32(value):
    # return unsigned 32bit
    return struct.pack('<L', value)


def from_u8(buffer):
    # returns a tuple with "quantity" number of elements
    return struct.unpack_from('B', buffer)[0]


def from_u16(buffer):
    # returns a tuple with "quantity" number of elements
    return struct.unpack_from('<H', buffer)[0]


def from_u32(buffer):
    # returns a tuple with "quantity" number of elements
    return struct.unpack_from('<L', buffer)[0]


def main():
    print(f"Called main() on utility library {__file__}")


if __name__ == "__main__":
    main()

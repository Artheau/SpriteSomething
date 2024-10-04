# originally written by Artheau
# with Darmok and Jalad at Tanagra
# in April of 2019

# this file contains various helper functions which facilitate the
# construction of the PNG layout files

import itertools
import json
import os
from json.decoder import JSONDecodeError
from PIL import Image, ImageOps, ImageDraw
from source.meta.common import common


class Layout():
    def __init__(self, filename, sprite_name=""):
        layout_path = filename.replace(os.sep, '/')
        layout_path = layout_path[layout_path.find("app/")+len("app/"):]
        if not filename or not os.path.isfile(filename):
            raise AssertionError(f"Layout not found: {layout_path}")
        with open(filename) as inFile:
            self.data = []
            try:
                self.data = json.load(inFile)
            except JSONDecodeError as e:
                raise ValueError("Layout manifest malformed: " + filename)
        self.reverse_lookup = {}
        print(f"Finding Layouts! [{layout_path.replace('/manifests/layout.json','')}]")
        if "layouts" in self.data:
            for layout in self.data["layouts"]:
                if "names" in layout and sprite_name in layout["names"]:
                    print(f"Found {sprite_name}!")
                    self.data = layout
        for image_name,image_info in self.data["images"].items():
            if "used by" in image_info:
                for image_ref in image_info["used by"]:
                    if tuple(image_ref) in self.reverse_lookup:
                        self.reverse_lookup[tuple(image_ref)].append(image_name)
                    else:
                        self.reverse_lookup[tuple(image_ref)] = [image_name]
        self.filename = filename
        self.subtype = None

    def get_image_name(self, animation, pose, force=None):
        if type(animation) is int:
            animation = common.pretty_hex(animation)

        image_name_list = self.get_all_image_names(animation,pose)
        if image_name_list:
            if force:
                for image_name in image_name_list:
                    if self.get_property("force",image_name) == force.lower():
                        return image_name
                else:
                    return "null"
            else:
                #get any old image name from reverse lookup
                return image_name_list[0]
        else:
            return "null"

    def get_all_image_names(self,animation, pose):
        if type(animation) is int:
            animation = common.pretty_hex(animation)
        #get the full list
        return self.reverse_lookup[(animation, pose)]

    def get_rows(self):
        rows = None
        if "layout" in self.data:
            rows = self.data["layout"]
        if not rows or len(rows) == 0:
            layout_path = self.filename.replace(os.sep, '/')
            layout_path = layout_path[layout_path.find("app/")+len("app/"):]
            raise AssertionError(f"No rows found in layout: {layout_path}")
        return rows

    def add_borders_and_scale(self, image, origin, image_name):
        #from the layout data, get all the different pieces of the image, and then assemble them together
        #into a proper rectangular image
        original_dimensions = self.get_property("dimensions", image_name)
        extra_area = self.get_property("extra area", image_name)
        shift = self.get_property("shift", image_name)
        border_color = self.data["border_color"]

        scale = self.get_property("scale", image_name)
        if scale:
            image = image.resize(tuple(scale*x for x in image.size), Image.NEAREST)
            origin = tuple(scale*x for x in origin)
            original_dimensions = [scale*x for x in original_dimensions]
            if extra_area is not None:
                extra_area = [[scale*x for x in region] for region in extra_area]

        if shift is not None:
            origin = tuple(origin[i] + shift[i] for i in range(2))

        dimensions = original_dimensions
        if extra_area is not None:         #indicates that there's patches over the top of this pose to fill it out
            for x0,y0,x1,y1 in extra_area:
                dimensions = (min(dimensions[0],x0),min(dimensions[1],y0),max(dimensions[2],x1),max(dimensions[3],y1))

        border = (
                            -origin[0]-dimensions[0],                                            #left
                            -origin[1]-dimensions[1],                                            #top,
                            dimensions[2] - (image.size[0] - origin[0]),    #right,
                            dimensions[3] - (image.size[1] - origin[1])        #bottom
        )

        fill_color = (0,0,0)
        if image.mode == "RGBA":
            fill_color = (0,0,0,0)
        image_with_border = ImageOps.expand(image,border=border,fill=fill_color)
        origin = (origin[0] + border[0], origin[1] + border[1])
        if extra_area is not None:     #we need to block off some areas that can't actually be used
            mask = Image.new("RGBA", (dimensions[2]-dimensions[0],dimensions[3]-dimensions[1]), tuple(border_color))
            x0,y0,x1,y1 = original_dimensions
            ImageDraw.Draw(mask).rectangle((x0+origin[0],y0+origin[1],x1+origin[0]-1,y1+origin[1]-1), fill = 0)
            for x0,y0,x1,y1 in extra_area:
                ImageDraw.Draw(mask).rectangle((x0+origin[0],y0+origin[1],x1+origin[0]-1,y1+origin[1]-1), fill = 0)

            image_with_border.paste(mask,mask=mask)

        spacer = self.data["images"][image_name]["spacer"] if "spacer" in self.data["images"][image_name] else 0
        border_with_spacer = (
                                                    self.data["border_size"]-min(spacer,0),
                                                    self.data["border_size"],
                                                    self.data["border_size"]+max(spacer,0),
                                                    self.data["border_size"]
        )

        if image_with_border.mode != "RGBA":
            border_color = (*border_color[:3],)
        image_with_border = ImageOps.expand(image_with_border,border=border_with_spacer,fill=tuple(border_color))     #hard border around the actual draw space
        origin = tuple(x+self.data["border_size"] for x in origin)

        if shift is not None:
            origin = tuple(origin[i] - shift[i] for i in range(2))

        return image_with_border, origin

    def get_property(self, this_property, image_name):
        FAILSAFE = 100
        if image_name in self.data["images"]:
            for _ in range(FAILSAFE):
                if this_property in self.data["images"][image_name]:
                    return self.data["images"][image_name][this_property]
                elif "parent" in self.data["images"][image_name]:
                    image_name = self.data["images"][image_name]["parent"]
                else:
                    return None
            else:
                #FIXME: English
                raise AssertionError(f"Encountered infinite parental loop in layout.json while investigating {image_name}")
        else:
            #FIXME: English
            #print(f"Key not found in layout.json while investigating {image_name}")
            pass
        return None

    def make_horizontal_collage(self, image_list):
        #assembles images horizontally and encapsulates them in a border.
        y_min = min([-origin[1] for image,origin in image_list])
        y_max = max([image.size[1]-origin[1] for image,origin in image_list])

        collage_width = sum([image.size[0] for image,_ in image_list])
        collage_y_size = y_max-y_min

        collage = Image.new("RGBA",(collage_width,collage_y_size),0)

        current_x_position = 0
        for image, origin in image_list:
            border = (
                                0,                                                        #left
                                -origin[1]-y_min,                            #top
                                0,                                                        #right
                                origin[1]+y_max-image.size[1]    #bottom
            )
            border_color = self.data["border_color"]
            if image.mode != "RGBA":
                border_color = border_color[:3]
            bordered_image = ImageOps.expand(image,border=border,fill=tuple(border_color))
            collage.paste(bordered_image, (current_x_position,0))

            current_x_position += image.size[0]

        return collage

    def make_vertical_collage(self, image_list):
        collage = None

        if len(image_list):
            width = max([image.size[0] for image in image_list])
            height = sum([image.size[1] for image in image_list])

            collage = Image.new("RGBA", (width,height), 0)
            current_y = 0
            for image in image_list:
                collage.paste(image, ((width-image.size[0])//2,current_y))
                current_y += image.size[1]

        return collage

    def export_all_images_to_PNG(self, all_images, master_palette):
        all_collages = []
        for row in self.get_rows():

            this_row_images = []
            for image_name in row:     #for every image referenced explicitly in the layout
                if image_name in all_images:
                    image = all_images[image_name]

                    xmin,ymin,xmax,ymax = self.get_bounding_box(image_name)
                    if not image:        #there was no image there to grab, so make a blank image
                        image = Image.new("RGBA", (xmax-xmin,ymax-ymin), 0)

                    palette = self.get_property("import palette interval", image_name)
                    palette = master_palette[palette[0]:palette[1]] if palette else []

                    image = common.apply_palette(image, palette)
                    bordered_image, origin = self.add_borders_and_scale(image, (-xmin,-ymin), image_name)

                    this_row_images.append((bordered_image, origin))

            collage = self.make_horizontal_collage(this_row_images)
            all_collages.append(collage)

        full_layout = self.make_vertical_collage(all_collages)
        return full_layout

    def coord_calc(self,origin,dims):
        x1, x2 = origin
        w, h = dims
        return (x1,x2,w+x1,h+x2)

    def extract_all_images_from_master(self, master_image):
        all_images = {}
        master_height = 0
        for row in self.get_rows():
            row_width = 0
            row_y_min,row_y_max = float('Inf'),-float('Inf')
            for image_name in row:     #for every image referenced explicitly in the layout
                if image_name in self.data["images"]:
                    spacer = self.data["images"][image_name]["spacer"] if "spacer" in self.data["images"][image_name] else 0
                    xmin,ymin,xmax,ymax = self.get_bounding_box(image_name)
                    row_width += (xmax-xmin)+2*self.data["border_size"]+abs(spacer)
                    row_y_min,row_y_max = min(row_y_min,ymin),max(row_y_max,ymax)
                else:
                    layout_path = self.filename.replace(os.sep, '/')
                    layout_path = layout_path[layout_path.find("app/")+len("app/"):]
                    raise AssertionError(f"'{image_name}' not found in layout/image definition for '{layout_path}'!")
            row_height = row_y_max-row_y_min+2*self.data["border_size"]
            row_margin = (master_image.size[0] - row_width)//2
            row_of_images = master_image.crop((row_margin,master_height,row_width+row_margin,master_height+row_height))
            master_height += row_height

            #now that we have the actual row of images, with the appropriate margins,
            # we can iterate over the row one more time to sweep through and extract the individual images
            master_width = 0
            for image_name in row:     #for every image referenced explicitly in the layout
                shift = self.get_property("shift", image_name)
                vert_shift = shift[1] if shift else 0
                scale = self.get_property("scale", image_name)
                xmin,ymin,xmax,ymax = self.get_bounding_box(image_name)
                this_image = Image.new("RGBA",(xmax-xmin,ymax-ymin),0)
                extra_area = self.get_property("extra area", image_name)
                spacer = self.data["images"][image_name]["spacer"] if "spacer" in self.data["images"][image_name] else 0
                master_width -= min(spacer,0)

                for x0,y0,x1,y1 in itertools.chain([self.get_property("dimensions", image_name)], \
                                                    extra_area if extra_area else []):
                    if scale:
                        x0,y0,x1,y1 = scale*x0,scale*y0,scale*x1,scale*y1
                    cropped_image = row_of_images.crop((
                                                        self.data["border_size"] + master_width+x0-xmin,
                                                        self.data["border_size"] + vert_shift    +y0-row_y_min,
                                                        self.data["border_size"] + master_width+x1-xmin,
                                                        self.data["border_size"] + vert_shift    +y1-row_y_min))
                    this_image.paste(cropped_image,(x0-xmin,y0-ymin+vert_shift))
                if scale:
                    if hasattr(Image, "Resampling"):
                        # PIL > 6.2.2
                        this_image = this_image.resize(
                            (
                                (xmax - xmin) // scale,
                                (ymax - ymin) // scale
                            ),
                            Image.Resampling.NEAREST
                        )
                    else:
                        # PIL <= 6.2.2
                        this_image = this_image.resize(
                            (
                                (xmax - xmin) // scale,
                                (ymax - ymin) // scale
                            )
                        )
                master_width += xmax - xmin + 2 * \
                    self.data["border_size"] + max(spacer, 0)
                all_images[image_name] = this_image

        all_images["transparent"] = Image.new("RGBA",(0,0),0)

        #FIXME: Extrapolate layoutlib.py to <console>/<game>/<sprite>/layout.py
        tmp = {}
        palette_block = None
        for block_name in [
            "meta_block",
            "meta_block1",
            "meta_block2"
        ]:
            if block_name in all_images:
                if f"ffmq{os.sep}benjamin" in self.filename:
                    meta_block = all_images[block_name].transpose(Image.FLIP_TOP_BOTTOM)
                    palette_block = meta_block.crop(self.coord_calc((0,0),(8,1)))
                if f"ffmq{os.sep}darkking" in self.filename:
                    meta_block = all_images[block_name].transpose(Image.FLIP_LEFT_RIGHT)
                    meta_block = meta_block.crop(self.coord_calc((0,0),(8,1)))
                    palette_block = meta_block.transpose(Image.FLIP_LEFT_RIGHT)
                    # tmp[block_name] = palette_block
                    # palette_block.show()

        if "stock_palette" in self.data:
            stock_palette = self.data["stock_palette"]
            rows = len(stock_palette)
            cols = len(stock_palette[0])
            flat_palette = []
            for row in stock_palette:
                for col in row:
                    flat_palette.append(tuple(col))
            palette_block = Image.new('RGB',(cols,rows),0)
            palette_block.putdata(flat_palette)

        if palette_block:
            all_images["palette_block"] = palette_block

        master_palettes = []
        if "palette_block" in all_images and "palette_block" in self.data["images"]:
            if "shift" in self.data["images"]["palette_block"]:
                shift = self.data["images"]["palette_block"]["shift"]
                if shift[0] != 0:
                    palette_block = all_images["palette_block"]
                    palette_block = palette_block.crop(
                        (
                            abs(shift[0]),
                            0,
                            *palette_block.size
                        )
                    )
                    all_images["palette_block"] = palette_block
            palette_rgb = list(all_images["palette_block"].convert("RGB").getdata())
            palette_rgba = list(all_images["palette_block"].convert("RGBA").getdata())
            is_z3link = os.path.join("zelda3","link") in self.filename
            is_doi = is_z3link and \
                len(set(palette_rgb[:16])) > 1 and \
                len(set(palette_rgba[:16])) > 1
            if is_doi:
                self.subtype = "doi"
            if is_z3link:
                green_start = 0x10
                bunny_start = green_start * 4
                bunny_end = bunny_start + 0x10
                if self.subtype == "doi":
                    # Get Yellow
                    yellow_rgb = palette_rgb[0:green_start]
                    yellow_rgba = palette_rgba[0:green_start]
                    # Get Bunny
                    bunny_rgb = palette_rgb[bunny_start:bunny_end]
                    bunny_rgba = palette_rgba[bunny_start:bunny_end]
                    # G B R Y Bun
                    palette_rgb = palette_rgb[green_start:bunny_start] + yellow_rgb + bunny_rgb
                    palette_rgba = palette_rgba[green_start:bunny_start] + yellow_rgba + bunny_rgba
                else:
                    # Remove dead Yellow
                    # G B R Bun
                    palette_rgb = palette_rgb[green_start:bunny_end]
                    palette_rgba = palette_rgba[green_start:bunny_end]
            if len(palette_rgba) > 0 and len(palette_rgba[0]) > 3:
                if palette_rgba[0][3] == 0:
                    palette_rgb[0] = (255,0,255)
            master_palettes = palette_rgb
            # print("Master Palettes:")
            # n_cols = 16
            # for i in range(0, len(master_palettes), n_cols):
            #     print([i / n_cols + 1,*master_palettes[i:i+n_cols]])
        else:
            master_palettes = []

        if len(master_palettes):
            for image_name, this_image in all_images.items():
                if not image_name in [
                    "transparent",
                    "doi_palette_block",
                    "palette_block"
                ]:
                    if "meta_block" in image_name \
                        or "null_block" in image_name:
                        continue
                    import_palette = self.get_property("import palette interval", image_name)
                    if not import_palette:
                        raise AssertionError(f"Import Palette Interval not found for image '{image_name}'!")
                    palette = [x for color in master_palettes[import_palette[0]:import_palette[1]] for x in color]     #flatten the RGB values
                    palette = palette + palette[:3]*(256-(len(palette)//3))
                    palette_seed = Image.new("P", (1,1))
                    palette_seed.putpalette(palette)

                    #this is a workaround to quantize without dithering
                    paletted_image = this_image._new(this_image.im.convert("P",0,palette_seed.im))

                    #have to shift the palette over now to include the transparent pixels correctly
                    #did it this way so that color pixels would not accidentally be matched to transparency
                    original_image_L = [0 if alpha < 255 else 1 for _,_,_,alpha in this_image.getdata()]
                    new_image_indices = [L*(index+1) for (L,index) in zip(original_image_L,paletted_image.getdata())]
                    paletted_image.putdata(new_image_indices)
                    shifted_palette = [0,0,0] + palette[:-3]
                    paletted_image.putpalette(shifted_palette)

                    all_images[image_name] = paletted_image

        return all_images, master_palettes

    def get_bounding_box(self, image_name):
        xmin,ymin,xmax,ymax = self.get_raw_bounding_box(image_name)
        scale = self.get_property("scale", image_name)
        if scale:
            xmin,ymin,xmax,ymax = xmin*scale,ymin*scale,xmax*scale,ymax*scale
        shift = self.get_property("shift", image_name)
        if shift:
            xmin, ymin, xmax, ymax = xmin+shift[0], ymin+shift[1], xmax+shift[0], ymax+shift[1]

        return xmin,ymin,xmax,ymax

    def get_raw_bounding_box(self,image_name):
        xmin,ymin,xmax,ymax = self.get_property("dimensions", image_name)
        extra_area = self.get_property("extra area", image_name)
        if extra_area:
            for x0,y0,x1,y1 in extra_area:
                xmin,ymin,xmax,ymax = min(xmin,x0), min(ymin,y0), max(xmax,x1), max(ymax,y1)
        return xmin,ymin,xmax,ymax

def main():
    print(f"Called main() on utility library {__file__}")


if __name__ == "__main__":
    main()

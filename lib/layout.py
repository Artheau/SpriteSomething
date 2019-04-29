#originally written by Artheau
#with Darmok and Jalad at Tanagra
#in April of 2019

#this file contains various helper functions which facilitate the construction of the PNG layout files

import json
from PIL import Image, ImageOps, ImageDraw
from lib.RomHandler import util

class Layout():
    def __init__(self, filename):
        with open(filename) as inFile:
            self.data = json.load(inFile)
        self.reverse_lookup = {}
        for image_name,image_info in self.data["images"].items():
            for image_ref in image_info["used by"]:
                if tuple(image_ref) in self.reverse_lookup:
                    self.reverse_lookup[tuple(image_ref)].append(image_name)
                else:
                    self.reverse_lookup[tuple(image_ref)] = [image_name]

    def get_image_name(self, animation, pose):
        #get any old image name from reverse lookup
        if type(animation) is int:
            animation = util.pretty_hex(animation)

        if (animation,pose) in self.reverse_lookup:
            return self.reverse_lookup[(animation, pose)][0]
        else:
            return "null"

    def get_all_image_names(self,animation, pose):
        if type(animation) is int:
            animation = util.pretty_hex(animation)
        #get the full list
        return self.reverse_lookup[(animation, pose)]

    def get_rows(self):
        return self.data["layout"]

    def add_borders_and_scale(self, image, origin, image_name, add_border=True, border_color=(0,0,0x7F,0xFF)):
        #from the layout data, get all the different pieces of the image, and then assemble them together
        #into a proper rectangular image
        original_dimensions = self.get_property("dimensions", image_name)
        extra_area = self.get_property("extra area", image_name)

        scale = self.get_property("scale", image_name)
        if scale:
            image = image.resize(tuple(scale*x for x in image.size), Image.NEAREST)
            origin = tuple(scale*x for x in origin)
            original_dimensions = [scale*x for x in original_dimensions]
            if extra_area is not None:
                extra_area = [[scale*x for x in region] for region in extra_area]

        dimensions = original_dimensions
        if extra_area is not None:     #indicates that there's patches over the top of this pose to fill it out
            for x0,x1,y0,y1 in extra_area:
                dimensions = (min(dimensions[0],x0),max(dimensions[1],x1),min(dimensions[2],y0),max(dimensions[3],y1))

        border = ( \
                    -origin[0]-dimensions[0],   #left
                    -origin[1]-dimensions[2],   #top,
                    dimensions[1] - (image.size[0] - origin[0]), #right,
                    dimensions[3] - (image.size[1] - origin[1])  #bottom
                )
        image_with_border = ImageOps.expand(image,border=border,fill=(0,0,0,0))
        origin = (origin[0] + border[0], origin[1] + border[1])
        if extra_area is not None:   #we need to block off some areas that can't actually be used
            mask = Image.new("RGBA", (dimensions[1]-dimensions[0],dimensions[3]-dimensions[2]), border_color)
            x0,x1,y0,y1 = original_dimensions
            ImageDraw.Draw(mask).rectangle((x0+origin[0],y0+origin[1],x1+origin[0]-1,y1+origin[1]-1), fill = 0)
            for x0,x1,y0,y1 in extra_area:
                ImageDraw.Draw(mask).rectangle((x0+origin[0],y0+origin[1],x1+origin[0]-1,y1+origin[1]-1), fill = 0)

            image_with_border.paste(mask,mask=mask)

        if add_border:
            image_with_border = ImageOps.expand(image_with_border,border=1,fill=border_color)   #hard border around the actual draw space
            origin = tuple(x+1 for x in origin)
        
        return image_with_border, origin


    def get_property(self, property, image_name):
        FAILSAFE = 100
        for _ in range(FAILSAFE):
            if property in self.data["images"][image_name]:
                return self.data["images"][image_name][property]
            elif "parent" in self.data["images"][image_name]:
                image_name = self.data["images"][image_name]["parent"]
            else:
                return None
        else:
            raise AssertionError(f"Encountered infinite parental loop in layout.json while investigating {image_name}")


    def make_horizontal_collage(self, image_list,add_border=True,border_color=(0,0,0x7F,0xFF)):
        #assembles images horizontally and encapsulates them in a blue border.  You can specify no border by using "None" for color
        y_min = min([-origin[1] for image,origin in image_list])
        y_max = max([image.size[1]-origin[1] for image,origin in image_list])

        num_images = len(image_list)
        
        collage_width = sum([image.size[0] for image,_ in image_list])
        collage_y_size = y_max-y_min

        collage = Image.new("RGBA",(collage_width,collage_y_size),0)

        current_x_position = 0
        for image, origin in image_list:
            if add_border:
                border =    ( \
                                0,                     #left
                                -origin[1]-y_min,     #top
                                0,                     #right
                                origin[1]+y_max-image.size[1]      #bottom
                            )
                bordered_image = ImageOps.expand(image,border=border,fill=border_color)
                collage.paste(bordered_image, (current_x_position,0))
            else:
                collage.paste(image, (current_x_position,0))
            current_x_position += image.size[0]

        return collage

    def make_vertical_collage(self, image_list):
        width = max([image.size[0] for image in image_list])
        height = sum([image.size[1] for image in image_list])

        collage = Image.new("RGBA", (width,height), 0)
        current_y = 0
        for image in image_list:
            collage.paste(image, ((width-image.size[0])//2,current_y))
            current_y += image.size[1]
        return collage

    def export_all_images_to_PNG(self, all_images):
        all_collages = []
        for i,row in enumerate(self.get_rows()):
            this_row_images = []
            for image_name in [x for x in row]:   #for every image referenced explicitly in the layout
                image, origin = all_images[image_name]

                if image:
                    bordered_image, new_origin = self.add_borders_and_scale(image, origin, image_name)

                    shift = self.get_property("shift", image_name)
                    if shift is not None:
                        new_origin = tuple(new_origin[i] - shift[i] for i in range(2))    
                    
                    this_row_images.append((bordered_image, new_origin))
                else:
                    print(f"WARNING: Did not generate image for {image_name}")

            collage = self.make_horizontal_collage(this_row_images)
            all_collages.append(collage)

        full_layout = self.make_vertical_collage(all_collages)
        return full_layout

if __name__ == "__main__":
    main()
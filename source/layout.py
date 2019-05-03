#originally written by Artheau
#with Darmok and Jalad at Tanagra
#in April of 2019

#this file contains various helper functions which facilitate the construction of the PNG layout files

import json
import itertools
from PIL import Image, ImageOps, ImageDraw
from source import util

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

	def get_image_name(self, animation, pose, force=None):
		if type(animation) is int:
			animation = util.pretty_hex(animation)

		for (animation,pose),image_name_list in self.reverse_lookup.items():
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
			animation = util.pretty_hex(animation)
		#get the full list
		return self.reverse_lookup[(animation, pose)]

	def get_rows(self):
		return self.data["layout"]

	def add_borders_and_scale(self, image, origin, image_name, border_color=(0,0,0x7F,0xFF)):
		#from the layout data, get all the different pieces of the image, and then assemble them together
		#into a proper rectangular image
		original_dimensions = self.get_property("dimensions", image_name)
		extra_area = self.get_property("extra area", image_name)
		shift = self.get_property("shift", image_name)
		
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

		image_with_border = ImageOps.expand(image_with_border,border=self.data["border_size"],fill=border_color)   #hard border around the actual draw space
		origin = tuple(x+self.data["border_size"] for x in origin)

		if shift is not None:
			origin = tuple(origin[i] - shift[i] for i in range(2))   
		
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
		#assembles images horizontally and encapsulates them in a blue border.
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
			for image_name in row:   #for every image referenced explicitly in the layout
				image, origin = all_images[image_name]

				if not image:    #there was no image there to grab, so make a blank image
					xmin,xmax,ymin,ymax = self.get_bounding_box(image_name)
					image = Image.new("RGBA", (xmax-xmin,ymax-ymin), 0)
					offset = (-xmin,-ymin)

				bordered_image, new_origin = self.add_borders_and_scale(image, origin, image_name)
				this_row_images.append((bordered_image, new_origin))

			collage = self.make_horizontal_collage(this_row_images)
			all_collages.append(collage)

		full_layout = self.make_vertical_collage(all_collages)
		return full_layout

	def extract_all_images_from_master(self, master_image):
		all_images = {}
		master_height = 0
		for i,row in enumerate(self.get_rows()):
			row_width = 0
			row_y_min,row_y_max = float('Inf'),-float('Inf')
			for image_name in row:   #for every image referenced explicitly in the layout
				xmin,xmax,ymin,ymax = self.get_bounding_box(image_name)
				row_width += (xmax-xmin)+2*self.data["border_size"]
				row_y_min,row_y_max = min(row_y_min,ymin),max(row_y_max,ymax)
			row_height = row_y_max-row_y_min+2*self.data["border_size"]
			row_margin = (master_image.size[0] - row_width)//2
			row_of_images = master_image.crop((row_margin,master_height,row_width+row_margin,master_height+row_height))
			master_height += row_height

			#now that we have the actual row of images, with the appropriate margins,
			# we can iterate over the row one more time to sweep through and extract the individual images
			master_width = 0
			for image_name in row:   #for every image referenced explicitly in the layout
				shift = self.get_property("shift", image_name)
				vert_shift = shift[1] if shift else 0
				scale = self.get_property("scale", image_name)
				xmin,xmax,ymin,ymax = self.get_bounding_box(image_name)
				this_image = Image.new("RGBA",(xmax-xmin,ymax-ymin),0)
				extra_area = self.get_property("extra area", image_name)
				for x0,x1,y0,y1 in itertools.chain([self.get_property("dimensions", image_name)], \
													extra_area if extra_area else []):
					if scale:
						x0,x1,y0,y1 = scale*x0,scale*x1,scale*y0,scale*y1
					cropped_image = row_of_images.crop((self.data["border_size"] + master_width+x0-xmin,
														self.data["border_size"] + vert_shift  +y0-row_y_min,
														self.data["border_size"] + master_width+x1-xmin,
														self.data["border_size"] + vert_shift  +y1-row_y_min))
					this_image.paste(cropped_image,(x0-xmin,y0-ymin+vert_shift))
				if scale:
					this_image = this_image.resize(  ((xmax-xmin)//scale,  (ymax-ymin)//scale)  )
				master_width += xmax-xmin+2*self.data["border_size"]

				all_images[image_name] = (this_image, (-xmin,-ymin))  #image and origin point

		master_palettes = list(all_images["palette_block"][0].convert("RGB").getdata())

		for image_name,(this_image,origin) in all_images.items():
			if image_name != "palette_block":
				palette_number = int(self.get_property("palette", image_name)[2:],16) & 0x0F
				import_palette = self.get_property("import palette", image_name)
				palette = [x for color in master_palettes[import_palette[0]:import_palette[1]] for x in color]   #flatten the RGB values
				palette = palette + palette[:3]*(256-(len(palette)//3))
				palette_seed = Image.new("P", (1,1))
				palette_seed.putpalette(palette)
				paletted_image = this_image.convert("RGB").quantize(palette=palette_seed)
				#have to shift the palette over now to include the transparent pixels correctly
				#did it this way so that color pixels would not accidentally be matched to transparency
				shift = palette_number*0x10
				original_image_L = [0 if alpha < 255 else 1 for _,_,_,alpha in this_image.getdata()]
				new_image_indices = [L*(index+shift+1) for (L,index) in zip(original_image_L,paletted_image.getdata())]
				paletted_image.putdata(new_image_indices)
				shifted_palette = [0,0,0]*(shift+1) + palette[:-3*(shift+1)]
				paletted_image.putpalette(shifted_palette)

				all_images[image_name] = (paletted_image,origin)

			
	def get_bounding_box(self, image_name):
		xmin,xmax,ymin,ymax = self.get_property("dimensions", image_name)
		extra_area = self.get_property("extra area", image_name)
		if extra_area:
			for x0,x1,y0,y1 in extra_area:
				xmin,xmax,ymin,ymax = min(xmin,x0), max(xmax,x1),min(ymin,y0), max(ymax,y1)
		scale = self.get_property("scale", image_name)
		if scale:
			xmin,xmax,ymin,ymax = xmin*scale,xmax*scale,ymin*scale,ymax*scale
		shift = self.get_property("shift", image_name)
		if shift:
			xmin, xmax, ymin, ymax = xmin+shift[0], xmax+shift[0], ymin+shift[1],ymax+shift[1]
				
		return xmin,xmax,ymin,ymax

if __name__ == "__main__":
	main()
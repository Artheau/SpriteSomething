import json
import os
import urllib
from source import common
from source.pluginslib import PluginsParent
from . import equipment

class Plugins(PluginsParent):
	def __init__(self):
		super().__init__()
		plugins = [
			("Download Official Sprites",None,self.get_alttpr_sprites),
			("Sheet Trawler",None,None),
			("Pose as Tracker Images",None,None)#,
			#("Equipment",None,self.equipment_test)
		]
		self.set_plugins(plugins)

	def equipment_test(self):
		equipment.equipment_test()

	def get_alttpr_sprites(self):
		success = False	#report success
		official = os.path.join('.',"user_resources","zelda3","link","sheets","official")	#save to user_resources/zelda3/link/sheets/official/*.zspr
		if not os.path.exists(official):
			os.makedirs(official)	#make it if we don't have it

		#make the request!
		alttpr_sprites_filename = "http://alttpr.com/sprites"
		alttpr_sprites_req = urllib.request.urlopen(alttpr_sprites_filename)
		alttpr_sprites = json.loads(alttpr_sprites_req.read().decode("utf-8"))
		#get an iterator and a counter for a makeshift progress bar
		i = 0
		total = len(alttpr_sprites)
		print("   Downloading Official ALttPR Sprites")
		for sprite in alttpr_sprites:
			sprite_filename = sprite["file"][sprite["file"].rfind('/')+1:]	#get the filename
			sprite_destination = os.path.join(official,sprite_filename)	#set the destination
			i += 1	#iterate iterator
			if not os.path.exists(sprite_destination):	#if we don't have it, download it
				with open(sprite_destination, "wb") as g:
					sprite_data_req = urllib.request.urlopen(sprite["file"])
					sprite_data = sprite_data_req.read()
					print("    Writing " + str(i).rjust(len(str(total))) + '/' + str(total) + ": " + sprite_filename)
					g.write(sprite_data)
					success = True
			else:	#if we do have it, next!
				print("    Skipping " + str(i).rjust(len(str(total))) + '/' + str(total) + ": " + sprite_filename)
		return success

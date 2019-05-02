#common functions for all entities (i.e. "Sprites")
#sprites are responsible for maintaining their widgets
#they have to contain PIL images of all of their data, and the offset info, and how to assemble it
#and they have to interpret the global frame timer, and communicate back when to next check in

#this file needs to contain all the metadata for the sprites

class SpriteParent():
	#parent class for sprites to inherit
	def __init__(self, manifest_dict, my_subpath):
		self.classic_name = manifest_dict["name"]    #e.g. "Samus" or "Link"
		self.resource_subpath = my_subpath           #the path to this sprite's subfolder in resources

	#to make a new sprite class, you must write code for all of the functions in this section below.
	############################# BEGIN ABSTRACT CODE ##############################



	############################# END ABSTRACT CODE ##############################

	#the functions below here are special to the parent class and do not need to be duplicated
import util
import os

def main():
	#main data
	data = util.Samus()

	if not os.access("images", os.F_OK):
		os.mkdir("images")

	EXPORT_CUSTOM_SEQUENCES = True
	if EXPORT_CUSTOM_SEQUENCES:
		events = { 80:{'kick':True}, \
		           200:{'kick':True}, \
		           200:{'heavy_breathing':True}, \
		           300:{'new_animation':0x0A}, \
		           400:{'new_animation':0x10}, \
		           500:{'new_animation':0x1A}}   #I'm thinking that this will eventually be JSON
		data.animation_sequence_to_gif('images/test_sequence.gif', zoom=2, starting_animation=0xE9, events=events)


	EXPORT_RAW_ANIMATIONS = True
	if EXPORT_RAW_ANIMATIONS:
		for animation_number in range(len(data.animations)):
			if data.animations[animation_number].used:
				try:
					data.animations[animation_number].gif(f"images/test{hex(animation_number)[2:].zfill(2)}.gif", data.palettes['standard'],zoom=2)
				except AssertionError as e:
					print(f"AssertionError on animation {hex(animation_number)}: {e.args}")


	EXPORT_SPECIFIC_POSE = False
	if EXPORT_SPECIFIC_POSE:
		animation_number = 0x1a
		pose_number = -1
		pose = data.animations[animation_number].poses[pose_number]
		img = pose.to_image(data.palettes['standard'],zoom=3)
		img.show()
		img.save(f"test{pose.ID}.png")


	EXPORT_TILES = False
	if EXPORT_TILES:
		animation_number = 0x1a
		pose_number = -1
		for tile in data.animations[animation_number].poses[pose_number].tiles:
			img = tile.to_image(data.palettes['standard'],zoom=2)
			img.show()
			img.save(f"test{tile.ID}.png")


if __name__ == "__main__":
    main()
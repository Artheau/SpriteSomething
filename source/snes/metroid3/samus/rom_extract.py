#connects with the Samus sprite class
import json
from PIL import Image
from source.meta.common import common

def rom_extract(sprite, rom):
    author_name = sprite.translate_author(rom)
    sprite.metadata["author.name"] = author_name
    sprite.metadata["author.name-short"] = author_name
    all_images = {}
    for image_name in [name for row in sprite.layout.get_rows() for name in row]:  #for every image referenced explicitly in the layout
        animation, pose = sprite.layout.data["images"][image_name]["used by"][0]   #import a representative animation and pose
        if isinstance(animation,str) and animation[0:2] == "0x":                #convert from hex if needed
            animation = int(animation[2:], 16)

        force = sprite.layout.get_property("import", image_name)
        bounding_box = sprite.layout.get_raw_bounding_box(image_name)
        if force:
            if force.lower() == "upper":
                image = get_sprite_pose(sprite, rom, animation, pose, bounding_box, lower=False)
            elif force.lower() == "lower":
                image = get_sprite_pose(sprite, rom, animation, pose, bounding_box,upper=False)
            else:
                # FIXME: English
                raise AssertionError(f"received call to force something in pose {image_name}, but did not understand command '{force}'")
        else:
            image = get_sprite_pose(sprite, rom, animation, pose, bounding_box)

        all_images[image_name] = image

    return all_images

def get_sprite_pose(sprite, rom, animation_ID, pose, bounding_box, upper=True,lower=True):
    if isinstance(animation_ID,str):
        if animation_ID[:2] == "0x":   #it's a hex code
            return get_sprite_pose(sprite, rom, int(animation_ID[2:],16), pose, bounding_box, upper=upper,lower=lower)
        if animation_ID == "death_left":
            tilemaps, DMA_writes, duration = rom.get_death_data(pose, facing="left") # FIXME: duration unused variable
            if not upper:   #trim out the suit pieces
                tilemaps = [tilemap for tilemap in tilemaps if tilemap[4] & 0x1C != 0x08]
            if not lower:   #trim out the body
                tilemaps = [tilemap for tilemap in tilemaps if tilemap[4] & 0x1C == 0x08]
        elif animation_ID == "death_right":
            tilemaps, DMA_writes, duration = rom.get_death_data(pose, facing="right")
            if not upper:   #trim out the suit pieces
                tilemaps = [tilemap for tilemap in tilemaps if tilemap[4] & 0x1C != 0x08]
            if not lower:   #trim out the body
                tilemaps = [tilemap for tilemap in tilemaps if tilemap[4] & 0x1C == 0x08]
        elif animation_ID == "file_select":
            tilemaps = rom.get_file_select_tilemaps(pose)
            DMA_writes = rom.get_file_select_dma_data()
        elif animation_ID == "gun":
            tile, palette, gun_tile, gun_DMA = rom.get_minimal_gun_data(pose % 10, pose // 10)  #use highest decimal digit as the level of opening, and lowest as direction
            tilemaps = [[0x00,0x00,0x00,tile,palette]]  #if the port is requested specifically, we normalize it to (0,0)
            DMA_writes = {gun_tile: gun_DMA}
        elif animation_ID == "palette_block":
            #no need to make tilemaps or anything, just make the image and then early exit
            palette_block = common.convert_555_to_rgb(rom.get_palette("standard","power")[0][1][-15:])
            palette_block.extend(common.convert_555_to_rgb(rom.get_palette("standard","varia")[0][1][-15:]))
            palette_block.extend(common.convert_555_to_rgb(rom.get_palette("standard","gravity")[0][1][-15:]))
            palette_block.extend(common.convert_555_to_rgb(rom.get_palette("death_flesh", None)[0][1][-15:]))
            palette_block.extend(common.convert_555_to_rgb(rom.get_palette("crystal_flash", None)[0][1][-15:]))
            palette_block.extend(common.convert_555_to_rgb(rom.get_palette("file_select", None)[0][1][-15:]))
            palette_block.append((0,0,0))
            palette_block.extend(common.convert_555_to_rgb(rom.get_nightvisor_colors()))
            palette_block.extend([(0,0,0) for _ in range(7)])
            _,full_ship_colors = rom.get_palette("ship", None)[7]  #7 is when the underglow is brightest
            palette_block.extend(common.convert_555_to_rgb([full_ship_colors[1],full_ship_colors[9],full_ship_colors[15]]))
            image = Image.new("RGB",(15,7),0)
            image.putdata(palette_block)
            return image
        else:
            # FIXME: English
            raise AssertionError(f"unknown command to get_sprite_pose(): {animation_ID}")
    else:
        tilemaps, DMA_writes, duration = rom.get_pose_data(animation_ID, pose, upper=upper, lower=lower)   #TODO: do full port opening animation

    #there is stuff in VRAM by default, so populate this and then overwrite with the DMA_writes
    constructed_VRAM_data = {}
    TILESIZE = 0x20
    def add_flattened_tiles(current_dict):
        for index, tile_data in current_dict:
            for i in range(len(tile_data) //TILESIZE):   #for each tile
                constructed_VRAM_data[index+i] = tile_data[i*TILESIZE: (i+1)*TILESIZE]

    add_flattened_tiles(rom.get_default_vram_data().items())
    add_flattened_tiles(DMA_writes.items())

    constructed_image = common.image_from_raw_data(tilemaps, constructed_VRAM_data, bounding_box)
    return constructed_image

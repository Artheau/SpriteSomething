import json
import os
from PIL import Image
from lib.game import Game
from lib.zspr import Zspr
from . import rom
from lib.RomHandler import util
from lib.layout import Layout

class Metroid3(Game):
    def __init__(self, rom_filename, meta_filename):
        self.game_name = "Super Metroid"
        self.game_nameShort = "Metroid3"
        self.game_nameAbbr =  "M3"

        self.background_images = {}
        with open(os.path.join("resources",self.game_nameShort.lower(),"backgrounds","backgrounds.json")) as bgimg_file:
            bg_imgs = json.load(bgimg_file)
        for bg_img in bg_imgs:
            self.background_images[bg_img["filename"]] = bg_img["title"]
        for file in os.listdir(os.path.join("resources",self.game_nameShort.lower(),"backgrounds")):
            if not file.endswith(".json") and not file in self.background_images.keys():
                self.background_images[file] = file.capitalize().rpartition('.')[0]
        self.background_images = {v:k for k,v in self.background_images.items()}

        self.rom_data = rom.Metroid3RomHandler(rom_filename)
        self.meta_data = None
        self.sprites = {0x01: ("Samus", "M3Samus")}   #as (display name, class name)


class Metroid3Sprite(Zspr):   #Super Metroid Sprites
    def __init__(self, *args):
        super().__init__(*args)    #do the stuff from the inherited class

SAMUS_ANIMATION_DICT = {
                "Elevator (Power)": 0x00,
                "Elevator (Varia/Gravity)": 0x9B,

                "Stand right": 0x01,
                "Stand right, aim up": 0x03,
                "Stand right, aim diag up": 0x05,
                "Stand right, aim diag down": 0x07,
                "Stand, turning left": 0x25,
                "Stand, turn left, aim up": 0x8B,
                "Stand, turn left, aim diag up": 0x9C,
                "Stand, turn left, aim diag down": 0x8D,

                "Stand left": 0x02,
                "Stand left, aim up": 0x04,
                "Stand left, aim diag up": 0x06,
                "Stand left, aim diag down": 0x08,
                "Stand, turning right": 0x26,
                "Stand, turn right, aim up": 0x8C,
                "Stand, turn right, aim diag up": 0x9D,
                "Stand, turn right, aim diag down": 0x8E,

                "Run right": 0x09,
                "Run right, aim diag up": 0x0F,
                "Run right, aim forward": 0x0B,
                "Run right, aim diag down": 0x11,

                "Run left": 0x0A,
                "Run left, aim diag up": 0x10,
                "Run left, aim forward": 0x0C,
                "Run left, aim diag down": 0x12,

                "Jump begin, right": 0x4B,
                "Jump begin, right, aim up": 0x55,
                "Jump begin, right, aim diag up": 0x57,
                "Jump begin, right, aim diag down": 0x59,
                "Jump right": 0x4D,
                "Jumping forward, right": 0x51,
                "Jump right, aim up": 0x15,
                "Jump right, aim diag up": 0x69,
                "Jump right, aim forward": 0x13,
                "Jump right, aim diag down": 0x6B,
                "Jump right, aim down": 0x17,
                "Jump, turning left": 0x2F,
                "Jump, turn left, aim up": 0x8F,
                "Jump, turn left, aim diag up": 0x9E,
                "Jump, turn left, aim diag down": 0x91,
                "Standing from jump right": 0xA4,
                "Standing from jump right, aim up": 0xE0,
                "Standing from jump right, aim diag up": 0xE2,
                "Standing from jump right, aim forward": 0xE6,
                "Standing from jump right, aim diag down": 0xE4,

                "Jump begin, left": 0x4C,
                "Jump begin, left, aim up": 0x56,
                "Jump begin, left, aim diag up": 0x58,
                "Jump begin, left, aim diag down": 0x5A,
                "Jump left": 0x4E,
                "Jumping forward, left": 0x52,
                "Jump left, aim up": 0x16,
                "Jump left, aim diag up:": 0x6A,
                "Jump left, aim forward": 0x14,
                "Jump left, aim diag down": 0x6C,
                "Jump left, aim down": 0x18,
                "Jump, turning right": 0x30,
                "Jump, turn right, aim up": 0x90,
                "Jump, turn right, aim diag up": 0x9F,
                "Jump, turn right, aim diag down": 0x92,
                "Standing from jump left": 0xA5,
                "Standing from jump left, aim up": 0xE1,
                "Standing from jump left, aim diag up": 0xE3,
                "Standing from jump left, aim forward": 0xE7,
                "Standing from jump left, aim diag down": 0xE5,

                "Spin jump right": 0x19,
                "Space jump right": 0x1B,
                "Screw attack right": 0x81,
                "Walljump right": 0x83,
                "Standing from spin jump, right": 0xA6,

                "Spin jump left": 0x1A,
                "Space jump left": 0x1C,
                "Screw attack left": 0x82,
                "Walljump left": 0x84,
                "Standing from spin jump, left": 0xA7,

                "Morphing right": 0x37,
                "Morphball right": 0x1D,
                "Morphball roll right": 0x1E,
                "Morphball fall right": 0x31,
                "Unmorphing right": 0x3D,

                "Morphing left": 0x38,
                "Morphball left": 0x41,
                "Morphball roll left": 0x1F,
                "Morphball fall left": 0x32,
                "Unmorphing left": 0x3E,

                "Springball right": 0x79,
                "Springball roll right": 0x7B,
                "Springball fall right": 0x7D,
                "Springball jump right": 0x7F,

                "Springball left": 0x7A,
                "Springball roll left": 0x7C,
                "Springball fall left": 0x7E,
                "Springball jump left": 0x80,

                "Crouching from stand, right": 0x36,
                "Crouching from stand right, aim up": 0xF1,
                "Crouching from stand right, aim diag up": 0xF3,
                "Crouching from stand right, aim diag down": 0xF5,
                "Crouch right": 0x27,
                "Crouch right, aim up": 0x85,
                "Crouch right, aim diag up": 0x71,
                "Crouch right, aim diag down": 0x73,
                "Crouch, turn left": 0x43,
                "Crouch, turn left, aim up": 0x97,
                "Crouch, turn left, aim diag up": 0xA2,
                "Crouch, turn left, aim diag down": 0x99,
                "Standing from crouch right": 0x3B,
                "Standing from crouch right, aim up": 0xF7,
                "Standing from crouch right, aim diag up": 0xF9,
                "Standing from crouch right, aim diag down": 0xFB,

                "Crouching from stand, left": 0x35,
                "Crouching from stand left, aim up": 0xF2,
                "Crouching from stand left, aim diag up": 0xF4,
                "Crouching from stand left, aim diag down": 0xF6,
                "Crouch left": 0x28,
                "Crouch left, aim up": 0x86,
                "Crouch left, aim diag up": 0x72,
                "Crouch left, aim diag down": 0x74,
                "Crouch, turn right": 0x44,
                "Crouch, turn right, aim up": 0x98,
                "Crouch, turn right, aim diag up": 0xA3,
                "Crouch, turn right, aim diag down": 0x9A,
                "Standing from crouch left": 0x3C,
                "Standing from crouch left, aim up": 0xF8,
                "Standing from crouch left, aim diag up": 0xFA,
                "Standing from crouch left, aim diag down": 0xFC,

                "Fall right": 0x29,
                "Fall right, aim up": 0x2B,
                "Fall right, aim diag up": 0x6D,
                "Fall right, aim forward": 0x67,
                "Fall right, aim diag down": 0x6F,
                "Fall right, aim down": 0x2D,
                "Fall, turn left": 0x87,
                "Fall, turn left, aim up": 0x93,
                "Fall, turn left, aim diag up": 0xA0,
                "Fall, turn left, aim diag down": 0x95,   #technically aim down too
                
                "Fall left": 0x2A,
                "Fall left, aim up": 0x2C,
                "Fall left, aim diag up": 0x6E,
                "Fall left, aim forward": 0x68,
                "Fall left, aim diag down": 0x70,
                "Fall left, aim down": 0x2E,
                "Fall, turn right": 0x88,
                "Fall, turn right, aim up": 0x94,
                "Fall, turn right, aim diag up": 0xA1,
                "Fall, turn right, aim diag down": 0x96,   #technically aim down too
                
                "Moonwalk away from right": 0x4A,
                "Moonwalk away from right, aim diag up": 0x76,
                "Moonwalk away from right, aim diag down": 0x78,
                "Moonwalk, turn left": 0xBF,
                "Moonwalk, turn left, aim diag up": 0xC1,
                "Moonwalk, turn left, aim diag down": 0xC3,

                "Moonwalk away from left": 0x49,
                "Moonwalk away from left, aim diag up": 0x75,
                "Moonwalk away from left, aim diag down": 0x77,
                "Moonwalk, turn right": 0xC0,
                "Moonwalk, turn right, aim diag up": 0xC2,
                "Moonwalk, turn right, aim diag down": 0xC4,

                "Bonk right": 0x53,
                "Bonk right, roll out": 0x50,

                "Bonk left": 0x54,
                "Bonk left, roll out": 0x4F,

                "Grapple clockwise": 0xB2,
                "Grapple counterclockwise": 0xB3,
                "Grappled to right wall": 0xB8,
                "Grappled to left wall": 0xB9,

                "Grabbed right": 0xEC,
                "Grabbed right, aim diag up": 0xED,
                "Grabbed right, aim forward": 0xEE,
                "Grabbed right, aim diag down": 0xEF,
                "Grabbed right, struggling": 0xF0,

                "Grabbed left": 0xBA,
                "Grabbed left, aim diag up": 0xBB,
                "Grabbed left, aim forward": 0xBC,
                "Grabbed left, aim diag down": 0xBD,
                "Grabbed left, struggling": 0xBE,

                "Superjump begin right": 0xC7,
                "Superjump vertical right": 0xCB,
                "Superjump right": 0xC9,
                
                "Superjump begin left": 0xC8,
                "Superjump vertical left": 0xCC,
                "Superjump left": 0xCA,

                "Crystal flash right": 0xD3,
                "Crystal flash interrupt, right": 0xD7,
                "Crystal flash left": 0xD4,
                "Crystal flash interrupt, left": 0xD8,

                "X-ray right": 0xD5,
                "X-ray crouch right": 0xD9,
                "X-ray left": 0xD6,
                "X-ray crouch left": 0xDA,

                "Drained right": 0xE8,
                "Supplication right": 0xEA,

                "Drained left": 0xE9,
                "Supplication left": 0xEB,

                "Ran into right wall": 0x89,
                "Ran into right wall, aim diag up": 0xCF,
                "Ran into right wall, aim diag down": 0xD1,
                "Ran into left wall": 0x8A,
                "Ran into left wall, aim diag up": 0xD0,
                "Ran into left wall, aim diag down": 0xD2,
                "Superjump diagonal right": 0xCD,
                "Superjump diagonal left": 0xCE,
}



class M3Samus(Metroid3Sprite):    # SM Player Character Sprites
    def __init__(self, *args):
        super().__init__(*args)    #do the stuff from the inherited class

        self.palette_types = {
                "power": 1,
                "varia": 2,
                "gravity": 3,
        }

        self.suit_lookup = {value:key for key,value in self.palette_types.items()}   #reverse lookup

        self.variant_type = {
                "standard": 0,
                #"loader": 1,
                "heat": 2,
                "charge": 3,
                "speed_boost": 4,
                "speed_squat": 5,
                "shine_spark": 6,
                "screw_attack": 7,
                "hyper_beam": 8,
                "death_suit": 9,
                "death_flesh": 10,
                #"crystal_flash": 11,
                "sepia": 12,
                "sepia_hurt": 13,
                "sepia_alternate": 14,
                "door": 15,
                "xray": 16,
                "file_select": 17,
                "ship": 18,
                "intro_ship": 19,
                "outro_ship": 20,
        }

        self.animations = SAMUS_ANIMATION_DICT

        self._layout = Layout(os.path.join("lib","metroid3","layout.json"))


    def get_timed_sprite_palette(self, variant_type, suit_type):   #for use in rendering the sprite
        #interface between this file and the corresponding enumerations in rom.py
        return self.rom_data.get_palette( \
                    getattr(rom.PaletteType,variant_type.upper()), \
                    getattr(rom.SuitType,suit_type.upper()) \
                    )

    def get_sprite_palette_from_buttons(self, buttons, frame):
        suit_type = [None,"power","varia","gravity"][buttons["suit"]]
        return self.get_sprite_palette("standard", suit_type, frame)

    def get_sprite_palette(self, variant_type, suit_type, frame):     #for displaying the palette in the GUI, not for rendering
        current_palette = self.get_current_time_palette(self.get_timed_sprite_palette(variant_type, suit_type),frame)
        death_palette = self.get_current_time_palette(self.get_timed_sprite_palette("death_flesh", suit_type),frame)
        loader_palette = self.get_current_time_palette(self.get_timed_sprite_palette("loader", suit_type),frame)
        flash_palette = self.get_current_time_palette(self.get_timed_sprite_palette("crystal_flash", suit_type),frame)
        file_select_palette = self.get_current_time_palette(self.get_timed_sprite_palette("file_select", suit_type),frame)
        zero_palette = [0 for _ in range(16)]
        full_palette = \
                zero_palette + \
                file_select_palette + \
                current_palette + \
                death_palette + \
                zero_palette + \
                zero_palette + \
                loader_palette + \
                flash_palette + \
                [0 for _ in range(16*8)]
        return full_palette

    def set_sprite_palette(self, variant_type, suit_type, frame):
        raise NotImplementedError()

    def get_sprite_pose(self, animation_ID, pose, upper=True,lower=True):
        if type(animation_ID) is str:
            if animation_ID == "death_left":
                tilemaps, DMA_writes, duration = self.rom_data.get_death_data(pose, facing="left")
                if not upper:   #trim out the suit pieces
                    tilemaps = [tilemap for tilemap in tilemaps if tilemap[4] & 0x1C != 0x08]
                if not lower:   #trim out the body
                    tilemaps = [tilemap for tilemap in tilemaps if tilemap[4] & 0x1C == 0x08]
            elif animation_ID == "death_right":
                tilemaps, DMA_writes, duration = self.rom_data.get_death_data(pose, facing="right")
                if not upper:   #trim out the suit pieces
                    tilemaps = [tilemap for tilemap in tilemaps if tilemap[4] & 0x1C != 0x08]
                if not lower:   #trim out the body
                    tilemaps = [tilemap for tilemap in tilemaps if tilemap[4] & 0x1C == 0x08]
            elif animation_ID == "file_select":
                tilemaps = self.rom_data.get_file_select_tilemaps(pose)
                DMA_writes = self.rom_data.get_file_select_dma_data()
            elif animation_ID == "gun":
                tile, palette, gun_tile, gun_DMA = self.rom_data.get_minimal_gun_data(pose % 10, pose // 10)  #use highest decimal digit as the level of opening, and lowest as direction
                tilemaps = [[0x00,0x00,0x00,tile,palette]]  #if the port is requested specifically, we normalize it to (0,0)
                DMA_writes = {gun_tile: gun_DMA}
            elif animation_ID == "palette_block":
                #no need to make tilemaps or anything, just make the image and then early exit
                palette_block = util.convert_to_rgb(self.get_current_time_palette(self.get_timed_sprite_palette("standard", "power"),0))[-15:]
                palette_block.extend(util.convert_to_rgb(self.get_current_time_palette(self.get_timed_sprite_palette("standard", "varia"),0))[-15:])
                palette_block.extend(util.convert_to_rgb(self.get_current_time_palette(self.get_timed_sprite_palette("standard", "gravity"),0))[-15:])
                palette_block.extend(util.convert_to_rgb(self.get_current_time_palette(self.get_timed_sprite_palette("death_flesh", "power"),0))[-15:])
                palette_block.extend(util.convert_to_rgb(self.get_current_time_palette(self.get_timed_sprite_palette("file_select", "power"),0))[-15:])
                palette_block.extend(util.convert_to_rgb(self.get_current_time_palette(self.get_timed_sprite_palette("crystal_flash", "power"),0))[-6:])
                palette_block.append((0,0,0,0))
                palette_block.extend(util.convert_to_rgb(self.rom_data.get_nightvisor_colors()))
                palette_block.append((0,0,0,0))
                _,full_ship_colors = self.get_timed_sprite_palette("ship", "power")[7]  #7 is when the underglow is brightest
                palette_block.extend(util.convert_to_rgb([full_ship_colors[1],full_ship_colors[9],full_ship_colors[15]]))
                image = Image.new("RGBA",(15,6),0)
                image.putdata(palette_block)
                return image, (0,0)
            else:
                raise AssertionError(f"unknown command to get_sprite_pose(): {animation_ID}")
        else:
            tilemaps, DMA_writes, duration = self.rom_data.get_pose_data(animation_ID, pose, upper=upper, lower=lower)   #TODO: do full port opening animation
        palette_timing_list = self.get_timed_sprite_palette("standard", "power")



        #there is stuff in VRAM by default, so populate this and then overwrite with the DMA_writes
        constructed_VRAM_data = {}
        TILESIZE = 0x20
        def add_flattened_tiles(current_dict):
            for index, tile_data in current_dict:
                for i in range(len(tile_data) //TILESIZE):   #for each tile
                    constructed_VRAM_data[index+i] = tile_data[i*TILESIZE: (i+1)*TILESIZE]

        add_flattened_tiles(self.rom_data.get_default_vram_data().items())
        add_flattened_tiles(DMA_writes.items())

        constructed_image, offset = util.image_from_raw_data(tilemaps, constructed_VRAM_data)
        return constructed_image, offset

    def get_pose_number_from_frame_number(self, animation_ID, frame):
        pose = 0
        MAX_ITS = 100   #failsafe in case of the unexpected
        frames_so_far = 0
        for _ in range(MAX_ITS):
            control_codes = self.rom_data.get_pose_control_data(animation_ID,pose)
            if control_codes[0] < 0xF0:   #this is a duration, not a control code
                frames_so_far += control_codes[0]
                if frames_so_far > frame:
                    return pose
                else:
                    pose += 1
            elif control_codes[0] == 0xFE:    #targeted loop
                loop_length = control_codes[1]
                frame = (frame-frames_so_far) % loop_length    #we know the loop size, so no need to keep looping a lot
                frames_so_far = 0
                pose -= loop_length
            elif control_codes[0] == 0xFB:    #for the walljump branching, let's just go to spinjump for now
                pose += 1
            else:                             #all (essentially) return to the beginning of the loop, with some caveats
                frame = frame % frames_so_far     #now we know the loop size, so no need to keep looping a lot
                frames_so_far = 0
                pose = 0                       #reset to the beginning

        else:
            raise AssertionError("In get_pose_number_from_frame_number(), exceeded MAX_ITS")
        raise AssertionError("In get_pose_number_from_frame_number(), escaped loop with no returned pose")

    def get_current_time_palette(self,palette_timing_list,frame):
        #figure out based upon frame number which palette should be used here
        palette_timing_index = frame
        current_palette = None
        time_for_one_loop = sum(x for x,_ in palette_timing_list)

        if time_for_one_loop == 0:            #static palette
            return palette_timing_list[0][1]
        else:
            palette_timing_index = palette_timing_index % time_for_one_loop

        for time,palette in palette_timing_list:
            palette_timing_index -= time
            if palette_timing_index <= 0 or time == 0:   #time = 0 is a special code for static palettes or "final" palettes
                return palette
        else:
            raise AssertionError(f"During get_sprite_pose() encountered modular arithmetic error while processing frame number {frame}")

    def get_all_poses(self):
        for animation, pose in [(animation, 0) for animation in self.animations.values()]:
            FAILSAFE_COUNTER = 100
            kicks = 0
            if animation in [0x00,0x9B]:
                kicks += 1    #loader stuff after elevator
            elif animation in [0x29,0x2A,0x67,0x68]:
                kicks += 1    #falling far distances
            elif animation in [0x19,0x1A,0x1B,0x1C,0x81,0x82]:
                kicks += 1    #walljump cue
            elif animation in [0xD3,0xD4]:
                kicks += 2    #crystal flash
            elif animation in [0xE9]:
                kicks += 3    #mother brain sequence
            elif animation in [0xEA,0xEB]:
                kicks += 1    #different type of mother brain sequence

            for _ in range(FAILSAFE_COUNTER):
                control_code, *_ = self.rom_data.get_pose_control_data(animation,pose)
                if control_code in [0xF6]:   #skip
                  pose += 1
                elif control_code in [0xF7,0xFB]:   #supplication sequence or walljump sequence
                  pose += 1
                  kicks += 2
                elif control_code in [0xF8,0xFD,0xFE]:   #1-byte argument terminal
                  pose += 2
                  kicks -= 1
                elif control_code in [0xFA]:   #2-byte argument terminal
                  pose += 3
                  kicks -= 1
                elif control_code in [0xFC]:   #4-byte argument terminal
                  pose += 5
                  kicks -= 1
                elif control_code in [0xF9]:   #6-byte argument terminal
                  pose += 7
                  kicks -= 1
                elif control_code in [0xFF]:   #just terminal
                  pose += 1
                  kicks -= 1
                else:
                  yield animation, pose
                  pose += 1
                
                if kicks < 0:    #end of the line
                  break
            else:
                raise AssertionError(f"Reached FAILSAFE_COUNTER in get_all_poses().  Animation {hex(animation)}, pose {hex(pose)}")

    def get_sprite_animation(self, animation_ID):
        raise NotImplementedError()

    def import_rgba_images_from_ROM(self):
        all_images = {}
        for image_name in [name for row in self._layout.get_rows() for name in row]:  #for every image referenced explicitly in the layout
            animation, pose = self._layout.data["images"][image_name]["used by"][0]   #import a representative animation and pose
            if type(animation) is str and animation[0:2] == "0x":                #convert from hex if needed
                animation = int(animation[2:], 16)

            force = self._layout.get_property("force", image_name)
            if force:
                if force.lower() == "upper":
                  image, origin = self.get_sprite_pose(animation, pose, None, lower=False)
                elif force.lower() == "lower":
                  image, origin = self.get_sprite_pose(animation, pose, None, upper=False)
                else:
                  raise AssertionError(f"received call to force something in pose {image_name}, but did not understand command '{force}'")
            else:
                image, origin = self.get_sprite_pose(animation, pose, None)

            if image:
                if image.mode == 'P':
                    image = util.apply_palette(image, self.get_sprite_palette("standard", "power", 0))
                all_images[image_name] = (image, origin)
            else:
                print(f"WARNING: Did not generate image for {image_name}")

        return all_images


    def export_PNG(self):
        images = self.import_rgba_images_from_ROM()     #TODO: Should also be able to import these from PNG or ZSPR
        return self._layout.export_all_images_to_PNG(images)
    
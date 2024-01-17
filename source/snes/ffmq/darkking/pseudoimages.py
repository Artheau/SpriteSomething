#pylint: disable=invalid-name
'''
Load Pseudoimage Props
'''
import os
from PIL import Image
from source.meta.common import common

def pseudoimages_test(save=False):
    '''
    Run pseudoimage-splitter
    '''
    pseudoimages = {}

    filenames = [ "darkkinga.png", "darkkingb.png" ]
    for filename in filenames:
        icon = filename[:filename.rfind('.')]
        pseudo_image = Image.open(
            os.path.join(
                ".",
                "resources",
                "app",
                "snes",
                "ffmq",
                "darkking",
                "sheets",
                filename
            )
        )

        pseudoimages[icon] = pseudo_image

    return pseudoimages

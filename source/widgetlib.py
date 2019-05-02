#common widgets, so as to easily populate the parts of the GUI that are delegated to other classes

def center_align_grid_in_frame(frame):
	frame.grid_columnconfigure(0, weight=1)       #the 0th column will be the margin
	frame.grid_columnconfigure(1000, weight=1)    #so I guess technically this just needs to be larger than the number of columns


def right_align_grid_in_frame(frame):
	frame.grid_columnconfigure(0, weight=1)       #the 0th column will be the margin
	frame.grid_columnconfigure(1000, weight=0)    #so I guess technically this just needs to be larger than the number of columns


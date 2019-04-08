#originally written by Artheau
#while suffering from delusions of grandeur
#in April 2019

import tkinter as tk
from PIL import Image, ImageTk

def main():
	root = tk.Tk()
	#window size
	root.geometry("400x300")
	app = AnimatorMainFrame(root)
	root.mainloop()

class AnimatorMainFrame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        #set the title    
        self.master.title("Sprite Animator")

        #main frame should take up the whole window
        self.pack(fill=tk.BOTH, expand=1)

        #create the menu bar
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        #create the file menu
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Load Sprite", command=self.load)
        file_menu.add_command(label="Export to ROM", command=self.export)
        file_menu.add_command(label="Exit", command=self.exit)
        #attach to the menu bar
        menu.add_cascade(label="File", menu=file_menu)

        #create the edit menu
        image_menu = tk.Menu(menu, tearoff=0)
        image_menu.add_command(label="Create GIF", command=self.create_gif)
        image_menu.add_command(label="Show Img", command=self.showImg)
        image_menu.add_command(label="Show Text", command=self.showText)
        #attach to the menu bar
        menu.add_cascade(label="Image", menu=image_menu)

        #create the help menu
        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="About", command=self.about)
        #attach to the menu bar
        menu.add_cascade(label="Help", menu=help_menu)

        #button example
        #quitButton = tk.Button(self, text="Quit", command=self.client_exit)
        #quitButton.place(x=0, y=0)

    def showImg(self):
        load = Image.open("houlihan.png")
        render = ImageTk.PhotoImage(load)

        # labels can be text or images
        img = tk.Label(self, image=render)
        img.image = render
        img.place(x=0, y=0)


    def showText(self):
        text = tk.Label(self, text="Hello World!")
        text.pack()

    def load(self):
        #TODO: implement loading from ROM, later expand to other formats
        pass

    def export(self):
        #TODO: implement exporting to ROM, later expand to other formats
        pass

    def create_gif(self):
        #TODO: implement this
        pass

    def about(self):
        #TODO: Open up a window with information directing the user to the website/github/wiki
        pass

    def exit(self):
        #TODO: confirmation box
        exit()



if __name__ == "__main__":
	main()
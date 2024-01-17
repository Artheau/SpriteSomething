import tkinter as tk

class HyperlinkManager:

	def __init__(self, text):
		self.text = text

		self.text.tag_config("hyper", foreground="blue", underline=1)

		self.text.tag_bind("hyper", "<Enter>", self._enter)
		self.text.tag_bind("hyper", "<Leave>", self._leave)
		self.text.tag_bind("hyper", "<Button-1>", self._click)

		self.reset()

	def reset(self):
		self.links = {}

	def add(self, action):
		# add an action to the manager.	returns tags to use in
		# associated text widget
		tag = "hyper-%d" % len(self.links)
		self.links[tag] = action
		return "hyper", tag

	def _enter(self, event):
		self.text.config(cursor="hand2")

	def _leave(self, event):
		self.text.config(cursor="")

	def _click(self, event):
		for tag in self.text.tag_names(tk.CURRENT):
			if tag[:6] == "hyper-":
				self.links[tag]()
				return

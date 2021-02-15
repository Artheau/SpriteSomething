import distutils.dir_util	# for copying trees
import json								# for reading sprite folders
import os									# for env vars
from shutil import copy, make_archive, move, rmtree	# file manipulation

# make dir to put app icon in
checkdir = os.path.join("..", "pages", "resources", "app", "meta", "icons")
if not os.path.isdir(checkdir):
	os.makedirs(checkdir)
# copy icon over
copy(
	os.path.join(".", "resources", "app", "meta", "icons", "app.gif"),
	os.path.join("..", "pages", "resources", "app", "meta", "icons")
)

# make dir to put build version in
checkdir = os.path.join("..", "pages", "resources", "app", "meta", "manifests")
if not os.path.isdir(checkdir):
	os.makedirs(checkdir)
# copy app_version over
copy(
	os.path.join("..", "build", "app_version.txt"),
	os.path.join("..", "pages", "resources", "app", "meta", "manifests")
)
# copy badges manifest over
copy(
	os.path.join(".", "resources", "app", "meta", "manifests", "badges.json"),
	os.path.join("..", "pages", "resources", "app", "meta", "manifests")
)

# copy GitHub Pages files to staging area
# copy index page
copy(
	os.path.join(".", "html", "index.html"),
	os.path.join("..", "pages")
)

# copy sprite previews
distutils.dir_util.copy_tree(
	os.path.join(".", "html"),
	os.path.join("..", "pages", "resources", "app")
)

# copy over game data
consoles = {}
games = []
checkdir = os.path.join(".", "resources", "app")
for console in os.listdir(checkdir):
	if os.path.isdir(os.path.join(checkdir, console)):
		if not console == "meta":
			consoles[console] = []
			for game in os.listdir(os.path.join(checkdir, console)):
				if not game == "meta":
					consoles[console].append(game)
					gamedir = os.path.join("..",
																	"pages",
																	"resources",
																	"app",
																	console,
																	game
					)
					if not os.path.isdir(os.path.join(gamedir, "manifests")):
						os.makedirs(os.path.join(gamedir, "manifests"))
						distutils.dir_util.copy_tree(os.path.join(".",
																											"resources",
																											"app",
																											console,
																											game,
																											"manifests"
																				),
																				os.path.join(gamedir, "manifests")
						)
						distutils.dir_util.copy_tree(os.path.join(".",
																											"resources",
																											"app",
																											console,
																											game,
																											"lang"
																				),
																				os.path.join(gamedir, "lang")
						)

spriteTemplateFile = open(os.path.join(".",
																				"html",
																				"template",
																				"sprites-index.html"
																			)
)
spriteTemplate = spriteTemplateFile.read()
spriteTemplateFile.close()

# write consoles dirs to file
with open(os.path.join(
	"..",
	"pages",
	"resources",
	"app",
	"meta",
	"manifests",
	"consoles.txt"
), "w+") as consoleList:
	for console in consoles:
		consoledir = os.path.join("..", "pages", "resources", "app", console)
		consoleList.write("%s\n" % console)
		# write games dirs to file
		with open(os.path.join(
			"..",
			"pages",
			"resources",
			"app",
			console,
			"games.txt"
		), "w+") as gameList:
			for game in consoles[console]:
				gamedir = os.path.join(consoledir, game)
				gameList.write("%s\n" % game)
				sprites = []
				with open(os.path.join(
					gamedir,
					"manifests",
					"manifest.json"
				)) as manifestFile:
					manifest = json.load(manifestFile)
					for key in manifest:
						if key != "$schema":
							if "folder name" in manifest[key]:
								sprites.append(manifest[key]["folder name"])
								for sprite in sprites:
									spritedir = os.path.join(gamedir, sprite)
									if not os.path.isdir(spritedir):
										os.makedirs(spritedir)
										# Backwards compatibility
										copy(
												os.path.join(".", "html", "template", "sprites-redir.html"),
												os.path.join(spritedir, "sprites.html")
										)
										with open(os.path.join(
												spritedir,
												"index.html"
										), "w+") as spriteFile:
											thisSpriteTemplate = spriteTemplate.replace(
													"<CONSOLE>", console)
											thisSpriteTemplate = thisSpriteTemplate.replace(
													"<GAME>", game)
											thisSpriteTemplate = thisSpriteTemplate.replace(
													"<SPRITE>", sprite)
											spriteFile.write(thisSpriteTemplate)

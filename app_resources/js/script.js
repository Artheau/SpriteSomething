function readTextFile(file) {
  let rawFile = new XMLHttpRequest();
  let allText = "";
  rawFile.open("GET", file, false);
  rawFile.onreadystatechange = function () {
    if(rawFile.readyState === 4) {
      if(rawFile.status === 200 || rawFile.status == 0) {
        allText = rawFile.responseText;
      }
    }
  }
  rawFile.send(null);

  return allText;
}

function init(mode = "index") {
	if(mode == "index") {
	  let VERSION = readTextFile(".\\app_resources\\meta\\manifests\\app_version.txt");
	  document.title += " v" + VERSION;

		let title = document.createElement("h1");
		title.setAttribute("id","title");
		title.innerHTML = "SpriteSomething";
		document.body.appendChild(title);

		let subtitle = document.createElement("h2");
		let version_a = document.createElement("a");
		version_a.setAttribute("id","version");
		version_a.innerHTML = "Current Version: v" + VERSION;
	  version_a.href = "https://github.com/Artheau/SpriteSomething/releases/tag/v" + VERSION;
		subtitle.appendChild(version_a);
		document.body.appendChild(subtitle);

		let list_ul = document.createElement("ul");
		let list_li = document.createElement("li");
		list_li.innerHTML = "Custom Sprite Repositories";
		let games_list = document.createElement("ul");
		games_list.setAttribute("id","games-list");
		list_li.appendChild(games_list);
		list_ul.appendChild(list_li);
		document.body.appendChild(list_ul);

	  let games = readTextFile(".\\app_resources\\meta\\manifests\\games.txt");
	  games = games.split("\n");
	  for(let game in games) {
	    game = games[game];
	    if(game != "") {
	      let game_li = document.createElement("li");
	      let sprites_ul = document.createElement("ul");
	      let sprite_li = document.createElement("li");
	      let sprite_a = document.createElement("a");
	      let game_name = game;
	      let en_lang = readTextFile(".\\app_resources\\" + game + "\\lang\\en.json");
	      en_lang = JSON.parse(en_lang);
	      if("game" in en_lang) {
	        if("name" in en_lang["game"]) {
	          game_name = en_lang["game"]["name"];
	        }
	      }

	      game_li.innerHTML = game_name;

	      let manifest = readTextFile(".\\app_resources\\" + game + "\\manifests\\manifest.json");
	      manifest = JSON.parse(manifest);
	      for(let key in manifest) {
	        let value = manifest[key];
	        if(key != "$schema") {
	          if("folder name" in value) {
	            let name = value["name"];
	            let sprite = value["folder name"];
	            sprite_li = document.createElement("li");
	            sprite_a = document.createElement("a");
							sprite_a.href = "./?mode=" + game + '/' + sprite;
	            sprite_a.innerHTML = name;
	            sprite_li.appendChild(sprite_a);
	            sprites_ul.appendChild(sprite_li);
	          }
	        }
	      }
	      game_li.appendChild(sprites_ul);
	      games_list.appendChild(game_li);
	    }
	  }
	} else {
		mode = mode.split('/');
		let game = mode[0];
		let sprite = mode[1];

		let title = document.createElement("h1");
		title.setAttribute("id","title");
		title.innerHTML = sprite.substring(0,1).toUpperCase() + sprite.substring(1) + " Sprites";
		document.body.appendChild(title);

		let link = document.createElement("link");
		link.setAttribute("rel","stylesheet");
		link.type = "text/css";

		let filepath = window.location.pathname;
		filepath += "app_resources/";
		filepath += game + '/';
		filepath += sprite + '/';
		link.href = filepath + "css.css";

		document.head.appendChild(link);

		let filename = filepath + "sprites.json";
	  let spritesManifest = readTextFile(filename);	// get sprites manifest
	  let sprites = JSON.parse(spritesManifest);				// parse JSON
	  sprites.sort(function(a,b) {								// sort by name
	    return a.name.localeCompare(b.name);
	  });

		filename = filepath + "layer-files.json";
		let layerfilesManifest = readTextFile(filename);
		let layerfiles = JSON.parse(layerfilesManifest);
		let layerfiles_container = document.createElement("ul");
		for (let layerext in layerfiles) {
			let layerfile = layerfiles[layerext];
			let app = layerfile["app"];
			let file = layerfile["file"];
			let site = layerfile["site"];
			let repo = layerfile["repo"];
			metas = new Array(
//												layerext,
												file,
												site,
												repo
			);

			let layerfile_li = document.createElement("li");
			layerfile_li.innerHTML = app;
			layerfile_meta_ul = document.createElement("ul");

			for(let meta in metas) {
				let meta_text = metas[meta];
				if(meta_text) {
					layerfile_meta_li = document.createElement("li");
					let layerfile_meta_a = document.createElement("a");
					let link_text = "";
					switch(meta) {
						case "0":
							link_text = layerext == "png" ? "PNG" : "Layer File";
							break;
						case "1":
							link_text = "Website";
							break;
						case "2":
							link_text = "Source Code";
							break;
					}
					if(meta_text.indexOf("alttpr") > -1) {
						switch(meta) {
							case "0":
								link_text = "Machine-readable Endpoint";
								break;
							case "1":
								link_text = "Sprite Previews";
								break;
						}
					}
					layerfile_meta_a.innerHTML = link_text;
					layerfile_meta_a.href = meta_text;
					layerfile_meta_li.appendChild(layerfile_meta_a);
					layerfile_meta_ul.appendChild(layerfile_meta_li);

					if(link_text == "Sprite Previews") {
						link_text = "Downloadable Sprite Previews";
						meta_text = "http://alttp.mymm1.com/sprites";
						layerfile_meta_li = document.createElement("li");
						layerfile_meta_a = document.createElement("a");
						layerfile_meta_a.innerHTML = link_text;
						layerfile_meta_a.href = meta_text;
						layerfile_meta_li.appendChild(layerfile_meta_a);
						layerfile_meta_ul.appendChild(layerfile_meta_li);
					}
				}
			}
			layerfile_li.appendChild(layerfile_meta_ul);
			layerfiles_container.appendChild(layerfile_li);
		}

		sprites_container = document.createElement("div");
		sprites_container.setAttribute("id","sprites_container")

	  for (let sprite in sprites) {								// iterate through sprites
	    sprite = sprites[sprite];								// get this sprite
	    let name = sprite.name;									// sprite name
	    let author = sprite.author;								// sprite author
	    let file = sprite.file;									// sprite url
	    let sprite_object = document.createElement("div");		// main container
	    let name_line = document.createElement("div");			// name container
	    let name_link = document.createElement("a");			// name link
	    let author_line = document.createElement("div");		// author container
	    let sprite_image = document.createElement("div");		// image container

	    sprite_object.className = "sprite";

	    name_link.innerHTML = name;
	    name_link.href = file;
	    name_line.className = "name";
	    name_line.appendChild(name_link);

	    author_line.innerHTML = author;
	    author_line.className = "author";

	    sprite_image.className = "sprite-preview";
	    sprite_image.style.backgroundImage = "url(" + file + ')';

	    sprite_object.appendChild(name_line);
	    sprite_object.appendChild(author_line);
	    sprite_object.appendChild(sprite_image);

	    sprites_container.appendChild(sprite_object);
	  }

		document.body.appendChild(sprites_container);
		let spacer = document.createElement("div");
		spacer.style.clear = "both";
		document.body.appendChild(spacer);
		document.body.appendChild(layerfiles_container);
	}
}

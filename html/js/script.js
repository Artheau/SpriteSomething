// Read a text file
function readTextFile(file) {
  // Create a request
  let rawFile = new XMLHttpRequest();
  let allText = "";
  // Get the thing
  rawFile.open("GET", file, false);
  rawFile.onreadystatechange = function () {
    // If we're ready to read
    if(rawFile.readyState === 4) {
      // If it's OK
      if(rawFile.status === 200 || rawFile.status == 0) {
        // Return the thing
        allText = rawFile.responseText;
      }
    }
  }
  rawFile.send(null);

  return allText;
}

function init(mode = "index") {
  // Index
	if(mode == "index") {
    // Version
	  let VERSION = readTextFile(".\\resources\\app\\meta\\manifests\\app_version.txt").trim();
	  document.title += " v" + VERSION;

    // SpriteSomething
		let title = $("<h1></h1>")
			.attr({"id": "title"})
			.text("SpriteSomething");
		$("body").append(title);

    // Version hyperlink
		let subtitle = $("<h2><a>");
		let version_a = $("<a>")
			.attr("id","version")
			.attr("href","https://github.com/Artheau/SpriteSomething/releases/tag/v" + VERSION)
			.text("Current Version: v" + VERSION);
		subtitle.append(version_a);
		$("body").append(subtitle);

		let list_li = $("<ul><li>")
			.text("Custom Sprite Repositories");
    let consoles_list = $("<ul>")
      .attr("id","consoles-list");
    list_li.append(consoles_list);
		$("body").append(list_li);

    let consoles = readTextFile(".\\resources\\app\\meta\\manifests\\consoles.txt");
    consoles = consoles.split("\n");
    for(let console in consoles) {
      console = consoles[console];
      if(console != "") {
        let console_li = $("<li>").text(console.toUpperCase());
        let consoleGames = readTextFile(".\\resources\\app\\" + console + "\\games.txt");
        consoleGames = consoleGames.split("\n");
        for(let game in consoleGames) {
          game = consoleGames[game];
          if(game != "") {
            let games_ul = $("<ul>");
    	      let game_li = $("<li>");
    	      let sprites_ul = $("<ul>");
    	      let sprite_li = $("<li>");
    	      let sprite_a = $("<a>");
    	      let en_lang = readTextFile(".\\resources\\app\\" + console + "\\" + game + "\\lang\\en.json");
    	      en_lang = JSON.parse(en_lang);
    	      if("game" in en_lang) {
    	        if("name" in en_lang["game"]) {
    	          game_li.text(en_lang["game"]["name"]);
    	        }
    	      }

    	      let manifest = readTextFile(".\\resources\\app\\" + console + "\\" + game + "\\manifests\\manifest.json");
    	      manifest = JSON.parse(manifest);
    	      for(let key in manifest) {
    	        let value = manifest[key];
    	        if(key != "$schema") {
    	          if("folder name" in value) {
    	            let name = value["name"];
    	            let sprite = value["folder name"];
    	            sprite_li = $("<li>");
    	            sprite_a = $("<a>")
    	            	.attr("href","./?mode=" + console + '/' + game + '/' + sprite)
    	            	.text(name);
    	            sprite_li.append(sprite_a);
    	            sprites_ul.append(sprite_li);
    	          }
    	        }
    	      }
    	      game_li.append(sprites_ul);
            games_ul.append(game_li);
            console_li.append(games_ul);
    	      consoles_list.append(console_li);
          }
        }
      }
    }

	  let manifest = readTextFile(".\\resources\\app\\meta\\manifests\\badges.json");
	  let badges = JSON.parse(manifest);
	  for(badge in badges) {
		  badge = badges[badge];
		  let label = badge["title"];
		  let query = badge["query"];
		  let left = badge["left"];
		  let logo = "logo" in badge ? badge["logo"] : "";
		  let logo_color = "logo-color" in badge ? badge["logo-color"] : "";
		  let repo = "Artheau/SpriteSomething";
		  let url = "https://img.shields.io/";
		  url += badge["keyword"];
		  url += '/';
		  url += repo;
		  url += (query.indexOf('?') == -1) ? '/' : '';
		  url += query;
		  url += (query.indexOf('?') == -1) ? '?' : '&';
		  url += "style=flat-square";
		  if(left != "") {
		    url += '&' + "label=" + left.replace(/ /g,"%20");
		  }
		  if(logo != "") {
		    url += '&' + "logo=" + logo;
		  }
		  if(logo_color != "") {
		    url += '&' + "logoColor=" + logo_color;
		  }
		  url = url.replace(/<LATEST_TAG>/g,'v'+VERSION);
		  let shield = $("<div>");
		  let img = $("<img>")
		  	.attr("src",url);
		  if(badge["url"] != "") {
		    let a = $("<a>")
		    	.attr("href",badge["url"].replace(/<LATEST_TAG>/g,'v'+VERSION));
		    a.append(img);
		    shield.append(a);
		  } else {
		    shield.append(img);
		  }
		  $("body").append(shield);
	  }
	} else {
		mode = mode.split('/');
    let console = mode[0];
		let game = mode[1];
		let sprite = mode[2];

		let title = $("<h1>")
			.attr("id","title")
			.text(sprite.substring(0,1).toUpperCase() + sprite.substring(1) + " Sprites");
        $("body").append(title);

		let filepath = window.location.pathname;
		filepath += "resources/app/";
    filepath += console + '/';
		filepath += game + '/';
		filepath += sprite + '/';
		let link = $("<link>")
			.attr("rel","stylesheet")
			.attr("type","text/css")
			.attr("href",filepath + "css.css");
        $("head").append(link);

		let filename = filepath + "sprites.json";
	  let spritesManifest = readTextFile(filename);	// get sprites manifest
	  let sprites = JSON.parse(spritesManifest);				// parse JSON
	  sprites.sort(function(a,b) {								// sort by name
	    return a.name.localeCompare(b.name);
	  });

		filename = filepath + "layer-files.json";
		let layerfilesManifest = readTextFile(filename);
		let layerfiles = JSON.parse(layerfilesManifest);
		let layerfiles_container = $("<ul>");
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

			let layerfile_li = $("<li>")
				.text(app);
			layerfile_meta_ul = $("<ul>");

			for(let meta in metas) {
				let meta_text = metas[meta];
				if(meta_text) {
					layerfile_meta_li = $("<li>");
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
					let layerfile_meta_a = $("<a>")
						.attr("href",meta_text)
						.text(link_text);
					layerfile_meta_li.append(layerfile_meta_a);
					layerfile_meta_ul.append(layerfile_meta_li);

					if(link_text == "Sprite Previews") {
						link_text = "Downloadable Sprite Previews";
						meta_text = "http://alttp.mymm1.com/sprites";
						layerfile_meta_li = $("<li>");
						layerfile_meta_a = $("<a>")
							.attr("href",meta_text)
							.text(link_text);
						layerfile_meta_li.append(layerfile_meta_a);
						layerfile_meta_ul.append(layerfile_meta_li);
					}
				}
			}
			layerfile_li.append(layerfile_meta_ul);
			layerfiles_container.append(layerfile_li);
		}

	  let sprites_container = $("<div>")
			.attr("id","sprites_container");

	  for (let sprite in sprites) {								// iterate through sprites
	    sprite = sprites[sprite];								// get this sprite
	    let name = sprite.name;									// sprite name
	    let author = sprite.author;								// sprite author
	    let file = sprite.file;									// sprite url
	    let name_link = $("<a>")
	    	.attr("href",file)
	    	.text(name);			// name link
	    let name_line = $("<div>")
	    	.attr("class","name")
	    	.append(name_link);			// name container
	    let author_line = $("<div>")
	    	.attr("class","author")
	    	.text(author);		// author container
	    let sprite_image = $("<div>")
	    	.attr("class","sprite-preview")
	    	.attr("style","background-image:url(" + file + ")");		// image container
	    let sprite_object = $("<div>")
	    	.attr("class","sprite")
	    	.append(name_line)
	    	.append(author_line)
	    	.append(sprite_image);		// main container
	    sprites_container.append(sprite_object);
	  }

		$("body").append(sprites_container);
		let spacer = $("<div>")
			.attr("style","clear:both");
		$("body").append(spacer);
		$("body").append(layerfiles_container);
	}
}

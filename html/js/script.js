// Read a text file
function readTextFile(file) {
  // Create a request
  let rawFile = new XMLHttpRequest();
  let allText = "";
  rawFile.onreadystatechange = function () {
    // If we're ready to read
    if (rawFile.readyState === 4) {
      // If it's OK
      if (rawFile.status === 200 || rawFile.status == 0) {
        // Return the thing
        allText = rawFile.responseText;
        // If it's not OK
      } else if (rawFile.status === 404) {
        // Return null
        return null;
      }
    }
  };

	// Get the thing
	rawFile.open("GET", file, false);
	rawFile.send(null);

	return allText;
}

function forkMe() {
  let title = "Contribute yours!";
  let stylesheet = $("<link>").attr({
    rel: "stylesheet",
    href: "https://cdnjs.cloudflare.com/ajax/libs/github-fork-ribbon-css/0.2.3/gh-fork-ribbon.min.css",
    type: "text/css",
  });
  let a = $("<a>")
    .attr({
      class: "github-fork-ribbon right-top",
      href: "https://github.com/miketrethewey/SpriteSomething-collections/blob/gh-pages/CONTRIBUTING.md",
      "data-ribbon": title,
      title: title,
    })
    .text(title);
  $("head").append(stylesheet);
  $("body").append(a);
}

function init(mode = "index") {
	// Index
	if (mode == "index") {
		forkMe();

    // Version
    let VERSION = readTextFile(
      ".\\resources\\app\\meta\\manifests\\app_version.txt"
    ).trim();
    document.title += " v" + VERSION;

    // SpriteSomething
    let title = $("<h1></h1>")
      .attr({
        id: "title",
      })
      .text("SpriteSomething");
    $("body").append(title);

    // Version hyperlink
    let subtitle = $("<h2><a>");
    let version_a = $("<a>")
      .attr({
        id: "version",
        href:
          "https://github.com/Artheau/SpriteSomething/releases/tag/v" + VERSION,
      })
      .text("Current Version: v" + VERSION);
    subtitle.append(version_a);
    $("body").append(subtitle);

    let list_ul = $("<ul>");
    let list_li_a = $("<a>")
      .attr({
        href: "https://miketrethewey.github.io/SpriteSomething-collections/",
      })
      .text("Custom Sprite Repositories");
    let list_li = $("<li>").append(list_li_a);
    list_ul.append(list_li);
    $("body").append(list_ul);

    let manifest = readTextFile(
      ".\\resources\\app\\meta\\manifests\\badges.json"
    );
    let badges = JSON.parse(manifest);
    for (let badge in badges) {
      badge = badges[badge];
      let label = badge["title"];
      let query = badge["query"];
      let left = badge["left"];
      let logo = badge.hasOwnProperty("logo") ? badge["logo"] : "";
      let logo_color = badge.hasOwnProperty("logo-color") ? badge["logo-color"] : "";
      let repo = "Artheau/SpriteSomething";
      let url = "https://img.shields.io/";
      url += badge["keyword"];
      url += "/";
      url += repo;
      url += query.indexOf("?") == -1 ? "/" : "";
      url += query;
      url += query.indexOf("?") == -1 ? "?" : "&";
      url += "style=flat-square";
      if (left != "") {
        url += "&" + "label=" + left.replace(/ /g, "%20");
      }
      if (logo != "") {
        url += "&" + "logo=" + logo;
      }
      if (logo_color != "") {
        url += "&" + "logoColor=" + logo_color;
      }
      url = url.replace(/<LATEST_TAG>/g, "v" + VERSION);
      let shield = $("<div>");
      let img = $("<img>").attr({
        src: url,
        title: label,
      });
      if (badge["url"] != "") {
        let a = $("<a>").attr({
          href: badge["url"].replace(/<LATEST_TAG>/g, "v" + VERSION),
        });
        a.append(img);
        shield.append(a);
      } else {
        shield.append(img);
      }
      $("body").append(shield);
    }
  }
}

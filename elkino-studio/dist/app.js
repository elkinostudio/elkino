import { works } from "./works.js";

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function link(text, href, className) {
  const node = element("a", text, className);
  node.href = href;
  return node;
}

function visual(work) {
  const image = element("img");
  image.src = "./assets/" + work.image;
  image.alt = work.alt;
  image.width = 1280;
  image.height = 720;
  return image;
}

function card(work) {
  const entry = element("article", "", "card");
  const target = link("", "?work=" + encodeURIComponent(work.slug));
  const image = visual(work);
  image.loading = "lazy";
  image.alt = "";
  target.append(
    image,
    element("p", work.newest ? "Latest featured film · " + work.series : work.series, "eyebrow"),
    element("h3", work.title),
    element("span", "Film details ↗", "line"),
  );
  entry.append(target);
  return entry;
}

const selection = new URLSearchParams(location.search).get("work");
const active = works.find(work => work.slug === selection);
if (selection) {
  document.querySelector("#home").hidden = true;
  const detail = document.querySelector("#detail");
  detail.hidden = false;
  detail.append(link("← Film archive", "./#films", "line"));
  if (active) {
    document.title = active.title + " | Elkino Studio";
    detail.append(element("p", active.series, "eyebrow"), element("h1", active.title), visual(active));
    const info = element("div", "", "detail-info");
    info.append(element("p", active.description), link("Watch on YouTube ↗", active.video, "button dark"));
    detail.append(info);
    const related = active.related.map(slug => works.find(work => work.slug === slug)).filter(Boolean);
    if (related.length) {
      const relatedGrid = element("div", "", "grid");
      relatedGrid.append(...related.map(card));
      detail.append(element("h2", "Related films"), relatedGrid);
    }
  } else {
    detail.append(element("h1", "Film unavailable"));
  }
} else {
  const list = document.querySelector("#films-grid");
  const filters = [...document.querySelectorAll("[data-filter]")];
  function render(filter) {
    const chosen = works.filter(work => filter === "all" || work.theme === filter);
    list.replaceChildren(...chosen.map(card));
  }
  for (const button of filters) {
    button.addEventListener("click", () => {
      for (const filter of filters) filter.setAttribute("aria-pressed", String(filter === button));
      render(button.dataset.filter);
    });
  }
  render("all");
}

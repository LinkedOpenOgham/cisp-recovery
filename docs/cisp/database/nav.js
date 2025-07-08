/**
 * Speichert Site-Informationen im Browser (statt parent.*)
 */
function navset(site, st_n, st_l) {
  localStorage.setItem("site", site);
  localStorage.setItem("stoneNumber", st_n);
  localStorage.setItem("stoneLabel", st_l);
  window.focus();
}

/**
 * Öffnet eine Bildseite in einem neuen Tab
 * @param {string} impage - Dateiname ohne Endung
 */
function showimage(impage) {
  const url = `../picpage/${impage}.html`;
  window.open(url, "_blank", "noopener,noreferrer");
}

/**
 * Öffnet eine Kartenansicht in einem neuen Tab
 * Übergibt site ggf. per window.IFL (falls Zielseite es nutzt)
 * @param {string} maptag - z. B. "clmac"
 * @param {string} site - z. B. "clmac"
 */
function showmap(maptag, site) {
  const url = `../maps/${maptag}_all.html`;
  window.open(url, "_blank", "noopener,noreferrer");
}

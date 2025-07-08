function navset(site,st_n,st_l)
{
  parent.site = site;
  parent.st_n = st_n;
  parent.st_l = st_l;
  focus();
}

function showimage(impage) {
  w = window.open("../picpage/" + impage + ".html","im","toolbar=no,scrollbars,resizable");
  w.focus();
}


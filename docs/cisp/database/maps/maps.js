
function loaded() {
  var op = window.opener;
  if (op == null) return;
  var si = window.opener.FLASHSITE;
  if (si != null) {
    flashsym(si);
  } 
}

function mover(msg) {
  status=msg;
}

function flashsym(site) {

  document.IMAP.JSFlash(site);
}

function jumpTo ( site ) {
  var all = document.all;
  var x , y , r;
  if (all == null) {
     r = document.anchors[site];
     x = r.x;
     y = r.y;
   } else {
     r = document.all.item(site);
     x = r.offsetLeft;
     y = r.offsetTop;
   }
  scrollTo ( x , y );
}


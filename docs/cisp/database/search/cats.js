
  
function MyOption ( text , value ) {
  this.text = text;
  this.value = value;
  }

MyOption.prototype.opt = function() {
 return new Option ( this.text , this.value );
  }
  
 
function Cats() {
  }
Cats.prototype.newcat = function ( cat ) {
  this[cat] = new Array();
  this.lastcat = cat;
  }

Cats.prototype.addcat = function ( cat , text , value ) {
  this[cat][this[cat].length] = new MyOption ( text , value );
  }
  
Cats.prototype.add  = function (text , value ) {
  this.addcat ( this.lastcat , text , value );
  }
  
Cats.prototype.setopts  = function ( sel , cat ) {
  var i;
  if (this[cat] == null) return 0;
  sel.options.length = 0;
  for (i = 0 ; i < this[cat].length ; ++i ) {
    sel.options[i] = this[cat][i].opt();
    }
  sel.selectedIndex = 0;
  return 1;
 }

  


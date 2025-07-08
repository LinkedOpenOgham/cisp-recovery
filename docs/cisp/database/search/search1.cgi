#!/usr/local/rbin/tcl8

source setlib.tcl

source $lib/http-query-setup.tcl
source $lib/setup.tcl
source $lib/indexctrl.tcl
source $lib/menumap.tcl
source $lib/mapdata.tcl
source $lib/maputils.tcl


proc main {} {
global RESULTS ar
getcgivars
makesql
genoutput $ar(opfmt)
}


proc showvars {} {
global ar
getcgivars
puththdr plain
foreach {k val} [array get ar] {
  puts "set ar($k) \"$ar($k)\""
  }
}

proc showsql {} {
global RESULTS ar
getcgivars
puththdr plain
makesql
puts "$RESULTS(sql)
"
catch {puts $RESULTS(exsql)}

foreach {k val} [array get ar] {
  puts "set ar($k) \"$ar($k)\""
  }

}


proc getcgivars {} {
global ar
catch {http_proc_cgi_args}
}

proc mitem key { return $::MENUMAP($key) }

proc makesql {} {
global RESULTS
global ar TABLES INDEXCTRL TARGET ITABLES
catch {unset TARGET}
catch {unset TABLES}
catch {unset RESULTS}
catch {unset ::OPCOLSTASH}
set ::OPSELECT {}
catch {unset ::ORDER}
set res {}
addoutputcolumn Site {SITE.NAME}
set TABLES(SITE) 1
for {set sr 0} {$sr < $ar(row)} {incr sr} {
  if {[catch {mitem $ar(f$sr)} cv]} {continue}
  set TABLES([lindex $cv 0]) 1
  if {[regexp {^=(.*)$} [lindex $cv 1] dum cmd]} {
     set r1 [PR_$cmd $sr]
     } else {
     set cspec [join [lrange $cv 0 1] .]
     if {[info exist ar(tsh$sr)]} {
       addoutputcolumn [lindex $cv 2] $cspec
       addorder $cspec SELECTION
       }
     set cl {}
     for {set sc 0} {$sc < $ar(col)} {incr sc} {
       if {[catch {mitem $ar(c${sr}_$sc)} val ]} {continue}
       lappend cl "($cspec IN ($val))"
       }
     set r1 [join $cl { OR }]
     }
  if {$r1 == {}} {continue}
  if {[info exist ar(tx$sr)]} {
    lappend res "( NOT ($r1))"
    } else {
    lappend res ($r1)
    }
 }
 
for {set sr 0} {$sr < $ar(ranges)} {incr sr} {
  if {[catch {mitem $ar(rf$sr)} cv]} {continue}
  set TABLES([lindex $cv 0]) 1
  if {[regexp {^=(.*)$} [lindex $cv 1] dum cmd]} {
     set r1 [PR_$cmd $sr]
     } else {
     set cspec [join [lrange $cv 0 1] .]
     if {[info exist ar(rsh$sr)]} {
       addoutputcolumn [lindex $cv 2] $cspec
       addorder $cspec RANGE
       }
     set cl {}
     foreach val [parserange $ar(rv$sr)] {
       lappend cl "($cspec $val)"
       }
     set r1 [join $cl { OR }]
     }
  if {$r1 == {}} {continue}
  if {[info exist ar(rx$sr)]} {
    lappend res "( NOT ($r1))"
    } else {
    lappend res ($r1)
    }
  
 }
 
for {set txti 0} {$txti <= 0} {incr txti} {
  if {![info exist ar(txt$txti)]} {continue}
  foreach cat $ar(txt$txti) {
    if {$cat == "READING"} {set cat INSCRIP}
    set TABLES($cat) 1
    }
 }

settargettable
set RESULTS(TARGET) $TARGET

array set tabkeys $INDEXCTRL(TABPREFIXES)
set KLIST $tabkeys(READING)

inittctr
set ITABLES {}

for {set txti 0} {$txti <= 0} {incr txti} {
  catch {unset ijoins}
  if {![info exist ar(txt$txti)]} {continue}
  foreach cat $ar(txt$txti) {
     lappend ijoins([min [llength $tabkeys($cat)] [llength $tabkeys($TARGET)]]) $cat
     }

  set jlist {}
  foreach {n tlist} [array get ijoins] {
    lappend jlist [lrange $KLIST 0 [incr n -1]] "('[join $tlist ',']')"
    }
   
  array set rtab [reduceinput $ar(txtv$txti)]
  
  foreach w $rtab(I+) {
    set tn [getntab]
    lappend ITABLES $tn
    lappend res "$tn.WORD LIKE '$w' AND ([mkijoins $tn $jlist])"
    }
    
    
  set tn [getntab]
  set orcl {}
  foreach w $rtab(I) { lappend orcl "$tn.WORD LIKE '$w'" }
  if {$orcl != {}} {
    lappend ITABLES $tn
    lappend res "(([join $orcl { OR }]) AND ([mkijoins $tn $jlist]))"
    }
  }   
  
  set tn [getntab]
  set excl {}
  if {[info exist rtab(I-)]} {
  foreach w $rtab(I-) {lappend excl "$tn.WORD LIKE '$w'" }
  if {$excl != {}} {
     set RESULTS(exsql) "select distinct [mkselectlist 1] from $TARGET , WORDINDEX $tn WHERE
(([join $excl { OR }]) AND ([mkijoins $tn $jlist]))"
     }
    }
  set slist [mkselectlist]
  
  set RESULTS(sql) "select distinct $slist 
FROM 
[mkfrom] 
WHERE
[joinx [list [mktjoins] [join $res { AND }]] {
AND 
}] 
ORDER BY 
[mkorder]"
  


}

proc PR_decoration sr { 
global TABLES ar
set table DECORATN
set TABLES($table) 1
set cspec $table.DECOR_CODE
set cl {}
for {set sc 0} {$sc < $ar(col)} {incr sc} {
    if {[catch {mitem $ar(c${sr}_$sc)} val ]} {continue}
    lappend cl "($cspec IN ($val))"
    }
set r1 [join $cl { OR }]
if {[info exist ar(tsh$sr)]} {
 addoutputcolumn [lindex [mitem $ar(f$sr)] 2] $cspec
 addorder $cspec SELECTION
 }
return $r1
} 

proc PR_museum sr {
global TABLES ar
set table MUSEUM
set TABLES($table) 1
set cspec $table.MUS
if {[info exist ar(tsh$sr)]} {
 addoutputcolumn [lindex [mitem $ar(f$sr)] 2] $cspec
 addorder $cspec SELECTION
 }
return {}
}

proc PR_lost sr { return [PR_RANGE $sr LOST DATE_LAST_PRESENT DATE_MISSING] }

proc PR_insdate sr { return [PR_RANGE $sr DATE_V DATE_FROM DATE_TO AUTHORITY] }

proc PR_RANGE { sr table d0 d1 {attrib {}} } {
global TABLES ar
set TABLES($table) 1
set d0 $table.$d0
set d1 $table.$d1
if {[info exist ar(rsh$sr)]} {
  if {$attrib == {}} {
    addoutputcolumn [lindex [mitem $ar(rf$sr)] 2] [list $d0 $d1] "%s - %s"
  } else {
    addoutputcolumn [lindex [mitem $ar(rf$sr)] 2] [list $d0 $d1 $attrib] "%s - %s (%s)"
  }
  addorder $d0 RANGE
  }
set res {}
foreach val [parserange $ar(rv$sr)] {
  set li [split $val]
  switch [lindex $li 0] {
     BETWEEN {set r "$d0 $val OR $d1 $val"}
     >= {set r "$d1 $val"}
     <= {set r "$d0 $val"}
     =  {set r "[lindex $li 1] BETWEEN $d0 AND $d1"}
  }
  lappend res ($r)
 }
 return "[join $res { OR }]"
}
  
proc PR_rddate sr {
global TABLES ar
set table READING
set TABLES($table) 1
set cspec $table.WHEN
if {[info exist ar(rsh$sr)]} {
  addoutputcolumn [lindex [mitem $ar(rf$sr)] 2] [list $cspec $table.BY_WHOM] "%s (%s)"
  addorder $cspec RANGE
  }
set res {}
foreach val [parserange $ar(rv$sr)] {
  
  lappend res "($cspec $val)"
 }
 return "[join $res { OR }]"
}

proc joinx {l {str " "}} {
set r ""
set sep ""
foreach item $l {
  if {$item == {}} {continue}
  set r "$r$sep$item"
  set sep $str
  }
return $r
}

proc mkijoins { tn jlist } {
global TARGET
set res {}
  foreach {kl cats} $jlist {
    set ks {}
    foreach k $kl { lappend ks "$tn.$k = $TARGET.$k" }
    lappend res "([join $ks { AND }] AND $tn.CATEGORY IN $cats)"
    }
return [join $res " OR "]
}

proc mktjoins {} {
global TARGET TABLES INDEXCTRL
array set tabkeys $INDEXCTRL(TABPREFIXES)
set KLIST $tabkeys(READING)

set res {}
foreach tab [array names TABLES] {
  if {$tab == $TARGET} {continue}
  set n [llength $tabkeys($tab)]
  foreach k [lrange $KLIST 0 [incr n -1]] {
    lappend res "$tab.$k = $TARGET.$k"
    }
  }
return [join $res " AND "]
}

proc mkfrom {} {
global TABLES ITABLES
set res [array names TABLES]
foreach it $ITABLES { lappend res "WORDINDEX $it" }
return [join $res " , "]
}

proc mkselectlist {{keys 0}} {
global TARGET INDEXCTRL RESULTS OPSELECT
array set tabkeys $INDEXCTRL(TABPREFIXES)
set res {}
set n -1
foreach k $tabkeys($TARGET) {
  lappend res $TARGET.$k
  incr n
  }
set RESULTS(keynum) $n
if {$keys == 0} {
  set res [concat $res $OPSELECT]
  }
return [join $res " , "]
}
 
proc mkorder {} {
global ORDER
foreach type {RANGE SELECTION} {
  if {[info exist ORDER($type)]} {return [lindex $ORDER($type) 0]}
  }
return SITE.NAME
}

proc settargettable {} {
global TABLES TARGET ar
foreach t {SITE STONE INSCROSS NAMES INSCRIP} {
  if {[info exist TABLES($t)]} {
    set TARGET $t
    if {$TARGET == "INSCROSS"} {
      set TARGET STONE
      set TABLES(STONE) 1
      }
    if {$TARGET == "NAMES"} {
      set TARGET INSCRIP
      set TABLES(INSCRIP) 1
      }
    }
  }

if {![info exist TARGET]} {
  for {set i 0} {$i <= 0} {incr i} {
    catch {foreach f $ar(txt$i) {set ttarg($f) 1}}
    }
  foreach  t {SITE STONE INSCRIP READING} {
      if {[info exist ttarg($t)]} {set TARGET $t}
      }
  if {$TARGET == "READING"} {set TARGET INSCRIP}
  set TABLES($TARGET) 1
  }

}

proc addoutputcolumn { hdrtxt fields {format %s} } {
global RESULTS
if {[info exist ::OPCOLSTASH($hdrtxt)]} {return}
set ::OPCOLSTASH($hdrtxt) [llength $::OPSELECT]
set ::OPSELECT [concat $::OPSELECT $fields]
lappend RESULTS(COLHDRS) $hdrtxt
lappend RESULTS(OPCOLS) [list [llength $fields] $format]
}

proc addorder { field type } {
  lappend ::ORDER($type) $field
}

proc parserange str {
   set res {}
   foreach r [split $str ,] {
    if {[catch {regexp {^([><]?) *([0-9.]+)[^0-9.]*([0-9.]*)} [string trim $r] dum mod n1 n2}]} {
      return {}
      }
    set mod ${mod}=
    if {$n2 != ""} {
       set st "BETWEEN $n1 AND $n2"
     
     } else {
       set st "$mod $n1"
     }
    lappend res $st
   }
 return $res
}

proc reduceinput txt {
global INDEXNULLS 
  array set WTAB {I {} I+ {} I- {}}

  regsub -all {[^a-z *?\+-]} [string tolower $txt] " " txt
  regsub -all {([+-]) *} $txt {\1} txt 
  regsub -all { +} $txt " " txt
  regsub -all {\*} $txt "%" txt
  regsub -all {\?} $txt "_" txt
  foreach wd [split [string trim $txt]] {
    regexp {^([+-])?(.*)} $wd v1 sig data
    if {![catch {set x $INDEXNULLS($data)}]} {continue}
    lappend WTAB(I$sig) $data
    }
return [array get WTAB]
}


proc getntab {} {
return I[incr ::TCTR]
}

proc inittctr {} { set ::TCTR -1 }


#
#   Procedures for generating html output to browser
#

proc genoutput {opfmt} {

genoutput.$opfmt
}

proc genoutput.sql {} {
global RESULTS
puththdr
puts "
<head><title>CISP Search SQL</title>
</head>
<body>
<h1>SQL Output</h1>
<h2>Search SQL:</h2>
<pre>
$RESULTS(sql)
</pre>
"
if {[info exist RESULTS(exsql)]} {
  puts "
<p>
<h2>Exclusion wordlist SQL</h2>
<pre>
$RESULTS(exsql)
</pre>"
  }
puts "</body>"
}

proc genoutput.table {} {
global RESULTS EXCLUDE HREFFORMAT ar
  array set HREFFORMAT {
    SITE "site/%s.html"
    STONE "stone/%s_%s.html"
    INSCRIP "stone/%s_%s.html#i%s"
  }
  puththdr
  opendb
  catch {unset EXCLUDE}
  catch {db eval exclist $RESULTS(exsql)}
  set RESULTS(list) {}
  foreach res [db $RESULTS(sql)] {
   set key [eval mkkey $res]
   if {[info exist EXCLUDE($key)]} {continue}
    lappend RESULTS(list) $res
    }
  mkmaplist $ar(selmap)
  db disconnect
  ht_Copy $::lib/searchres.thtml
}

proc exclist args {
global EXCLUDE
set EXCLUDE([eval mkkey $args]) 1
}

proc mkkey args {
global RESULTS
return [join [lrange $args 0 $RESULTS(keynum)] "/"]
}

proc mkhref { args } {
global HREFFORMAT RESULTS
return [string tolower [eval format $HREFFORMAT($RESULTS(TARGET)) $args]]
}

proc RES_results_o {} {
global RESULTS EXCLUDE
set hdrs ""
catch {set hdrs "<th>[join $RESULTS(COLHDRS) {</th><th>}]</th>"}
putht "<tr><th>Key</th>$hdrs"
if {[info exist RESULTS(map)]} {
  writemap
  }
  
set okey ""
set cols [llength $RESULTS(OPCOLS)]
foreach res [db $RESULTS(sql)] {
  set key [eval mkkey $res]
  if {[info exist EXCLUDE($key)]} {continue}
  if {$okey == ""} {set okey $key}
  if {$okey != $key} {
    set rt {}
    for {set i 0} {$i < $cols} {incr i} {
      lappend rt [join $col($i) {<br>}]
      }
    putht "
<tr><td><a href=\"$href\">$okey</a><td>[join $rt {</td><td>}]</td>"
    catch {unset col}
    set okey $key
    }
  set href [eval mkhref $res]
  set n -1
  set opind $RESULTS(keynum)
  incr opind
  foreach colspec $RESULTS(OPCOLS) {
    lappend col([incr n]) [eval format \"[lindex $colspec 1]\" [lrange $res $opind end]]
    incr opind [lindex $colspec 0]
    }
  }
set rt {}
for {set i 0} {$i < $cols} {incr i} {
  lappend rt [join $col($i) {<br>}]
  }
putht "
<tr><td><a href=\"$href\">$key</a><td>[join $rt {</td><td>}]</td>"
return ""
}

proc RES_map {} {
global RESULTS
if {[info exist RESULTS(map)]} {
  writemap
  }
}


proc RES_results {} {
global RESULTS EXCLUDE SITEREF TILELIST
set hdrs ""
catch {set hdrs "<th>[join $RESULTS(COLHDRS) {</th><th>}]</th>"}
putht "<td><h1>All Results</h1>
<table border=2 cellpadding=4 bgcolor=linen>
<tr><th>Key</th>$hdrs"
set okey ""
set cols [llength $RESULTS(OPCOLS)]
foreach res $RESULTS(list) {
  set key [eval mkkey $res]
  if {$okey == $key} {continue}
  set okey $key
  set href [eval mkhref $res]
  set opind $RESULTS(keynum)
  incr opind
  set mref ""
  if {[info exist SITEREF([lindex $res 0])]} {
    set mref "[nbsp 2]<a href=\"\" onClick=\"showonmap('[lindex $res 0]');return false;\"><img src=icons/pin.gif  alt=\"Show on map\" border=0></a>"
    }
  set row {}
  foreach colspec $RESULTS(OPCOLS) {
    lappend  row [eval format \"[lindex $colspec 1]\" [lrange $res $opind end]]
    incr opind [lindex $colspec 0]
    }
  putht "
<tr><td><a name=$key href=\"$href\" target=text_display>$key</a>$mref</td><td>[join $row {</td><td>}]</td>"
  }
putht "</table></td>"

if {[info exist RESULTS(map)]} {
  putht "<td valign=top>
<h1>Clustered Sites</h1>
<table border=2 cellpadding=4 bgcolor=linen>
<tr><th>Key</th><th>Site</th>"
  foreach {key slist} [array get TILELIST] {
   if {[set N [llength $slist]] == 1} {continue}
   putht "<tr><th colspan=2><a name=\"$key\">$N hits near [lindex [lindex $slist 0] 2]</a></th>"
   foreach sr $slist {
     putht "<tr><td><a href=# onclick=\"jumpTo('[lindex $sr 1]');return false;\">[lindex $sr 1]</a></td><td>[lindex $sr 2]</td>"
     }
  }
  putht "</table></td>"
  
 }
return ""
}



#
### Procedures for dealing with maps
#

proc mkmaplist {bestmap} {
global RESULTS  ALLMAPS   SITEREF  TILELIST TILESHAPE
if {$bestmap == "NOMAP"} {return}
catch {unset SITEHITS}
catch {unset TILELIST}
foreach res $RESULTS(list) {
  if {[catch {incr SITEHITS([lindex $res 0])}]  } {set SITEHITS([lindex $res 0]) 1}
  }
set siteselect '[join [array names SITEHITS] ',']'
set sql "select site,system,east,north from gridref where site in ($siteselect)"
set grlist [db $sql]

if {$bestmap  == "BEST"} {
   set bestmap [getbestmap $grlist]
   }
set RESULTS(map) $bestmap
array set map $ALLMAPS($bestmap)
foreach mapping $map(mappings) {
  array set m $mapping
  lappend sysmap($m(system)) [concat $m(bl) $m(tr)] $m(matrix)
  }
foreach siteref $grlist {
 foreach {site sys e n} $siteref {
   if {![info exist sysmap($sys)]} {continue}
   foreach {bnds mat} $sysmap($sys) {
     if {[isin $e $n $bnds]} {
       set SITEREF($site) [w2m $e $n $mat]
       break
       }
    }
  }
 
 }
symscale
set nmi $RESULTS(keynum)
incr nmi
foreach res $RESULTS(list) {
  set site [lindex $res 0]
  if {[catch {set xy $SITEREF($site)}]} {continue}
  set tind [tileindex $xy]
  lappend TILELIST($tind) [list $site [eval mkkey $res] [lindex $res $nmi]]
  if {![info exist tshape($tind)]} {set tshape($tind) [getshape $res]}
  }
  foreach {tind lst} [array get TILELIST] {
    set ni [llength $lst]
    set size 1
    foreach b {1 5 20} {
     if {$ni <= $b} {break}
     incr size
    }
    set TILESHAPE($tind) [join [lreplace $tshape($tind) 1 1 $size] ,]
  } 
}


proc getbestmap grlist {
global ALLMAPS MAPORDER BOUNDS
set defltmap bigmap
if {[llength $grlist] == 0} {return $defltmap}
foreach sys {GB IR FR CH} {
  foreach {mm v} {min 9999999 max -9999999 } {
    set bar($sys.$mm.x) $v
    set bar($sys.$mm.y) $v
    }
  }
foreach gref $grlist {
  foreach {site sys e n} $gref {
    set allsys($sys) 1
    set bar($sys.min.x) [min $e $bar($sys.min.x)]
    set bar($sys.min.y) [min $n $bar($sys.min.y)]
    set bar($sys.max.x) [max $e $bar($sys.max.x)]
    set bar($sys.max.y) [max $n $bar($sys.max.y)]
    }
  }
mkbestmapindex

set syss [array names allsys]
set okmaps $MAPORDER([lindex $syss 0])
foreach sys  $syss {
  set newokmaps {}
  foreach map $okmaps {
    if {[catch {set bnl $BOUNDS($sys.$map)}]} {continue}
    foreach bn $bnl {
     if { ($bar($sys.min.x) >= [lindex $bn 0]) &&
          ($bar($sys.min.y) >= [lindex $bn 1]) &&
          ($bar($sys.max.x) <= [lindex $bn 2]) &&
          ($bar($sys.max.y) <= [lindex $bn 3]) } {
       lappend newokmaps $map
       break
       }
     }
    }
  set okmaps $newokmaps
  }
 if {$okmaps == {}} {return $defltmap}
 return [lindex $okmaps 0]
}

proc symscale {} {
 global RESULTS ar MENUTYPE SYMCTRL
 catch {unset SYMCTRL}
 set rbase $RESULTS(keynum)
 incr rbase
 foreach {i si} {0 1 2 2} {
   set sm $ar(symcat_$si)
   if {$sm == 0} {
     set SYMCTRL($i) 0
     continue
     }
   set SYMCTRL(iskey) 1
   set type $MENUTYPE($sm)
   set header [lindex [mitem $sm] 2]
   set offset $::OPCOLSTASH($header)
   incr offset $rbase
   set scale [symscale.$type $offset]
   set SYMCTRL($i.type) $type
   set SYMCTRL($i.offset) $offset
   set SYMCTRL($i.scale) $scale
   set SYMCTRL($i.header) $header
  }
}

proc symscale.R off {
global RESULTS
foreach r $RESULTS(list) {
  set v [lindex $r $off]
  if {[catch {set min [min $v $min]}]} {set min $v}
  if {[catch {set max [max $v $max]}]} {set max $v}
  }
set interval [expr ($max - $min) / 5]
return [list $min $max $interval]
}

proc symscale.S off {
global RESULTS
foreach r $RESULTS(list) {
  set v [lindex $r $off]
  if {[catch {incr ary($v)}]} {set ary($v) 1}
  }
foreach {key n} [array get ary] {lappend kl [list $n $key]}
set kl [lsort -integer -index 0 -decreasing $kl]
if {[llength $kl] <= 5} {
  set n -1
  foreach item $kl {set rar([lindex $item 1]) [incr n]}
  } else {
  for {set n 0} {$n < 4} {incr n} {set rar([lindex [lindex $kl $n] 1]) $n}
  set rar(Other) 4
  }
 return [array get rar]
}

proc symscale.N off { return [symscale.S $off] }

set SYMDFLT {0 1 1 2 2 1}

proc mkshape {ind val} {
 array set def $::SYMDFLT
 set def($ind) $val
 foreach {nm v} [array get def] {lappend res $v}
 return [join $res ,]
} 
 
proc symkey.S ind {
global SYMCTRL
foreach {nm v} $SYMCTRL($ind.scale) {set scale($v) $nm}
set res ""
for {set i 0} {$i < 5} {incr i} {
 catch { set res "$res\nitem shape=[mkshape $ind $i] text='$scale($i)'" }
 }
 return $res
}

proc symkey.N ind {return [symkey.S $ind]}

proc symkey.R ind {
global SYMCTRL
set scale $SYMCTRL($ind.scale)
set res ""
set low [lindex $scale 0]
set inter [lindex $scale 2]
for {set i 0} {$i < 5} {incr i} {
  set next [expr $low + $inter]
  set txt "$low - $next"
  set low $next
  set res "$res
item shape=[mkshape $ind $i] text='$txt'"
  }
  return $res
}
  
 
proc symkey {} {
global SYMCTRL
if {![info exist SYMCTRL(iskey)]} {return ""}
set res "<PARAM NAME=key VALUE=\"
header text='Item Count'"
set n -1
foreach txt {"1 item" "2 - 5 items" "6 - 10 items" "11 - 20 items" "> 20 items"} {
  set res "$res
item shape=[mkshape 1 [incr n]] text='$txt'"
  }

foreach i { 0 2 } {
  if {[catch {set ty $SYMCTRL($i.type)}]} {continue}
  set res "$res
header text=|$SYMCTRL($i.header)|
[symkey.$ty $i]"
  }
 return "$res
\">"
}


  
proc writemap {} {
global TILELIST SITEREF RESULTS ALLMAPS TILESHAPE
putht [imapapplettag $ALLMAPS($RESULTS(map)) maps/]
putht "<PARAM NAME=areas VALUE=\""
foreach {tile vlist} [array get TILELIST] {
   set s0 [lindex $vlist 0]
   catch {unset si}
   foreach s $vlist {set si([lindex $s 0]) 1}
   set tags [join [array names si] ,]
   set shape $TILESHAPE($tile)
   if {[set N [llength $vlist]] > 1} {
     set coords [tile2coords $tile]
     set alt "$N hits near [lindex $s0 2]"
     set oncl $tile
    } else {
     set coords [join $SITEREF([lindex $s0 0]) ,]
     set alt [lindex $s0 2]
     set oncl [lindex $s0 1]
    }
   putht "area coords=$coords alt=|$alt|
   onclick=|jumpTo('$oncl')|
   shape=$shape id=$tags
   "
  }
putht "\">
[symkey]
"

imapappletend
}

proc getshape r1 {
  global SYMCTRL
  array set shape $::SYMDFLT
  foreach i {0 2} {
    if {[catch {set ty $SYMCTRL($i.type)}]} {continue}
    set shape($i) [symresolve.$ty $i $r1]
    }
  foreach {nm v} [array get shape] {lappend res $v}
  return $res
}
  
proc symresolve.S { ind  res } {
global SYMCTRL
set val [lindex $res $SYMCTRL($ind.offset)]
array set sca $SYMCTRL($ind.scale)
if {[catch {set r $sca($val)}]} {set r $sca(Other)}
return $r
}

proc symresolve.N {ind res} {return [symresolve.R $ind $res]}

proc symresolve.R { ind res } {
global SYMCTRL
set val [lindex $res $SYMCTRL($ind.offset)]
set sca $SYMCTRL($ind.scale)
set st [lindex $sca 0]
set inc [lindex $sca 2]
set n -1
while {$val >= $st} {
  incr n
  set st [expr $st + $inc]
  }
 return [min 4 $n]
}


main
#showvars


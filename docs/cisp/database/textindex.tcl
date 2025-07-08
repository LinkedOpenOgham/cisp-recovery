


proc txindex {} {
set wh "where site = 'ADARN'"
set wh ""
foreach n {IND IND1 INDC} {
   global $n
   catch {unset $n}
   }
global OLDINS
set OLDINS {}
gaugest [db1 "select count(*) from translat"]
db eval txindex_1 "select site, stone, inscription, reading, expand_id from translat $wh
			order by site, stone, inscription"
checkold flush

mkindfile
}

proc txindex_1 {site stone ins rd ex} {
global IND1 OLDINS
checkold [list $site $stone $ins]
set txt [db1 "select expansion from translat where site = '$site' and 
	stone = $stone and inscription = $ins and reading = $rd and expand_id = $ex"]
#puts $txt
regsub -all {(PN)} [string toupper $txt] "" txt
regsub -all {[^[:alpha:] ]} $txt "" txt
regsub -all { +} $txt " " txt
#puts >>$txt<<
#update
foreach wd [split $txt] {set IND1($wd) $OLDINS}
gaugeup
}

proc checkold key {
global OLDINS IND IND1 INDC
if {$OLDINS == $key} {return}
foreach {wd dum} [array get IND1] {
  lappend IND($wd) $OLDINS
  if {[catch {incr INDC($wd)}]} {set INDC($wd) 1}
  }
catch {unset IND1}
puts ">>> $OLDINS"
update
set OLDINS $key
}

proc mkwordindex {} {
global IND
db "delete from wordindex"
catch {unset IND()}
foreach {wd ilist} [array get IND] {
  foreach l $ilist {
    set sql "insert into wordindex values ('$wd','[join $l ',']')"
    puts $sql
    db $sql
    update
  }
}

}  

proc mkindfile {} {
global IND PA
set f [open $PA(search)/wordindex.tcl w]
puts $f "array set WINDEX {[array get IND]}"
close $f

}

proc findins txt {
global WINDEX
regsub -all { +} [string trim [string toupper $txt]] " " txt
set sl [split $txt]

foreach s $sl {
  set r {}
  puts [array names WINDEX $s]
  foreach {key ilist} [array get WINDEX $s] {set r [concat $r $ilist]}
  set r [lrmdups $r]
  if {[catch {intersect $res $r} res]} {set res $r}
  }
return $res
}


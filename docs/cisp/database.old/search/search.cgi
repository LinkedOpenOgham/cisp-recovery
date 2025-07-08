#!/usr/local/rbin/tcl8

lappend auto_path /home/booking/tcllib8

package require cgi

cgi_input 

source wordindex.tcl

proc main {} {
global _cgi_uservar AUX

cgi_eval {
  cgi_head {
  cgi_title "Search Results"
  puts {<base href="/archaeology/cisp/database/">
<link rel=stylesheet type="text/css" href="style.css">}
  }
  cgi_body {
    set rlist [findins $_cgi_uservar(search)]
    puts "
<center><h1>Search Results</h1></center>
Matching:
<tt>[string toupper $_cgi_uservar(search)]</tt> - <b>[llength $rlist]</b> matches."
   if {[llength $rlist] > 0} {
    puts "<ul><table border=0>"
    foreach tup $rlist {
      foreach {site stone ins} $tup {
      puts "<tr><td><a href=stone/[string tolower $site]_$stone.html#i$ins target=text_display>$site/$stone/$ins</a>
      <td><tt>[join $AUX($tup) { , }]</tt>"
      }
    }
   puts "</table></ul>"
   }
  }
}
}
  
proc findins txt {
global WINDEX AUX
catch {unset AUX}
regsub -all { +} [string trim [string toupper $txt]] " " txt
set sl [split $txt]

foreach s $sl {
  set r {}
#  puts [array names WINDEX $s]
  foreach {key ilist} [array get WINDEX $s] {
    set r [concat $r $ilist]
    foreach ins $ilist {set mat($ins) $key}
    }
  set r [lrmdups $r]
  if {[catch {intersect $res $r} res]} {set res $r}
  foreach ins $res {lappend AUX($ins) $mat($ins)}
  catch {unset mat}
  }
if {[catch {set res}]} {set res {}}
return $res

}

main

#!/usr/local/rbin/tcl8

source setlib.tcl

source $lib/http-query-setup.tcl
source $lib/setup.tcl
source $lib/indexctrl.tcl
source $lib/mapdata.tcl

http_proc_cgi_args

proc adjscparms {} {
global ar SCPARMS

foreach {k val} [array get SCPARMS] {
  if {[regexp {^[0-9]+$} $ar($k)]} {set SCPARMS($k) $ar($k)}
  }
}

proc genform {} {

puththdr

source $::lib/selectprocs.tcl
ht_Copy $::lib/select.thtml
}

genform
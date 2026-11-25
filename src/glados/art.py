"""Aperture/GLaDOS ASCII mark matching the user-provided reference image."""

IDLE = "\n".join((
    "       #+ @      # #              M#@",
    " .    .X  X.%##@;# #   +@#######X. @H%",
    "   ,==.   ,######M+  -#####%M####M-    #",
    "  :H##M%:=##+ .M##M,;#####/+#######% ,M#",
    " .M########=  =@#@.=#####M=M#######=  X#",
    " :@@MMM##M.  -##M.,#######M#######. =  M",
    "             @##..###:.    .H####. @@ X,",
    "   ############: ###,/####;  /##= @#. M",
    "           ,M## ;##,@#M;/M#M  @# X#% X#",
    ".%=   ######M## ##.M#:   ./#M ,M #M ,#$",
    "##/         $## #+;#: #### ;#/ M M- @# :",
    "#+ #M@MM###M-;M #:$#-##$H# .#X @ + $#. #",
    "      ######/.: #%=# M#:MM./#.-#  @#: H#",
    "+,.=   @###: /@ %#,@  ##@X #,-#@.##% .@#",
    "#####+;/##/ @##  @#,+       /#M    . X,",
    "   ;###M#@ M###H .#M-     ,##M  ;@@; ###",
    "   .M#M##H ;####X ,@#######M/ -M###$  -H",
    "    .M###%  X####H  .@@MM@;  ;@#M@",
    "      H#M    /@####/      ,++.  / ==-,",
    "               ,=/:, .+X@MMH@#H  #####$=",
))
# Keep the reference logo intact in each state; the UI animates its subtitle and
# emphasis instead of morphing the supplied ASCII artwork.
TALKING = IDLE
ANNOYED = IDLE
FRAMES = (IDLE, TALKING, ANNOYED)

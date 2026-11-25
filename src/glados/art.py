"""Aperture/GLaDOS ASCII mark matching the user-provided reference image."""

IDLE = "\n".join((
    "              .,-:;//;:=,",
    "          . :H@@@MM@M#H/.,+%;,",
    "        ,/X+ +M@@M@MM%=,-%HMMM@X/,",
    "     -+@MM; $M@@MH+-,;XMMMM@MMMM@+-",
    "    ;@M@@M- XM@X;. -+XXXXXHHH@M@M#@/.",
    "  ,%MM@@MH ,@%=             .---=-=:=,.",
    "  =@#@@@MX .,               -%HX$$$%%+;",
    " =-./@M@M$                   .;@MMMM@MM:",
    " X@/ -$MM/                     .+MM@@@M$",
    ",@M@H: :@:                     . =X#@@@@-",
    ",@@@MMX, .                     /H- ;@M@M=",
    ".H@@@@M@+,                     %MM+..%#$.",
    " /MMMM@MMH/.                   XM@MH; =;",
    "  /%+%$XHH@$=               , .H@@@@MX,",
    "   .=--------.            -%H.,@@@@@MX,",
    "   .%MM@@@HHHXX$$$%+- .:$MMX =M@@MM%.",
    "     =XMMM@MM@MM#H;,-+HMM@M+ /MMMX=",
    "       =%@M@M#@$-.=$@MM@@@M; %M%=",
    "         ,:+$+-,/H#MMMMMMM@= =,",
    "               =++%%%%+/:-",
))

# Keep the reference logo intact in each state; the UI animates its subtitle and
# emphasis instead of morphing the supplied ASCII artwork.
TALKING = IDLE
ANNOYED = IDLE
FRAMES = (IDLE, TALKING, ANNOYED)

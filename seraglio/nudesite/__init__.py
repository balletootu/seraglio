from .nudesite import NudeSite

from .metart import MetArt
from .sexart import SexArt
from .metartx import MetArtX
from .thelifeerotic import TheLifeErotic
from .vivthomas import VivThomas
from .errotica_archives import ErroticaArchives
from .domai import Domai
from .goddessnudes import GoddessNudes
from .eroticbeauty import EroticBeauty

from .rylskyart import RylskyArt
from .stunning18 import Stunning18
from .eternaldesire import EternalDesire

from .mplstudios import MPLStudios


metart = MetArt()
sexart = SexArt()
metartx = MetArtX()
thelifeerotic = TheLifeErotic()
vivthomas = VivThomas()
errotica_archives = ErroticaArchives()
domai = Domai()
goddessnudes = GoddessNudes()
eroticbeauty = EroticBeauty()
rylskyart = RylskyArt()
stunning18 = Stunning18()
eternaldesire = EternalDesire()
mplstudios = MPLStudios()

site_dict = {
    'metart': metart,
    'sexart': sexart,
    'metartx': metartx,
    'thelifeerotic': thelifeerotic,
    'vivthomas': vivthomas,
    'errotica-archives': errotica_archives,
    'domai': domai,
    'goddessnudes': goddessnudes,
    'eroticbeauty': eroticbeauty,
    'rylskyart': rylskyart,
    'stunning18': stunning18,
    'eternaldesire': eternaldesire,
    'mplstudios': mplstudios,
}
sites = site_dict.values()


def get_site(site_name):
    return site_dict[site_name]

import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )
from ..models.mymodel import (
    DBSession)
from ..models import (mymodel)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session_factory = get_session_factory(engine)
    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        c = mymodel.Country (name = "Россия")
        r = mymodel.Region (name = "Свердловская область",country = c, country_id = 1)
        ci =  mymodel.City (name = "Екатеринбург",region = r, region_id = 1)
        ci1 =  mymodel.City (name = "Первоуральск",region = r, region_id = 1)
        ci2 =  mymodel.City (name = "Ревда",region = r, region_id = 1)
        dbsession.add(c)
        dbsession.add(r)
        dbsession.add(ci1)
        dbsession.add(ci)

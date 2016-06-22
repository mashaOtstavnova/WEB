import os

from pyramid.view import (view_config)
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.security import remember, authenticated_userid, forget
from datetime import datetime

from ..models.mymodel import (
    DBSession,
    User,Advert,History,Country,Region,City,
    login,
    register,)


@view_config(route_name='oneAdvert', renderer='/templates/oneAdvert.jinja2')
def oneAdvert_view(request):
    session = DBSession()
    thisUser = False
    history_id = request.matchdict['history_id']
    history = session.query(History).filter(History.id == history_id).first()
    patch = history.patchImageAvatar
    login = False
    thisUserIs = get_current_user(request)
    if thisUserIs:
        login = True
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        if history.user.id == thisUserIs.id:
            thisUser = True

    return {
        'thisUser':thisUser,
        'login': login,
        'advert':history.advert,
        'history':history,
        'About': u'Создать удобный для вас удобный и простой сервис.'
                 u'С помощью данного сервиса у вас появиться возможность хранить все данные в одном месте, '
                 u'а так же очень просто рассчитывать свои расходы. ',

    }

def auth_required(func):
    def wrapper(request):
        owner = authenticated_userid(request)
        if owner is None:
            raise HTTPForbidden()
        return func(request)

    return wrapper


def get_current_user(request):
    try:
        id_ = authenticated_userid(request)
        session = DBSession()
        print(id_)
        return session.query(User).get(id_)
    except Exception as e:
        print("ERR:" + str(e))
        return None

def search1(text,history):
    session = DBSession()
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print(text)
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!history')
    print(type(history))
    result = []
    for hi in history:
        textAdver = hi.advert.text.lower()
        nameAdvert = hi.advert.name.lower()
        if(text.lower() in textAdver) or (text.lower() in nameAdvert):
            result.append(hi)
    return result

@view_config(route_name='home', renderer='/templates/home.jinja2')
def my_view(request):
    session = DBSession()
    search = request.params
    history = session.query(History).all()
    msg = "По дате (сначала старые)"
    if(len(search)!=0):
       for i in search:
        if (i=='q'):
             text = search['q']
             history = search1(text,history)
        if (i == 's'):
            sort = search['s']
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(sort)
            print(sort == '1')
            if (sort == '1'):
                history = sorted(history, key=lambda hi: hi.advert.cost)
                msg = "По цене (возрастание)"
            if (sort == '2'):
                msg = "По цене (убывание)"
                history = sorted(history, key=lambda hi: hi.advert.cost)
                history = history[::-1]
            if (sort == '3'):
                msg = "По дате (сначала старые)"
                history = sorted(history, key=lambda hi: hi.advert.date)
            if (sort == '4'):
                msg = "По дате (сначала новые)"
                history = sorted(history, key=lambda hi: hi.advert.date)
                history = history[::-1]
    if get_current_user(request):
        return {'login': True,'msg':msg,'history':history}
    else:
        return {'login': False,'msg':msg,'history':history}



@view_config(route_name='uslugi', renderer='/templates/uslugi.jinja2')
def uslugi_view(request):
    session = DBSession()
    history = session.query(History).all()
    if get_current_user(request):
        return {'login': True,'history':history}
    else:
        return {'login': False,'history':history}


@view_config(route_name='user', renderer='templates/user.jinja2')
@auth_required
def user_view(request):
    session = DBSession()
    nxt = request.route_url('user')
    user = get_current_user(request)
    history = session.query(History).filter(History.user_id == get_current_user(request).id)
    search = request.params
    msg = "По дате (сначала старые)"
    if(len(search)!=0):
       for i in search:
        if (i=='q'):
             text = search['q']
             history = search1(text,history)
        if (i == 's'):
            sort = search['s']
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(sort)
            print(sort == '1')
            if (sort == '1'):
                history = sorted(history, key=lambda hi: hi.advert.cost)
                msg = "По цене (возрастание)"
            if (sort == '2'):
                msg = "По цене (убывание)"
                history = sorted(history, key=lambda hi: hi.advert.cost)
                history = history[::-1]
            if (sort == '3'):
                msg = "По дате (сначала старые)"
                history = sorted(history)
            if (sort == '4'):
                msg = "По дате (сначала новые)"
                history = sorted(history, key=lambda hi: hi.advert.date)
                history = history[::-1]
    advert = session.query(Advert).all()
    return {
        'msg':msg,
        'user':user,
        'advert': advert,
        'history': history,
        'next': nxt,
        'login': True
    }

@view_config(route_name='about', renderer='templates/about.jinja2')
def about_view(request):
    login = False
    if get_current_user(request):
        login = True
    return {
        'login': login,
        'About': u'Создать удобный  и простой для вас сервис.'
                 u'На котором каждый может предложить или найти услугу. '
                 u'Мы очень рады что Вы посетели наш сайт! ',

    }

@view_config(route_name='delete', renderer='templates/delete.jinja2')
def delete_view(request):
    session = DBSession()
    login = False
    history_id = request.matchdict['id']
    history = session.query(History).filter(History.id == history_id).first()
    print(str(history.advert.text))
    session.delete(history.advert)
    session.delete(history)
    session.commit()
    if get_current_user(request):
        login = True
    return {
        'login': login,
        'About': 'deleteMsg'

    }

@view_config(route_name='login', renderer='templates/login.jinja2')
def login_view(request):
    nxt = request.route_url('user')
    did_fail = False
    if 'email' in request.POST:
        # LOGIN PROCESSING
        user = login(request.POST["email"], request.POST["password"])
        if user:
            headers = remember(request, user.id)
            return HTTPFound(location=nxt, headers=headers)
        else:
            did_fail = True
    return {
        'login': "",
        'next': nxt,
        'failed_attempt': did_fail,
    }


@view_config(route_name='logout')
def logout_view(request):
    headers = forget(request)
    loc = request.route_url('home')
    return HTTPFound(location=loc, headers=headers)

def write_some_porn(image):
    file_path = os.path.join('myserviceboard\static\images', (image.filename))
    print(image)
    open(file_path , 'wb').write(image.file.read())
    return file_path




@view_config(route_name='advert', renderer='templates/advert.jinja2')
def advert_view(request):
    session = DBSession()
    nxt = request.route_url('user')
    user = get_current_user(request)
    cities = session.query(City).all()
    if 'text' and 'name' and 'cost'  in request.POST:
        if request.POST['text'] != '' and request.POST['name'] != '' and request.POST['cost'] != '':

            try:
                    input_file = request.POST['img']
                    name = input_file.filename
                    write_some_porn(input_file)
            except:
                    name = 'notPhoto.jpg'
            file_path = os.path.join('\static\images', (name))
            try:
                cost = float(request.POST['cost'])
            except:
                cost = 0
            advert = Advert (name = request.POST['name'],
                             text = request.POST['text'],
                             cost =  cost,
                             date = datetime.today()
                             )
            session.add(advert)
            history = History(user_id = user.id,
                              user = user,
                              advert = advert,
                              advert_id = advert.id,
                              patchImageAvatar = file_path
                              )
            session.add(history)
            # pict = ProfilePic(user_id = user.id,
            #                   user = user,name =name)
            # session.add(pict)
            session.commit()
            return HTTPFound(location=nxt)
        else:
            return {
                    'login': True,
                    'cities': cities,
                    'error': True
            }
    return {
        'login': True,
        'cities': cities,
    }

@view_config(route_name='registration', renderer='templates/registration.jinja2')
def registration_view(request):
    session = DBSession()
    nxt = request.params.get('next') or request.route_url('home')
    did_fail = False
    cities = session.query(City).all()
    countries = session.query(Country).all()
    regions = session.query(Region).all()

    if 'email' and 'name' and 'city'and 'password'and 'phone'in request.POST:
        city =  session.query(City).filter(City.id == request.POST["city"]).first()
        user = register(
            request.POST["name"], request.POST["email"],
            request.POST["password"], request.POST["phone"], city
        )
        print(user)
        print(nxt)
        if user:
            headers = remember(request, user.id)
            return HTTPFound(location=nxt, headers=headers)
        else:
            did_fail = True
    return {
        'login': "",
        'next': nxt,
        'failed_attempt': did_fail,
        'cities': cities,
    }


db_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_MyServiceBoard_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

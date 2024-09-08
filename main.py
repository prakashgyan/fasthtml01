from fasthtml.common import *
from hmac import compare_digest
# app,rt = fast_app()

db = database("data/usingage.db")

signage, users = db.t.sinage, db.t.users

if users not in db.t:
    users.create(
        dict(
            name = str,
            email = str, 
            passwd = str,
            id = int 
        ),
        pk = 'id'
    )
    signage.create(
        dict(
            signageid = int,
            signagename = str,
            metadata = dict,
            content = dict
        ),
        pk = 'singageid'
    )

Users, Signage = users.dataclass(), signage.dataclass()

login_redir = RedirectResponse('/login', status_code=303) 
singup_redir = RedirectResponse('/signup', status_code=303)

def before(req, sess):
    auth = req.scope['auth'] = sess.get('auth', None)
    if not auth: return login_redir

    signage.xtra(singageid=auth)   

markdown_js = """
import { marked } from "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js";
import { proc_htmx} from "https://cdn.jsdelivr.net/gh/answerdotai/fasthtml-js/fasthtml.js";
proc_htmx('.markdown', e => e.innerHTML = marked.parse(e.textContent));
"""


def _not_found(req, exc): return Titled('Oh Snap!', Div('This page does not exist yet!'))

bware = Beforeware(before, skip=[r'/favicon.ico', r'/static/.*', r'.*\.css', '/login'])

app = FastHTML(
        before=before,
        exception_handlers={404: _not_found},
        hdrs=(
            picolink,
            Style(':root { --pico-font-size: 100%; }'),
            SortableJS('.sortable'),
            Script(markdown_js, type='module')
        )      
    )

rt = app.route

@rt("/login")
def get():
    frm = Form(
        Input(id='email', placeholder='Email'),
        Input(id='pwd', placeholder='********', type= 'password'),
        Button('Login'), 
        action = '/login',
        method = 'post'
    )
    return Titled("Login", frm)


@dataclass
class Login: email:str; pwd:str


@rt("/login")
def post(login:Login, sess):
    if not login.email and login.pwd: return login_redir

    try: u = users[login.email]

    except NotFoundError: return singup_redir

    if not compare_digest(u.pwd.encode('utf-8'), login.pwd.encode('utf-8')): return login_redir

    sess['auth'] = u.email

    return RedirectResponse('/', status_code=303)

@app.get('/logout')
def logout(sess):
    del sess['auth']
    return login_redir


@patch
def __ft__(self:Signage):
    



serve()
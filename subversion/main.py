#!/usr/bin/env python

import ansible.runner
import bcrypt
import concurrent.futures
import logging
import MySQLdb
import os.path
import re
import socket
import subprocess
import torndb
import tornado.escape
from tornado import gen
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import unicodedata

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)
define("mysql_host", default="db01", help="database host")
define("mysql_database", default="subversion", help="database name")
define("mysql_user", default="subversion", help="database user")
define("mysql_password", default="subversion", help="database password")
define("remote_user", default='www')
define("admin_role", default='admin')


# A thread pool to be used for password hashing with bcrypt.
executor = concurrent.futures.ThreadPoolExecutor(2)


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/compose", ComposeHandler),
            (r"/delete/([^/]+)", DeleteHandler),
            (r"/update/([^/]+)", UpdateHandler),
            (r"/auth/create", AuthCreateHandler),
            (r"/auth/login", AuthLoginHandler),
            (r"/auth/logout", AuthLogoutHandler),
        ]
        settings = dict(
            site_title=u"Tornado subversion",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            ui_modules={"Entry": EntryModule},
            xsrf_cookies=True,
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            login_url="/auth/login",
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)

        self.db = torndb.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)

        self.maybe_create_tables()

    def maybe_create_tables(self):
        try:
            self.db.get("SELECT COUNT(*) from entries;")
        except MySQLdb.ProgrammingError:
            subprocess.check_call(['mysql',
                                   '--host=' + options.mysql_host,
                                   '--database=' + options.mysql_database,
                                   '--user=' + options.mysql_user,
                                   '--password=' + options.mysql_password],
                                  stdin=open('schema.sql'))


class BaseHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        user_id = self.get_secure_cookie("demo_user")
        if not user_id:
            return None
        return self.db.get("SELECT * FROM authors WHERE id = %s", int(user_id))

    def any_author_exists(self):
        return bool(self.db.get("SELECT * FROM authors LIMIT 1"))

    def check_author_exists(self):
        return bool(self.db.get("SELECT * FROM authors WHERE email = %s",
                                self.get_argument("email")))

    # def on_finish(self):
    #     self.db.close()


class HomeHandler(BaseHandler):

    def get(self):
        entries = self.db.query("SELECT * FROM entries ORDER BY published ")
        if not entries:
            self.redirect("/compose")
            return
        self.render("home.html", entries=entries)


class ComposeHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        id = self.get_argument("id", None)
        entry = error = None
        if id:
            entry = self.db.get("SELECT * FROM entries WHERE id = %s", int(id))
        self.render("compose.html", entry=entry, error=error)

    @tornado.web.authenticated
    def post(self):
        id = self.get_argument("id", None)
        title = self.get_argument("title")
        repo = self.get_argument("repo")
        username = self.get_argument("username")
        password = self.get_argument("password")
        host = self.get_argument("host")
        dest = self.get_argument("dest")
        revision = self.get_argument("revision", None)

        # try:
        #     socket.gethostbyname(host)
        # except:
        #     self.render("compose.html", entry=None, error="hostname not known")
        #     return

        conv = lambda x, y: x + os.path.sep + \
            y if x.endswith(os.path.sep) or not re.findall(y, x) else x

        if id:
            entry = self.db.get("SELECT * FROM entries WHERE id = %s", int(id))
            if not entry:
                raise tornado.web.HTTPError(404)
            slug = entry.slug
            dest = conv(dest, slug)
            self.db.execute(
                "UPDATE entries SET title = %s, repo = %s, username = %s, password=%s, host=%s, dest=%s, revision=%s "
                "WHERE id = %s", title, repo, username, password, host, dest, revision, int(id))
        else:
            slug = unicodedata.normalize("NFKD", title).encode(
                "ascii", "ignore")
            slug = re.sub(r"[^\w]+", " ", slug)
            slug = "-".join(slug.lower().strip().split())
            if not slug:
                slug = "entry"
            while True:
                e = self.db.get("SELECT * FROM entries WHERE slug = %s", slug)
                if not e:
                    break
                slug += "-2"
            dest = dest = conv(dest, slug)
            self.db.execute(
                "INSERT INTO entries (author_id,title,slug,repo,username,password,host,dest,revision,"
                "published) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,UTC_TIMESTAMP())",
                self.current_user.id, title, slug, repo, username, password, host, dest, revision)
        logging.info("%s update %s", self.current_user.name, slug)
        self.redirect("/")


class DeleteHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, slug):
        self.db.execute("DELETE FROM entries where slug = %s", slug)
        self.redirect("/")


def checkout(host, repo, user, passwd, dest):
    runner = ansible.runner.Runner(
        module_name='subversion',
        module_args='repo={0} dest={1} username={2} password={3}'.format(
            repo, dest, user, passwd),
        pattern=host,
        forks=10,
        remote_user=options.remote_user
    )
    datastructure = runner.run()
    return datastructure


class UpdateHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, slug):
        entry = self.db.get("SELECT * FROM entries WHERE slug = %s", slug)
        error = None
        if not entry:
            raise tornado.web.HTTPError(404)
        rets = checkout(host=entry.host, repo=entry.repo, user=entry.username,
                        passwd=entry.password, dest=entry.dest)
        for host, result in rets['contacted'].items():
            if not 'failed' in result:
                self.db.execute(
                    "UPDATE entries SET revision = %s where slug = %s",
                    result['after'][0].split(':')[1].strip(), slug
                )
            else:
                error = rets
        logging.info(self.current_user.name + "\t" +
                     tornado.escape.json_encode(rets))
        if error:
            self.write(tornado.escape.json_encode(error))
            return
        self.redirect("/")


class AuthCreateHandler(BaseHandler):

    def check_admin_user(self):
        error = None
        if self.get_current_user().role != options.admin_role:
            error = "Please login as a admin user."
        return error

    @tornado.web.authenticated
    def get(self):
        error = self.check_admin_user()
        self.render("create_author.html", error=error)

    @tornado.web.authenticated
    @gen.coroutine
    def post(self):
        error = self.check_admin_user()
        if error:
            self.render("create_author.html", error=error)
            return
        if self.check_author_exists():
            self.render("create_author.html", error="author already created")
            return
        hashed_password = yield executor.submit(
            bcrypt.hashpw, tornado.escape.utf8(self.get_argument("password")),
            bcrypt.gensalt())
        author_id = self.db.execute(
            "INSERT INTO authors (email, name, role, hashed_password) "
            "VALUES (%s, %s, %s, %s)",
            self.get_argument("email"), self.get_argument("name"),
            self.get_argument("role"), hashed_password)
        self.set_secure_cookie("demo_user", str(author_id))
        self.redirect(self.get_argument("next", "/"))


class AuthLoginHandler(BaseHandler):

    def get(self):
        error = None
        if not self.any_author_exists():
            error = "First you must create a admin user."
        self.render("login.html", error=error)

    @gen.coroutine
    def post(self):
        author = self.db.get("SELECT * FROM authors WHERE email = %s",
                             self.get_argument("email"))
        if not author:
            self.render("login.html", error="email not found")
            return
        hashed_password = yield executor.submit(
            bcrypt.hashpw, tornado.escape.utf8(self.get_argument("password")),
            tornado.escape.utf8(author.hashed_password))
        if hashed_password == author.hashed_password:
            self.set_secure_cookie("demo_user", str(author.id))
            self.redirect(self.get_argument("next", "/"))
        else:
            self.render("login.html", error="incorrect password")


class AuthLogoutHandler(BaseHandler):

    def get(self):
        self.clear_cookie("demo_user")
        self.redirect(self.get_argument("next", "/"))


class EntryModule(tornado.web.UIModule):

    def render(self, entry):
        return self.render_string("modules/entry.html", entry=entry)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()

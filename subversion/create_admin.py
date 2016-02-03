#!/usr/bin/env python
# -*- coding:utf-8 -*-

import bcrypt
import getpass
import sys
from main import Application, options

email = raw_input("Admin email: ")
username = raw_input("Admin username: ")
password = getpass.getpass("Admin password: ")
password2 = getpass.getpass("Admin password again: ")

if password != password2:
    print "Password doesn\'t match."
    sys.exit()

hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

conn = Application()
conn.db.execute(
    "INSERT INTO authors(email, name, role, hashed_password)"
    "VALUES (%s, %s, %s, %s)", email, username, options.admin_role, hashed_password)

print "Create admin user %s success." % email

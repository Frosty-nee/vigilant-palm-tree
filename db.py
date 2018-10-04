import hashlib
import os
import string
import random
import binascii

import sqlalchemy
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import backref, joinedload, relationship
import sqlalchemy.ext.declarative
import psycopg2

#conn = psycopg2.connect("dbname=dice user=dice")
#curs = conn.cursor()
engine = sqlalchemy.create_engine(sqlalchemy.engine.url.URL(
	drivername='postgresql+psycopg2',
	username='dice',
	database='dice')
	)
session = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(
		autocommit=False, autoflush=False, bind=engine))


Base = sqlalchemy.ext.declarative.declarative_base()
Base.query = session.query_property()

class User(Base):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True)
	username = Column(String)
	email = Column(String, unique=True)
	salt = Column(String)
	password = Column(String)

	def __repr__(self):
		return "<User(username='%s', email='%s', password='%s', salt='%s')>" % (self.username, self.email, self.password, self.salt)
	
	@staticmethod
	def hash_pw(password, salt=None):
		if salt is None:
			salt = os.urandom(24)
		hashed = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
		hashed_hex = binascii.hexlify(hashed).decode()
		salt_hex = salt.hex()
		return hashed_hex, salt_hex

	@staticmethod
	def login(email, password):
		user = session.query(User).filter(User.email == email).first()
		
		if not user:
			return False
		hashed, _ = User.hash_pw(password, binascii.unhexlify(user.salt))
		if hashed == user.password:
			return user

def init_db():
	Base.metadata.create_all(bind=engine)

def drop_db():
	pass

if __name__ == '__main__':
	import sys
	if sys.argv:
			if sys.argv[1] == 'init':
				init_db()
			elif sys.argv[1] == 'drop':
				drop_db()

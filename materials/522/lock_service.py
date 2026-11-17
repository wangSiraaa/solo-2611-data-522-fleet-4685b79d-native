"""Existing exclusive partition guards: one transaction per client currently works."""
import sqlite3
import uuid

class LockService:
    def __init__(self, path):
        self.path = str(path)
        with self.connect() as c:
            c.execute('CREATE TABLE IF NOT EXISTS grants(token TEXT PRIMARY KEY, session TEXT NOT NULL, resource TEXT NOT NULL, scope TEXT NOT NULL, tx TEXT)')
    def connect(self):
        return sqlite3.connect(self.path, timeout=2)
    def acquire(self, session, resource, scope='session', tx=None):
        with self.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            other=c.execute('SELECT session FROM grants WHERE resource=? AND session<>?', (resource,session)).fetchone()
            if other:
                return {'status':'waiting','resource':resource}
            token=uuid.uuid4().hex
            c.execute('INSERT INTO grants VALUES(?,?,?,?,?)',(token,session,resource,scope,tx))
            return {'status':'granted','token':token}
    def release(self, session, token):
        with self.connect() as c:
            return c.execute('DELETE FROM grants WHERE session=? AND token=?',(session,token)).rowcount == 1
    def end_transaction(self, session, tx):
        with self.connect() as c:
            # Original users owned a connection for one transaction only.
            c.execute('DELETE FROM grants WHERE session=?',(session,))
    def close_session(self, session):
        with self.connect() as c:
            c.execute('DELETE FROM grants WHERE session=?',(session,))
    def inspect(self, resource):
        with self.connect() as c:
            return c.execute('SELECT session,scope,tx FROM grants WHERE resource=? ORDER BY token',(resource,)).fetchall()

"""Controlled real ETL worker. Signal acknowledgement is separate from process exit."""
from pathlib import Path
import signal
import sqlite3
import sys
import time

def main():
    controls=Path(sys.argv[1]);db=sys.argv[2];job_id=sys.argv[3]
    controls.mkdir(parents=True,exist_ok=True)
    def stopping(signum,frame):
        (controls/'signal-seen').write_text('TERM')
    signal.signal(signal.SIGTERM,stopping)
    (controls/'ready').write_text(str(__import__('os').getpid()))
    deadline=time.monotonic()+10
    while not (controls/'finish').exists():
        if time.monotonic()>deadline:return 2
        time.sleep(.005)
    if (controls/'signal-seen').exists():return 143
    with sqlite3.connect(db) as c:
        c.execute('CREATE TABLE IF NOT EXISTS products(job_id TEXT PRIMARY KEY, total INTEGER NOT NULL)')
        c.execute('INSERT INTO products SELECT ?, SUM(value) FROM input_rows',(job_id,))
    return 0
if __name__=='__main__':raise SystemExit(main())

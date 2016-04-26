from json import load
from JumpScale import j


EMAILS_DIR = j.sal.fs.joinPaths(j.dirs.varDir, 'email')

def get_msg_path(key):
    ts, _, _ = key.partition("-")
    return j.sal.fs.joinPath(EMAILS_DIR, ts.tm_year, ts.tm_mon, ts.tm_mday, key)


def get_json_msg(key):
    return load(get_msg_path(key))

from JumpScale import j

class attrdict(dict):
    def __getattr__(self, k):
        return self[k]

    def __dir__(self):
        atts=list(self.keys())
        atts.extend(dir(super()))

        return atts

def toattrdict(d):
    if isinstance(d, dict):
        d=attrdict(d) #the parent
        for k,v in d.items():
            if isinstance(v, dict):
                d[k]=toattrdict(v)

        return d
    return d


m="""
{

'msg':
    {
        'raw_msg': 'somethinggg'
        'headers': 'somethinnnn1111'
        'text' : 'that the bodyyy'
        'from_email': 'ahmed@there.com'
        'from_name': 'ahmed'
        'to': 'someone2'
        'email': 'someone2 @there.com'

    }
}


"""
class Message(object):

    def __init__(self, msg):
        if isinstance(msg, dict):
            self.msg=toattrdict(msg)
        elif isinstance(msg, str):
            self.msg=json.loads(msg)['msg']
        else:
            pass

if __name__=="__main__":
    msg=Message(m)
    print(msg)

from JumpScale import j
from JumpScale.tools.zip.ZipFile import ZipFile

try:
    import github
except:
    cmd="pip3 install pygithub"
    j.do.execute(cmd)
    import github


class GitHubFactory(object):
    def __init__(self):
        self.__jslocation__ = "j.clients.github"

    # def getRepoClient(self, account, reponame):
    #     return GitHubRepoClient(account, reponame)

    def getClient(self,secret):
        return GitHubClient(secret)

class Base():

    def __str__(self):
        return str(self._ddict)

    __repr__=__str__    

class User(Base):
    def __init__(self,client,githubObj=None):
        self._ddict={}    
        self._githubObj=githubObj
        if githubObj!=None:
            self.load()

    @property
    def api(self):
        if self._githubObj==None:
            from IPython import embed
            print ("DEBUG NOW get api for user")
            embed()
        return self._githubObj

    def load(self):
        self._ddict={}
        self._ddict["name"]=self.api.name
        self._ddict["email"]=self.api.email
        self._ddict["id"]=self.api.id
        self._ddict["login"]=self.api.login
        
    @property
    def name(self):
        return self._ddict["name"]

    @property
    def email(self):
        return self._ddict["email"]                
        
    @property
    def id(self):
        return self._ddict["id"]        

    @property
    def login(self):
        return self._ddict["login"]    

            


class Milestone(Base):
    def __init__(self,client,githubObj=None):
        self._ddict={}    
        self._githubObj=githubObj
        if githubObj!=None:
            self.load()

    @property
    def api(self):
        if self._githubObj==None:
            from IPython import embed
            print ("DEBUG NOW get api for milestone")
            embed()
        return self._githubObj

    def load(self):
        self._ddict={}
        self._ddict["deadline"]=j.data.time.any2HRDateTime(self.api.due_on)
        self._ddict["id"]=self.api.id
        self._ddict["url"]=self.api.url
        self._ddict["title"]=self.api.title
        self._ddict["number"]=self.api.number
        
    @property
    def title(self):
        return self._ddict["title"]

    @property
    def deadline(self):
        return self._ddict["deadline"]                

    @deadline.setter
    def deadline(self,value):
        self._ddict["deadline"] =j.data.time.any2HRDateTime(self.api.due_on)
        from IPython import embed
        print ("DEBUG NOW set deadline on milestone")
        embed()
        
        
    @property
    def id(self):
        return self._ddict["id"]        

    @property
    def url(self):
        return self._ddict["url"]    

    @property
    def number(self):
        return self._ddict["number"]    


class Issue(Base):

    def __init__(self,repo,ddict={},githubObj=None):
        self.repo=repo
        self._ddict=ddict
        self._githubObj=githubObj
        if githubObj!=None:
            self.load()

    @property
    def api(self):
        if self._githubObj==None:
            from IPython import embed
            print ("DEBUG NOW get api")
            embed()
        return self._githubObj

    @property
    def ddict(self):
        if self._ddict=={}:
            #no dict yet, fetch from github
            self.load()
        return self._ddict


    @property
    def comments(self):
        return self.ddict["comments"]

    @property
    def guid(self):
        return self.repo.fullname+"_"+str(self.ddict["number"])

    @property
    def number(self):
        return int(self.ddict["number"])

    @property
    def title(self):
        return self.ddict["title"]

    @property
    def body(self):
        return self.ddict["body"]

    @property
    def time(self):
        return self.ddict["time"]

    @property
    def url(self):
        return self.ddict["url"]

    @property
    def assignee(self):
        return self.ddict["assignee"]

    @property
    def labels(self):
        return self.ddict["labels"]

    @property
    def id(self):
        return self.ddict["id"]

    @labels.setter
    def labels(self,val):
        #check if all are already in labels, if yes nothing to do
        if len(val)==len(self.ddict["labels"]):
            self.ddict["labels"].sort()
            val.sort()
            if val==self.ddict["labels"]:
                return
        self.ddict["labels"]=val
        toset=[self.repo.getLabel(item) for item in self.ddict["labels"]]
        self.api.set_labels(*toset)

    @property
    def milestone(self):
        return self.ddict["milestone"]
    
    @property
    def state(self):
        states=[]
        for label in self.labels:
            if label.startswith("state"):
                states.append(label)
        if len(states)==1:
            return states[0]
        else:
            self.state="state_new"
            return "state_new"

    @state.setter
    def state(self,val):
        return self._setLabels(val,"state")

    @property
    def type(self):
        items=[]
        for label in self.labels:
            if label.startswith("type"):
                items.append(label)
        if len(items)==1:
            return items[0]
        else:
            self.type="type_unknown"
            return "type_unknown"        

    @type.setter
    def type(self,val):
        return self._setLabels(val,"type")

    @property
    def priority(self):
        items=[]
        for label in self.labels:
            if label.startswith("priority"):
                items.append(label)
        if len(items)==1:
            return items[0]
        else:
            self.priority="priority_normal"
            return self.priority 

    @priority.setter
    def priority(self,val):
        return self._setLabels(val,"priority")

    @property
    def process(self):
        items=[]
        for label in self.labels:
            if label.startswith("process"):
                items.append(label)
        if len(items)==1:
            return items[0]
        else:
            self.priority=""
            return self.priority 

    @process.setter
    def process(self,val):
        return self._setLabels(val,"process")

    def _setLabels(self,val,category):

        if val.startswith(category):
            val=val[7:]
        val=val.strip("_")
        val=val.lower()

        val="%s_%s"%(category,val)

        if val not in self.repo.labelnames:
            self.repo.labelnames.sort()
            llist=",".join(self.repo.labelnames)
            raise j.exceptions.Input("Label needs to be in list:%s, now is: '%s'"%(llist,val))

        #make sure there is only 1
        labels2set=self.labels
        items=[]
        for label in self.labels:
            if label.startswith(category):
                items.append(label)
        if len(items)==1 and val in items:
            return
        for item in items:
            labels2set.pop(item)
        if val!=None or val!="":
            labels2set.append(val)
        self.labels=labels2set

    def load(self):

        self._ddict={}

        #check labels
        labels=[item.name for item in self.api.labels]
        newlabels=[]
        for label in labels:
            if label not in self.repo.labels2set:
                if label in replacelabels:
                    if replacelabels[label] not in newlabels:
                        newlabels.append(replacelabels[label] )
            else:
                if label not in newlabels:
                    newlabels.append(label)

        if labels!=newlabels:
            from IPython import embed
            print ("DEBUG NOW change labels")
            embed()
            labels2set=[self.repo.getLabel(item) for item in newlabels]
            self.api.set_labels(labels2set)
            labels=newlabels

        comments=[comment for comment in self.api.get_comments()]
        commentsToSet=[]
        if len(comments)>0:            
            for comment in comments:                
                obj={}
                user=self.repo.client.getUserLogin(githubObj=comment.user)
                obj["user"]=user
                obj["url"]=comment.url
                obj["id"]=comment.id
                obj["body"]=comment.body
                obj["time"]=j.data.time.any2HRDateTime([comment.last_modified,comment.created_at])
                commentsToSet.append(obj)
            
        self._ddict["labels"]=labels
        self._ddict["id"]=self.api.id
        self._ddict["url"]=self.api.html_url
        self._ddict["number"]=self.api.number
        

        self._ddict["assignee"]=self.repo.client.getUserLogin(githubObj=self.api.assignee)
        self._ddict["state"]=self.api.state
        self._ddict["title"]=self.api.title

        self._ddict["body"]=self.api.body

        self._ddict["comments"]=commentsToSet

        self._ddict["time"]=j.data.time.any2HRDateTime([self.api.last_modified,self.api.created_at])
        
        print ("LOAD:%s %s"%(self.repo.fullname,self._ddict["title"]))

        if self.api.milestone==None:
            self._ddict["milestone"]=""
        else:
            ms=self.repo.client.getMilestone(githubObj=self.api.milestone)
            self._ddict["milestone"]="%s:%s"%(ms.number,ms.title)
            
replacelabels={'bug':'type_bug',
 'duplicate':'process_duplicate',
 'enhancement':'type_feature',
 'help wanted':'state_question',
 'invalid':'state_question',
 'question':'state_question',
 'wontfix':'process_wontfix',
 'completed':'state_verification',
 'in progress':'state_inprogress',
 'ready':'state_verification',
 'story':'type_story',
 'urgent':'priority_urgent'}


class GithubRepo():
    def __init__(self, client,fullname):
        self.client=client
        self.fullname=fullname
        self._repoclient=None
        self._labels=None
        self.issues=[]

    @property
    def api(self):
        if self._repoclient==None:
            self._repoclient=self.client.api.get_repo(self.fullname)
        return self._repoclient

    @property
    def labelnames(self):
        return [item.name for item in self.labels]

    @property
    def labels(self):
        if self._labels==None:
            self._labels=[item for item in self.api.get_labels()]
        return self._labels

    def getLabel(self,name):
        for item in self.labels:
            if item.name==name:
                return item
        raise RuntimeError("not found")

    def getColor(self,name):

        colors={'state_question':'fbca04',
         'priority_urgent':'d93f0b',
         'state_verification':'006b75',
         'priority_minor':'',
         'type_task':'',
         'type_feature':'',
         'process_wontfix':"ffffff",
         'priority_critical':"b60205",
         'state_inprogress':"e6e6e6",
         'priority_normal':"e6e6e6",
         'type_story':"ee9a00",
         'process_duplicate':"",
         'state_closed':"5319e7",
         'type_bug':"fc2929",
         'state_accepted':"0e8a16",
         'type_question':"fbca04",
         'state_new':"1d76db"}

        if name.startswith("process"):
            return("e6e6e6")

        if name.startswith("type"):
            return("fef2c0")

        if name in colors:
            color=colors[name]
            if color=="":
                color="ffffff"
            return color

        return "ffffff"

    def configureLabels(self,labels2set):
        self.labels2set=labels2set

        #walk over github existing labels
        for item in self.labels:
            name=item.name.lower()
            if name not in labels2set:                
                #label in repo does not correspond to label we need                
                if name in replacelabels:
                    nameNew=replacelabels[item.name.lower()]
                    if not nameNew in self.labelnames:
                        color=self.getColor(name)
                        print ("change label: %s %s %s"%(self.fullname,nameNew,color))
                        item.edit(nameNew, color)
                        self._labels=None                            
                else:
                    #no replacement
                    from IPython import embed
                    print ("DEBUG NOW no replacement label")
                    embed()
        
            #we recognise the label
            print ("check color of %s %s"%(self.fullname,name))
            color=self.getColor(name)
            if item.color != color:
                print ("change label color: %s %s %s"%(self.fullname,name,color))
                item.edit(name, color)
                    
                self._labels=None
                    
        for name in labels2set:
            if name not in self.labelnames:
                #does not exist yet in repo
                color=self.getColor(name)
                print ("create label: %s %s %s"%(self.fullname,name,color))
                self.api.create_label(name, color)
                self._labels=None

        for item in self.labels:
            if item.name not in labels2set:
                print ("delete label: %s %s"%(self.fullname,item.name))
                item.delete()
    
    def loadIssues(self):
        for item in self.api.get_issues():     
            self.issues.append(Issue(self,githubObj=item))

class GitHubClient():

    def __init__(self, secret):
        self.api=github.Github(secret)
        self.users={}
        self.milestones={}

    def getRepo(self,fullname):
        """
        fullname e.g. incubaid/myrepo
        """
        return GithubRepo(self,fullname)

    def getUserLogin(self,githubObj):
        if githubObj==None:
            return ""
        if not githubObj.login in self.users:                
            user=User(self,githubObj=githubObj)
            self.users[githubObj.login]=user
        return self.users[githubObj.login].login

    def getUser(self,login="",githubObj=None):
        if login in self.users:
            return self.users[login]

        if githubObj!=None:
            if not githubObj.login in self.users:                
                user=User(self,githubObj=githubObj)
                self.users[githubObj.login]=user
            return self.users[githubObj.login]

    def getMilestone(self,number=None,githubObj=None):
        if number in self.milestones:
            return self.milestones[number]

        if githubObj!=None:
            if not githubObj.number in self.milestones:                
                obj=Milestone(self,githubObj=githubObj)
                self.milestones[githubObj.number]=obj
            return self.milestones[githubObj.number]


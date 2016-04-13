from JumpScale import j
from JumpScale.tools.zip.ZipFile import ZipFile

try:
    import github
except:
    cmd="pip3 install pygithub"
    j.do.execute(cmd)
    import github

import copy

class GitHubFactory(object):
    def __init__(self):
        self.__jslocation__ = "j.clients.github"

    # def getRepoClient(self, account, reponame):
    #     return GitHubRepoClient(account, reponame)

    def getClient(self,secret):
        return GitHubClient(secret)

class Base():


    @property
    def bodyWithoutTags(self):
        #remove the tag lines from the body
        out=""
        for line in self.body.split("\n"):
            if line.startswith("##") and not line.startswith("###"):
                continue
            out+="%s\n"%line

        out=out.rstrip()+"\n"
        return out




    @property
    def tags(self):
        if "_tags" not in self.__dict__:
            lineAll=""
            for line in self.body.split("\n"):
                #look for multiple lines, append and then transform to tags
                if line.startswith(".. ") and not line.startswith("..."):
                    line0=line[2:].strip()
                    lineAll+="%s "%line0
            self._tags=j.data.tags.getObject(lineAll)
        return self._tags

    @tags.setter
    def tags(self,ddict):
        if j.data.types.dict(ddict)==False:
            raise j.exceptions.Input("Tags need to be dict as input for setter, now:%s"%ddict)

        keys=ddict.keys()
        keys.sort()

        out=self.bodyWithoutTags+"\n"
        for key,val in ddict.items():
            out+=".. %s:%s\n"%(key,val)

        self.body=out
        return self.tags


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

            
class RepoMilestone(Base):
    """
    milestone as defined on 1 specific repo
    """
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
        self._ddict["body"]=self.api.description
        self._ddict["number"]=self.api.number
        self._ddict["name"]=""
        self._ddict["owner"]=""

        #load the props
        self.owner
        self.name

    @property
    def title(self):
        return self._ddict["title"]

    @title.setter
    def title(self,val):
        self._ddict["title"]=val
        from IPython import embed
        print ("DEBUG NOW set title in ms")
        embed()
        s
        

    @property
    def name(self):
        """
        is name, corresponds to ays instance of milestone who created this
        """
        if self._ddict["name"]=="":
            self._ddict["name"]=self.tags.tagGet("name",default="")
        if self._ddict["name"]=="":
            return self.title
        return self._ddict["name"]

    @property
    def owner(self):
        """
        is name, corresponds to ays instance of milestone who created this
        """
        if self._ddict["owner"]=="":
            self._ddict["owner"]=self.tags.tagGet("owner",default="")
        return self._ddict["owner"]

    @property
    def descr(self):
        return self.bodyWithoutTags

    #synonym to let the tags of super class work
    @property
    def body(self):
        return self._ddict["body"]      

    @body.setter
    def body(self,val):
        if self._ddict["body"]!=val:
            self._ddict["body"]=val
            self.api.edit(self.title, description=val)

    @property
    def deadline(self):
        return self._ddict["deadline"]                

    @deadline.setter
    def deadline(self,val):
        self._ddict["deadline"]=val
        from IPython import embed
        print ("DEBUG NOW set deadline in ms")
        embed()
        s
        

        
    @property
    def id(self):
        return self._ddict["id"]        

    @property
    def url(self):
        return self._ddict["url"]    

    @property
    def number(self):
        return self._ddict["number"]    

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
     'urgent':'priority_urgent',
     'type_bug':'type_unknown',
     'type_story':'type_unknown'}

class Issue(Base):

    def __init__(self,repo,ddict={},githubObj=None,md=None):
        self.repo=repo
        self._ddict=ddict
        self._githubObj=githubObj
        if githubObj!=None:
            self.load()
        if md!=None:
            self._loadMD(md)
        # self.todo

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
            return states[0][len("state"):].strip("_")
        elif len(states)>1:
            self.state="question"
        else:
            return ""

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
            return items[0][len("type"):].strip("_")
        else:
            self.type="type_unknown"
            return "unknown"        

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
            return items[0][len("priority"):].strip("_")
        else:
            self.priority="normal"
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
            return items[0][len("process"):].strip("_")
        else:
            return ""

    @process.setter
    def process(self,val):
        return self._setLabels(val,"process")

    def _setLabels(self,val,category):

        if val.startswith(category):
            val=val[len(category):]
        val=val.strip("_")
        val=val.lower()

        val="%s_%s"%(category,val)

        if val not in self.repo.labelnames:
            self.repo.labelnames.sort()
            llist=",".join(self.repo.labelnames)
            raise j.exceptions.Input("Label needs to be in list:%s (is understood labels in this repo on github), now is: '%s'"%(llist,val))

        #make sure there is only 1
        labels2set=self.labels
        items=[]
        for label in self.labels:
            if label.startswith(category):
                items.append(label)
        if len(items)==1 and val in items:
            return
        for item in items:
            labels2set.pop(labels2set.index(item))
        if val!=None or val!="":
            labels2set.append(val)
        self.labels=labels2set

    def load(self):

        self._ddict={}

        #check labels
        labels=[item.name for item in self.api.labels] #are the names
        newlabels=[]
        for label in labels:
            if label not in self.repo.labelnames:
                if label in replacelabels:
                    if replacelabels[label] not in newlabels:
                        newlabels.append(replacelabels[label] )
            else:
                if label not in newlabels:
                    newlabels.append(label)

        if labels!=newlabels:
            print("change label:%s for %s"%(labels,self.api.title))
            labels2set=[self.repo.getLabel(item) for item in newlabels]
            self.api.set_labels(*labels2set)
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

    def getMarkdown(self,priotype=True):
        md=j.data.markdown.getDocument()
        md.addMDComment1Line("issue:%s"%self.number)
        md.addMDHeader(4,self.title)
        if self.body!=None and self.body.strip()!="":
            md.addMDBlock(self.body)
        h=[self.state,"[%s](%s)"%(self.number,self.url)]
        rows=[]
        t=md.addMDTable()
        t.addHeader(h)
        t.addRow(["milestone",self.milestone])
        t.addRow([self.priority,self.type])
        t.addRow(["assignee",self.assignee])
        t.addRow(["time",self.time])

        if self.comments!=[]:
            for comment in self.comments:
                md.addMDHeader(5,"comment")
                md.addMDBlock(comment["body"])
                h=[comment["user"],"[%s](%s)"%(comment["id"],comment["url"])]
                t=md.addMDTable()
                t.addHeader(h)
                t.addRow(["time",comment["time"]])

        return md

    def _loadMD(self,md):
        from IPython import embed
        print ("DEBUG NOW loadmd")
        embed()


    @property
    def todo(self):
        if "_todo" not in self.__dict__:
            todo=[]
            for line in self.body.split("\n"):
                if line.startswith("!! "):
                    todo.append(line.strip().strip("!"))
            for comment in self.comments:
                for line in comment['body'].split("\n"):
                    if line.startswith("!! "):
                        todo.append(line.strip().strip("!"))
            self._todo=todo
        return self._todo

    @property
    def isStory(self):
        #check on type_story
        #check on ($story) and end of title, needs to be well chosen name
        #if issue, fix
        pass

    @property
    def isTask(self):
        #check on type_task
        #check on $story: ...
        #if issue, fix
        pass
        #@todo (1)


    def process(self):
        """
        find all todo's
        cmds supported

        !!prio $prio  ($prio is checked on first 4 letters, e.g. critical, or crit matches same)
        !!p $prio (alias above)

        !!move gig-projects/home (move issue to this project, try to keep milestones, labels, ...)

        !!delete

        """
        #process commands & execute

        #when repo of type home (ONLY THERE)    
            #for any issue check for ($storyname) at end of title
                #if found remember the storyname
            #for any issue
                #see if there is '$storyname:' in title  (no spaces in $storyname)
                #find the story, if story found in same repo then put link in body of this issue e.g. story:#4
                #in story put link tasks:#4,#5, ...
                #if we found storyname make sure type is task
                #if we found the storyname then make sure type is story
        #describe these rules in our process wiki

        #use repo.stories... property

        #@todo (1)

        
        
class GithubRepo():
    def __init__(self, client,fullname):
        self.client=client
        self.fullname=fullname
        self._repoclient=None
        self._labels=None
        self.issues=[]
        self._milestones=[]

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

    @property
    def stories(self):
        #walk overall issues find the stories (based on type)
        #only for home type repo, otherwise return []
        return []

        #@todo (1)

    @property
    def tasks(self):
        #walk overall issues find the stories (based on type)
        #only for home type repo, otherwise return []
        return []

        #@todo (1)

    @labels.setter
    def labels(self,labels2set):

        for item in labels2set:
            if not j.data.types.string.check(item):
                raise j.exceptions.Input("Labels to set need to be in string format, found:%s"%labels2set)

        #walk over github existing labels
        labelstowalk=copy.copy(self.labels)
        for item in labelstowalk:
            name=item.name.lower()
            if name not in labels2set:                
                #label in repo does not correspond to label we need                
                if name in replacelabels:
                    nameNew=replacelabels[item.name.lower()]
                    if not nameNew in self.labelnames:
                        color=self.getColor(name)
                        print ("change label in repo: %s oldlabel:'%s' to:'%s' color:%s"%(self.fullname,item.name,nameNew,color))
                        item.edit(nameNew, color)
                        self._labels=None                            
                else:
                    #no replacement
                    name='type_unknown'
                    color=self.getColor(name)
                    try:
                        item.edit(name, color)
                    except:
                        item.delete()
                    self._labels=None                            
        
        #walk over new labels we need to set
        for name in labels2set:
            if name not in self.labelnames:
                #does not exist yet in repo
                color=self.getColor(name)
                print ("create label: %s %s %s"%(self.fullname,name,color))
                self.api.create_label(name, color)
                self._labels=None

        name=""

        labelstowalk=copy.copy(self.labels)
        for item in labelstowalk:
            if item.name not in labels2set:
                print ("delete label: %s %s"%(self.fullname,item.name))
                item.delete()
                self._labels=None

        #check the colors
        labelstowalk=copy.copy(self.labels)
        for item in labelstowalk:
            #we recognise the label
            print ("check color of repo:%s labelname:'%s'"%(self.fullname,item.name))
            color=self.getColor(item.name)
            if item.color != color:
                print ("change label color for repo %s %s"%(item.name,color))
                item.edit(item.name, color)                    
                self._labels=None                

    def getLabel(self,name):
        for item in self.labels:
            print ("%s:look for name:'%s'"%(item.name,name))
            if item.name==name:
                return item
        raise j.exceptions.Input("Dit not find label: '%s'"%name)

    def issues_by_type(self,filter=None):
        """
        filter is method which takes  issue as argument and returns True or False to include
        """
        res={}
        for item in self.types:
            res[item]={}
            for issue in self.issues:
                if issue.type==item:
                    if filter==None or filter(issue):
                        res[item].append(issue)
        return res

    def issues_by_state(self,filter=None):
        """
        filter is method which takes  issue as argument and returns True or False to include
        """
        res={}
        for item in self.states:
            res[item]={}
            for issue in self.issues:
                if issue.state==item:
                    if filter==None or filter(issue):
                        res[item].append(issue)
        return res

    def issues_by_priority(self,filter=None):
        """
        filter is method which takes  issue as argument and returns True or False to include
        """
        res={}
        for item in self.priorities:
            res[item]={}
            for issue in self.issues:
                if issue.priority==item:
                    if filter==None or filter(issue):
                        res[item].append(issue)
        return res
    
    def issues_by_type_state(self,filter=None,collapsepriority=True):
        """
        filter is method which takes  issue as argument and returns True or False to include
        returns dict of dict keys: type, state and then issues sorted following priority
        """
        res={}
        for type in self.types:
            res[type]={}
            for state in self.states:
                res[type][state]={}
                for priority in self.priorities:
                    res[type][state][priority]=[]
                    for issue in self.issues:
                        if issue.type==type and issue.state==state :
                            if filter==None or filter(issue):
                                res[type][state][priority].append(issue)
                if collapsepriority:
                    #sort the issues following priority
                    temp=res[type][state]
                    res[type][state]=[]
                    for priority in self.priorities:
                        for subitem in temp[priority]:
                            res[type][state].append(subitem)
        return res

    @property
    def types(self):
        return ["story","ticket","task","bug","feature","question","monitor","unknown"]

    @property
    def priorities(self):
        return ["critical","urgent","normal","minor"]

    @property
    def states(self):
        return ["new","accepted","question","inprogress","verification","closed"]

    @property
    def milestones(self):
        if self._milestones==[]:
            for ms in self.api.get_milestones():
                milestoneObj=self.client.getMilestone(githubObj=ms)
                self._milestones.append(milestoneObj)
        return self._milestones
        
    @property
    def milestoneTitles(self):
        return [item.title for item in self._milestones]

    @property
    def milestoneNames(self):
        return [item.name for item in self._milestones]

    def getMilestone(self,name,die=True):
        if name.strip()=="":
            raise j.exceptions.Input("Name cannot be empty.")
        for item in self.milestones:
            if name==item.name or name==item.title:
                return item
        if die:
            raise j.exceptions.Input("Could not find milestone with name:%s"%name)
        else:
            return None

    def createMilestone(self,name,title,description="",deadline="",owner=""):

        def getBody(descr,name,owner):
            out="%s\n\n"%descr
            out+="## name:%s\n"%name
            out+="## owner:%s\n"%owner
            return out

        ms=self.getMilestone(name,die=False)
        if ms!=None:

            if ms.title!=title:
                ms.title=title
            #@todo milestone setting does not work
            # if ms.deadline!=deadline:
            #     ms.deadline=deadline
            tocheck=getBody(description.strip(),name,owner)
            if ms.body.strip()!=tocheck.strip():
                ms.body=tocheck
        else:
            self._milestones=[]
            due=j.data.time.epoch2ISODateTime(int(j.data.time.any2epoch(deadline)))
            print ("Create milestone on %s: %s"%(self,title))
            body=getBody(description.strip(),name,owner)
            self.api.create_milestone(title=title, description=body)#, due_on=due    #@todo cannot set deadline, please fix


    def deleteMilestone(self,name):
        if name.strip()=="":
            raise j.exceptions.Input("Name cannot be empty.")        
        print ("Delete milestone on %s: '%s'"%(self,name))
        ms=self.getMilestone(name)
        ms.api.delete()
        self._milestones=[]

    def _labelSubset(self,cat):
        res=[]
        for item in self.labels:
            if item.startswith(cat):
                item=item[len(cat):].strip("_")
                res.append(item)
        res.sort()
        return res

    def getColor(self,name):

        # colors={'state_question':'fbca04',
        #  'priority_urgent':'d93f0b',
        #  'state_verification':'006b75',
        #  'priority_minor':'',
        #  'type_task':'',
        #  'type_feature':'',
        #  'process_wontfix':"ffffff",
        #  'priority_critical':"b60205",
        #  'state_inprogress':"e6e6e6",
        #  'priority_normal':"e6e6e6",
        #  'type_story':"ee9a00",
        #  'process_duplicate':"",
        #  'state_closed':"5319e7",
        #  'type_bug':"fc2929",
        #  'state_accepted':"0e8a16",
        #  'type_question':"fbca04",
        #  'state_new':"1d76db"}

        if name.startswith("state"):
            return("c2e0c6") #light green

        if name.startswith("process"):
            return("d4c5f9") #light purple

        if name.startswith("type"):
            return("fef2c0") #light yellow

        if name.startswith("priority_critical"):
            return("b60205")

        if name.startswith("priority_urgent"):
            return("d93f0b")

        if name.startswith("priority"):
            return("f9d0c4")  #roze            

        # if name in colors:
        #     color=colors[name]
        #     if color=="":
        #         color="ffffff"
        #     return color

        return "ffffff"


    def loadIssues(self):
        for item in self.api.get_issues():     
            self.issues.append(Issue(self,githubObj=item))

    def __str__(self):
        return "gitrepo:%s"%self.fullname

    __repr__=__str__                

class GitHubClient():

    def __init__(self, secret):
        self.api=github.Github(secret)
        self.users={}
        self._milestones={}

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
        if number in self._milestones:
            return self._milestones[number]

        if githubObj!=None:
            if not githubObj.number in self._milestones:                
                obj=RepoMilestone(self,githubObj=githubObj)
                self._milestones[githubObj.number]=obj
            return self._milestones[githubObj.number]


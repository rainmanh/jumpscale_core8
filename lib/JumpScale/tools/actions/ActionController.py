
# import sys
# import inspect
# import textwrap
# import operator

from JumpScale import j
from Action import *




class ActionController(object):
    '''Manager controlling actions'''
    def __init__(self, _output=None, _width=70):
        self.__jslocation__ = "j.actions"
        # self._actions = list()
        # self._width = _width
        self.rememberDone=False
        self._lastid={}

    def reset(self,runid=None):
        if runid!=None:
            j.core.db.delete("actions.%s"%runid)
            return
        for item in j.core.db.keys("actions.*"):
            self.reset(item.split(".",1)[1])


    def start(self, action,runid=0,actionRecover=None,args={},die=True,stdOutput=False,errorOutput=True,retry=1,serviceObj=None):
        '''
        self.doc is in doc string of method
        specify recover actions in the description

        name is name of method

        @param id is unique id which allows finding back of action
        @param loglevel: Message level
        @param action: python function to execute
        @param actionRecover: link to other action (same as this object but will be used to recover the situation)
        @param args is dict with arguments
        @param serviceObj: service, will be used to get category filled in
        '''
        runid=str(runid)
        if runid not in self._lastid:
            self._lastid[runid]=0
        self._lastid[runid]+=1
        id=self._lastid[runid]
        action=Action(action,runid=runid,actionRecover=actionRecover,args=args,die=die,stdOutput=stdOutput,errorOutput=errorOutput,retry=retry,serviceObj=serviceObj,id=id)
        action.execute()

        

    # def hasRunningActions(self):
    #     '''Check whether actions are currently running

    #     @returns: Whether actions are runnin
    #     @rtype: bool
    #     '''
    #     return bool(self._actions)
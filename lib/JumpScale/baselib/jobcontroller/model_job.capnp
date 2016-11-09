@0xc95b52bf39888c7e;

struct Job {
  #this object is hosted by actor based on FQDN
  #is the run which asked for this job
  runKey @0 :Text;

  #role of service e.g. node.ssh
  actorName @1 :Text;

  #name e.g. install
  actionName @2 :Text;

  #FQDN of actor who owns this service
  actorFQDN @3 :Text;

  #name of service run by actor e.g. myhost
  serviceName @4 :Text;

  #has link to code which needs to be executed
  actionKey @5 :Text;

  stateChanges @6 :List(StateChange);

  struct StateChange {
    epoch @0: UInt32;
    state @1 :State;
  }

  logs @7 :List(LogEntry);

  struct LogEntry {
    epoch @0: UInt32;
    log @1 :Text;
    level @2 :Int8; #levels as used in jumpscale
    category @3 :Cat;
    enum Cat {
      out @0; #std out from executing in console
      err @1; #std err from executing in console
      msg @2; #std log message
      alert @3; #alert e.g. result of error
      errormsg @4; #info from error
      trace @5; #e.g. stacktrace
    }
    tags @4 :Text;
  }

  # need to know from in which repo to look for the service
  repoKey @8 :Text;
  #info which is input for the action, will be given to methods as service=...
  serviceKey @9 :Text;

  #binary or other
  argsData @10 :Data;

  #dict which will be given to method as **args (msgpack)
  args @11 :Data;

  #is the last current state
  state @12 :State;
  enum State {
      new @0;
      running @1;
      ok @2;
      error @3;
  }

  #msgpack serialized
  result @13 :Data;

  lastModDate @14: UInt32;

  simulate @15: Bool;

  debug @16: Bool;

  profile @17: Bool;
  profileData @18: Data;

}

#is one specific piece of code which can be executed
#is owned by a ACTOR_TEMPLATE specified by actor_name e.g. node.ssh
#this is used to know which code was executed and what exactly the code was
struct Action {

  #name of the method e.g. install
  name @0 :Text;

  actorName @1 :Text;

  code @2 :Text;

  lastModDate @3: UInt32;

  args @4 :Text;

  #documentation string in markdown of the action
  doc @5 :Text;

  #is optional, could be e.g. sourcefile
  origin @6 :Text;

  whoami @7 :Data;

  debug @8: Bool;

  #modules to import
  imports @9 :List(Text);

  log @10: Bool;

  logStdout @11: Bool;

  remember @12: Bool;

}


struct Run {
    #this object is hosted by actor based on FQDN

    #which step is running right now, can only move to next one if previous one was completed
    currentStep @0: UInt16;

    #FQDN of a specific actor which can run multiple jobs & orchestrate work
    aysControllerFQDN @1 :Text;

    steps @2 :List(RunStep);
    struct RunStep {
      epoch @0: UInt32;
      state @1 :State;
      # number of the step in the run
      number @2 :UInt32;
      #list of jobs which need to be executed, key alone is enough to fetch the job info
      jobs @3 :List(Job);
      struct Job {
          key @0 :Text;

          #NEXT IS CACHED INFO, THE MAIN SOURCE OF NEXT INFO IS IN Job
          #BUT is good practice will make all run very much faster& allow fast vizualization
          state @1 :State;
          #e.g. node.ssh
          actorName @2 :Text;
          #name e.g. install
          actionName @3 :Text;
          #name of service run by actor e.g. myhost
          serviceName @4 :Text;

          serviceKey @5:Text;
      }
    }

    #state of run in general
    state @3 :State;
    enum State {
        new @0;
        running @1;
        ok @2;
        error @3;
    }

    lastModDate @4: UInt32;

    logs @5:List(Text);

    #key of repo where run is created
    repo @6 :Text;
}

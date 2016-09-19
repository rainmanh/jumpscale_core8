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

  #info which is input for the action, will be given to methods as service=...
  serviceKey @8 :Text;

  #binary or other
  argsData @9 :Data;

  #dict which will be given to method as **args (msgpack)
  args @10 :Data;

  #is the last current state
  state @11 :State;
  enum State {
      new @0;
      running @1;
      ok @2;
      error @3;
  }

  #msgpack serialized
  result @12 :Data;

  lastModDate @13: UInt32;

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

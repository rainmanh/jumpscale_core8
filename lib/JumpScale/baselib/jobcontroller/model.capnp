@0x13c1ac9e09464fd1;

struct Job {
  #this object is hosted by actor based on FQDN
  #is the run which asked for this job
  runGuid @0 :Text;

  #role of service e.g. node.ssh
  actorName @1 :Text;

  #name e.g. install
  actionName @2 :Text;

  #FQDN of actor who owns this service
  actorFQDN @3 :Text;

  #name of service run by actor e.g. myhost
  serviceName @4 :Text;

  #has link to code which needs to be executed
  actionCodeGUID @5 :Text;

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
  argsCapnp @8 :Data;
  #any other format e.g. binary or text or ... is up to actionmethod to deserialize & use, normally, will be given to method as data=...
  argsData @9 :Data;
  #dict which will be given to method as **args
  argsJson @10 :Data;


  #is the last current state
  state @11 :State;
  enum State {
      new @0;
      running @1;
      ok @2;
      error @3;
  }

  #json serialized result (dict), if any
  result @12 :Text;

}

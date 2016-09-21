@0x93c1ac9f09464fd9;

struct Actor {

  state @0 :State;
  enum State {
    new @0;
    ok @1;
    error @2;
    disabled @3;
  }

  #name of actor e.g. node.ssh (role is the first part of it)
  name @1 :Text;

  #dns name of actor who owns this service
  actorFQDN @2 :Text;

  parent @3 :ActorPointer;

  producers @4 :List(ActorPointer);

  struct ActorPointer {
    actorKey @0 :Text;
    actorName @1 :Text;
    minServices @2 :UInt8;
    maxServices @3 :UInt8;
  }

  actions @5 :List(Action);
  struct Action {
    name @0 :Text;
    #unique key for code of action (see below)
    actionKey @1 :Text;
    type @2 :Type;
    enum Type {
      actor @0;
      service @1;
      node @2;
    }
  }

  recurringTemplate @6 :List(Recurring);
  struct Recurring {
    #period in seconds
    action @0 :Text;
    period @1 :UInt32;
    #if True then will keep log of what happened, otherwise only when error
    log @2 :Bool;
  }


  #where does the template compe from
  origin @7 :Origin;
  struct Origin {
    #link to git which hosts this template for the actor
    gitUrl @0 :Text;
    #path in that repo
    path @1 :Text;
  }

  #python script which interactively asks for the information when not filled in
  serviceDataUI @8 :Text;

  serviceDataSchema @9 :Text;

  data @10 :Data; #is msgpack dict

  dataUI @11 :Text;

  gitRepo @12 :GitRepo;
  struct GitRepo {
    #git url
    url @0 :Text;
    #path in repo
    path @1 :Text;
  }

}

struct Service {
  #is the unique deployed name of the service of a specific actor name e.g. myhost
  name @0 :Text;

  #name of actor e.g. node.ssh
  actorName @1 :Text;

  #FQDN of actor who owns this service
  actorFQDN @2 :Text;

  parent @3 :ServicePointer;

  producers @4 :List(ServicePointer);

  struct ServicePointer {
    actorName @0 :Text;
    serviceName @1 :Text;
    #domain name of actor who owns this service pointed too
    actorFQDN @2 :Text;
    #defines which rights this service has to the other service e.g. owner or not
    key @3 :Text;
  }

  actions @5 :List(Action);

  struct Action {
    #e.g. install
    name @0 :Text;
    #unique key for code of action (see below)
    actionKey @1 :Text;
    state @2: State;
  }

  recurring @6 :List(Recurring);
  struct Recurring {
    #period in seconds
    action @0 :Text;
    period @1 :UInt32;
    lastRun @2: UInt32;
    # needs to be bool
    # if True then will keep log of what happened, otherwise only when error
    log @3: Bool;
  }

  state @7 :State;
  enum State {
    new @0;
    installing @1;
    ok @2;
    error @3;
    disabled @4;
    changed @5;
  }

  data @8 :Data;
  # bytes version of the content of schema.hrd after translation to canpn

  #schema of config data in textual format
  dataSchema @9 :Text;

  gitRepos @10 :List(GitRepo);
  struct GitRepo {
    #git url
    url @0 :Text;
    #path in repo
    path @1 :Text;
  }

  actorKey @11 :Text;

}

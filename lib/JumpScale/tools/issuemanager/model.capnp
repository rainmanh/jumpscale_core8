@0x93c1qq9f09464fd9;

# # common struct
# enum ActionState {
#   new @0;
#   changed @1;
#   ok @2;
#   scheduled @3;
#   disabled @4;
#   error @5;
#   running @6;
# }

struct Issue {

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
    actorRole @0 :Text;
    minServices @1 :UInt8;
    maxServices @2 :UInt8;
    auto @3 :Bool;
    optional @4 :Bool;
    argKey @5 :Text; # key in the args that contains the instance name of the targets
  }

  actions @5 :List(Action);
  struct Action {
    name @0 :Text;
    #unique key for code of action (see below)
    actionKey @1 :Text;
    period @2 :UInt32; #use j.data.time.getSecondsInHR( to show HR
    log @3 :Bool;
    state @4 :ActionState;
  }

  eventFilters @6 :List(EventFilter);

  #where does the template come from
  origin @7 :Origin;
  struct Origin {
    #link to git which hosts this template for the actor
    gitUrl @0 :Text;
    #path in that repo
    path @1 :Text;
  }

  flists @8 :List(Flist);
  struct Flist {
      name @0 :Text;
      namespace @1 :Text;
      mountpoint @2 :Text;
      mode @3 :Mode;
      storeUrl @4:Text;
      content @5 :Text;

      enum Mode {
        ro @0;
        rw @1;
        ol @2;
      }
  }

  #python script which interactively asks for the information when not filled in
  serviceDataUI @9 :Text;

  serviceDataSchema @10 :Text;

  data @11 :Data; #is msgpack dict

  dataUI @12 :Text;

  gitRepo @13 :GitRepo;
  struct GitRepo {
    #git url
    url @0 :Text;
    #path in repo
    path @1 :Text;
  }

}

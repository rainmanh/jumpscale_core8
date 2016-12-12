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

}

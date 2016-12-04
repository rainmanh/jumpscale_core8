@0xd80b12c2d2d132c5;

struct Issue {
    title @0 :Text;
    repo @1 :Text;
    milestone @2 :Text; #reference to key of Milestone
    assignees @3 :List(Text); #keys of user
    isClosed @4 :Bool;
    comments @5 :List(Comment);
    struct Comment{
        owner @0 :User;
        description @1 :Text;
        id @2 :UInt32;
        name @3 :Text; #???
    }
    labels @6 :List(Text);
    content @7 :Text;
    id @8 :UInt32;
    source @9 :Text;
    organization @10 :Text;  #key to organization
    modTime @11 :UInt32;
    creationTime @12 :UInt32;
}

struct Organization{
    owner @0 :Text;
    name @1 :Text;
    description @2 :Text;
    nrIssues @3 :UInt16;
    numMilestones @4 :UInt16;
    id @5 :UInt32;
    source @6 :Text;
    members @7: List(Member)
    struct Member{
        userKey @0 :Text;
        right @1:Text;
    }
    repos @8: List(Text) #references to the repo's
}

struct Repo{
    owner @0 :Text;
    name @1 :Text;
    description @2 :Text;
    nrIssues @3 :UInt16;
    numMilestones @4 :UInt16;
    id @5 :UInt32;
    source @6 :Text;
    milestones @7: List(Milestone)
    struct Milestone{
        name @0 :Text;
        isClosed @1 :Bool;
        nrIssues @2 :UInt16;
        nrClosed @3 :UInt16;
        completeness @4 :UInt16; #in integer (0-100)
        deadline @5 :UInt32;
        id @6 :UInt32;
    }
    members @7: List(Member)
    struct Member{
        userKey @0 :Text;
        right @1:Text;
    }
    labels @8 :List(Text);
}

struct User{
    name @0 :Text;
    fullname @1 :Text;
    email @2 :Text;
    id @3 :UInt32;
    source @4 :Text;
}

@0xd80b12c2d2d132c5;

struct Issue {
    title @0 :Text;
    repo @1 :UInt32;
    milestone @2 :UInt32; #reference to key of Milestone
    assignees @3 :List(UInt32); #keys of user
    isClosed @4 :Bool;
    comments @5 :List(Comment);
    struct Comment{
        owner @0 :UInt32;
        content @1 :Text;
        id @2 :UInt32;
    }
    labels @6 :List(Text);
    content @7 :Text;
    id @8 :UInt32;
    source @9 :Text;
    #organization @10 :Text;  #key to organization , not sure??
    modTime @10 :UInt32;
    creationTime @11 :UInt32;
    gogsRefs @12 :List(GogsRef);
    struct GogsRef{
        name @0 :Text;
        id @1 :UInt32;
    }

}

struct Organization{
    owners @0 :List(Text);
    name @1 :Text;
    description @2 :Text; # deos not exist will place in it full name
    nrIssues @3 :UInt16;
    nrMilestones @4 :UInt16;
    gogsRefs @5 :List(GogsRef);
    struct GogsRef{
        name @0 :Text;
        id @1 :UInt32;
    }
    members @6 :List(Member);
    struct Member{
        key @0 :Text;
        access @1:UInt16;
        name @2: Text;
    }
    repos @7 :List(Repo);
    struct Repo{
        key @0 :Text;
        name @1: Text;
        access @2:UInt16;
    }

}

struct Repo{
    owner @0 :Text;
    name @1 :Text;
    description @2 :Text;
    nrIssues @3 :UInt16;
    nrMilestones @4 :UInt16;
    id @5 :UInt32;
    source @6 :Text;
    milestones @7 :List(Milestone);
    struct Milestone{
        name @0 :Text;
        isClosed @1 :Bool;
        nrIssues @2 :UInt16;
        nrClosedIssues @3 :UInt16;
        completeness @4 :UInt16; #in integer (0-100)
        deadline @5 :UInt64;
        id @6 :UInt32;
    }
    members @8 :List(Member);
    struct Member{
        userKey @0 :Text;
        access @1 :UInt16;
    }
    labels @9 :List(Text);
    gogsRefs @10 :List(GogsRef);
    struct GogsRef{
        name @0 :Text;
        id @1 :UInt32;
    }
}

struct User{
    name @0 :Text; #as to be used to represent in UI
    fullname @1 :Text;
    email @2 :Text; #will be used for escalation
    gogsRefs @3 :List(GogsRef);
    struct GogsRef{
        name @0 :Text;
        id @1 :UInt32;
    }
    githubId @4 :Text; #e.g. despiegk
    telegramId @5: Text;#e.g. despiegk
    iyoId@6: Text;#e.g. despiegk
}

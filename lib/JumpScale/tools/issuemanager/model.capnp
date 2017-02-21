@0xd80b12c2d2d132c5;

struct Issue {
    title @0 :Text;
    repo @1 :Text;
    milestone @2 :Text; #reference to key of Milestone
    assignees @3 :List(Text); #keys of user
    isClosed @4 :Bool;
    comments @5 :List(Comment);
    struct Comment{
        owner @0 :Text;
        comment @1 :Text;
    }
    labels @6 :List(Text);
    content @7 :Text;
    organization @8 :Text;
    modTime @9 :UInt32;
    creationTime @10 :UInt32;
    gogsRefs @11 :List(GogsRef);
    struct GogsRef{
        name @0 :Text;
        id @1 :UInt32;
    }

}

struct Organization{
    owners @0 :List(Text);
    name @1 :Text;
    description @2 :Text;
    nrIssues @3 :UInt16;
    nrRepos @4 :UInt16;
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
    members @5 :List(Member);
    struct Member{
        userKey @0 :Text;
        access @1 :UInt16;
    }
    gogsRefs @6 :List(GogsRef);
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

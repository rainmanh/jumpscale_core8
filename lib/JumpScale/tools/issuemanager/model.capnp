@0xd80b12c2d2d132c5;

struct Issue {
    title @0 :Text;
    repo @1 :Repo;
    milestone @2 :Milestone;
    assignee @3 :User;
    isClosed @4 :Bool; 
    numComments @5 :UInt16;
    label @6 :Label;
    content @7 :Text;
    struct Repo{
        owner @0 :User; 
        name @1 :Text;
        description @2 :Text; 
        numIssues @3 :UInt16;
        numMilestones @4 :UInt16;
    }
    struct User{
        name @0 :Text;  
        fullname @1 :Text; 
        email @2 :Text; 
    }
    
    struct Milestone{
        name @0 :Text; 
        isClosed @1 :Bool;
        numIssues @2 :UInt16;
        numClosed @3 :UInt16;
        completeness @4 :UInt16;   
        deadline @5 :UInt64; 
    }

    struct Label{
        name @0 :Text;
        color @1 :Text;  
    }

    
}

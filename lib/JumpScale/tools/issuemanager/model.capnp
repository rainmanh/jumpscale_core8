@0xd80b12c2d2d132c5;
struct Issue {
    #all the id variables will be replaces with full structs such as repo and label , but WIP so for now 
    title @0 :Text;
    repoId @1: UInt32; 
    milestoneId @2: UInt16;
    assigneeId @3: UInt16;
    isClosed @4: Bool; 
    numComments @5: UInt16;
    labelId @6: UInt16;
    content @7: Text;
    
}



# issue
#     id 
#     repo_id
#     title
#     content
#     milestone_id
#     assignee_id 
#     is_closed
#     is_pull
#     no_comments
# 
# issue_label 
#     id
#     issue_id
#     label_id
# 
# issue_user 
#     id
#     issue_id 
#     repo_id
#     milestone_id
#     is_read
#     is_assigned
#     is_mentioned 
#     is_closed


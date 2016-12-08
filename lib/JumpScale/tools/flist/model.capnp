@0xae9223e76351538a;

struct Dir {

  #name of dir
  name @0 :Text;

  #location in filesystem = namespace
  location @1 :Text;

  files @2 :List(File);
  struct File{
      name @0 : Text;
      #blocksize in bytes = blocksize * 4 KB, blocksize is same for all parts of file
      #max blocksize = 128 MB
      blocksize @1 : UInt8;
      blocks @2 :List(Data); #list of the hashes of the blocks
      size @3 : UInt64; #in bytes
      aclkey @4: UInt32; #is pointer to ACL
      modificationTime @5: UInt32;
      creationTime @6: UInt32;
  }

  dirs @3 :List(SubDir);
  struct SubDir{
      name @0 : Text;
      key @1: Text;
  }

  links @4 :List(Link); #only for non dirs
  struct Link{
      name @0 : Text;
      aclkey @1: UInt32; #is pointer to ACL
      destDirKey @2: Text; #key of dir in which destination is
      destName @3: Text;
      modificationTime @4: UInt32;
      creationTime @5: UInt32;
  }

  specials @5 :List(Special);
  struct Special{
      name @0 : Text;
      type @1 :State;
      # - 0: socket       (S_IFSOCK)
      # - 1: block device (S_IFBLK)
      # - 2: char. device (S_IFCHR)
      # - 3: fifo pipe    (S_IFIFO)
      enum State {
        socket @0;
        block @1;
        chardev @2;
        fifopipe @3;
        unknown @4;
      }
      #data relevant for type of item
      data @2 :Data;
      modificationTime @3: UInt32;
      creationTime @4: UInt32;
  }

  parent @6 :Text; #dir key of parent

  #metadata for dir
  size @7 : UInt64; #in bytes
  aclkey @8: UInt32; #is pointer to ACL
  isLink @9: Bool; #if is link and not physically on disk
  modificationTime @10: UInt32;
  creationTime @11: UInt32;


}


struct UserGroup{
    name @0 : Text;
    #itsyouonline id
    iyoId @1 : Text;
    #itsyouonline unique id per user or group, is globally unique
    iyoInt @2 : UInt64;
}


struct ACI {
    #for backwards compatibility with posix
    uname @0 :Text;
    gname @1 :Text;
    mode @2 : UInt16;

    rights @3 :List(Right);
    struct Right {
      #text e.g. rwdl- (admin read write delete list -), freely to be chosen
      #admin means all rights (e.g. on / = namespace or filesystem level all rights for everything)
      #- means remove all previous ones (is to stop recursion), if usergroupid=0 then is for all users & all groups
      right @0 :Text;
      usergroupid @1 : UInt16;
    }

    id @4 :UInt32;
}

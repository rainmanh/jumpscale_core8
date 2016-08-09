@0x93c1ac9f09464fd4
struct Actor {

    state @0: State
    enum State {
        new @0
        ok @1
        error @2
        disabled @3
    }

    # role of service e.g. node.ssh
    role @1: Text

    # dns name of actor who owns this service
    actorFQDN @2: Text

    parentTemplate @3: ActorPointer

    producersTemplate @4: List(ActorPointer)

    struct ActorPointer {
        role @0: Text
        actorDN @1: Text
        # defines which rights this actor has to the other actor e.g. owner or
        # not
        key @2: Text
    }

    key @5: Text
    ownerkey @6: Text

    actionsTemplate @7: List(Action)
    struct Action {
        name @0: Text
        # unique key for action (hash of code inside action)
        key @1: Text
        code @2: Text
    }

    recurringTemplate @8: List(Recurring)
    struct Recurring {
        #period in seconds
        action @0: Text
        period @1: UInt32
        # if True then will keep log of what happened, otherwise only when
        # error
        log @2: Bool
    }

    serviceDataSchema @9: Text
    actorDataSchema @10: Text

    hashes @11: Hashes
    struct Hashes {
        # capnp schema for the service
        serviceDataSchema @0: Text
        # capnp schema for the actor, whatever is stored here is valid for each
        # service
        actorDataSchema @1: Text
        actions @2: Text
    }

    origin @12: Origin
    struct Origin {
        # link to git which hosts this template for the actor
        giturl @0: Void
        # path in that repo
        path @1: Text
    }

    # python script which interactively asks for the information when not
    # filled in
    serviceDataUI @13: Text
    actorDataUI @14: Text
}

struct Service {
    name @0: Text
    # role of service e.g. node.ssh
    role @1: Text

    # FQDN of actor who owns this service
    actor @2: Text

    parent @3: ServicePointer

    producers @4: List(ServicePointer)

    struct ServicePointer {
        name @0: Text
        role @1: Text
        # domain name of actor who owns this service pointed too
        actorFQDN @2: Text
        # defines which rights this service has to the other service e.g. owner or
        # not
        key @3: Text
    }

    actions @5: List(Action)
    struct Action {
        name @0: Text
        # unique key for action (hash of code inside action)
        key @1: Text
    }

    recurring @6: List(Recurring)
    struct Recurring {
        #period in seconds
        action @0: Text
        period @1: UInt32
        # needs to be bool
        # if True then will keep log of what happened, otherwise only when
        # error
        log @2: UInt32
    }

    state @7: State
    enum State {
        new @0
        init @1
        installing @2
        ok @3
        error @4
        disabled @5
        changed @6
    }

    configdata @8: Data

    hashes @9: Hashes
    struct Hashes {
        configdata @0: Text
        actorActions @1: Text
        actorData @2: Text
    }

    key @10: Text


    gitrepos @11: List(GitRepo)
    struct GitRepo {
        # git url
        url @0: Text
        #path in repo
        path @1: Text
    }

}


struct ActorIndex {
    actors @0: List(IndexItem)
    struct IndexItem {
        role @0: Text
        key @1: Text
    }

}

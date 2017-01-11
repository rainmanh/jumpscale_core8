from JumpScale import j
import dns.resolver
import time


def test(geodns_install=False, dnsresolver_install=True, port=3333, tmux=True):
    # start geodns instance(this is the main object to be used it is an
    # abstraction of the domain object)
    cuisine = j.tools.cuisine.local
    geodns = cuisine.geodns

    if dnsresolver_install:
        cuisine.core.run('pip install dnspython')
        # cuisine.core.file_download("http://www.dnspython.org/kits3/1.12.0/dnspython3-1.12.0.tar.gz",
        #                            to="$TMPDIR", overwrite=False, expand=True)
        # tarpath = cuisine.core.find("$TMPDIR", recursive=True, pattern="*dns*.gz", type='f')[0]
        # extracted = cuisine.core.file_expand(tarpath, "$TMPDIR")
        # cuisine.core.run("cd %s && python setup.py" % extracted)

    if geodns_install:
        geodns.install()

    geodns.start(port=port, tmux=tmux)

    # create a domain(the domain object is used as for specific trasactions
    # and is exposed for debugging purposes)
    domain_manager = j.sal.domainmanager.get(cuisine)
    domain = domain_manager.ensure_domain("gig.com", serial=3, ttl=600)
    print(domain._a_records)
    print(domain._cname_records)

    # add an A record
    domain_manager.add_record("gig.com", "www", "a", "123.45.123.1")

    # test_connection
    my_resolver = dns.resolver.Resolver()
    my_resolver.nameservers = ['127.0.0.1', '192.168.122.250']
    my_resolver.port = port
    answer1 = my_resolver.query('www.gig.com')
    time.sleep(5)
    if 1 == answer1.rrset[0].rdtype and "123.45.123.1" == answer1.rrset[0].to_text():
        print("add A record Test SUCCESS")
    else:
        print("failure")

    # add cname record
    domain_manager.add_record("gig.com", "grid", "cname", "www")

    # test connection
    answer2 = my_resolver.query("grid.gig.com", rdtype="cname")
    time.sleep(5)
    if 5 == answer2.rrset[0].rdtype and "www.gig.com." == answer2.rrset[0].to_text():
        print("add CNAME record Test SUCCESS")
    else:
        print("failure")
    print(str(type(answer1)) + str(type(answer2)))

    # get A record
    a_records = domain_manager.get_record("gig.com", "a")

    if a_records == {"www": [["123.45.123.1", 100]]}:
        print("get A record Test SUCCESS")

    # get cname record
    cname_records = domain_manager.get_record("gig.com", "cname")
    if cname_records == {"grid": "www"}:
        print("get cname cname_records")

    # delete A record
    domain_manager.del_record("gig.com", "a", "www", full=True)

    # test deltion
    try:
        answer1 = my_resolver.query('www.gig.com')
    except Exception as e:
        print(str(e))

    # delete cname record
    domain_manager.del_record("gig.com", "cname", "grid", full=True)

    # test deltion
    try:
        answer1 = my_resolver.query('grid.gig.com')
    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    test()

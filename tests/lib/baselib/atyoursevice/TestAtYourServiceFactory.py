"""
Tests for AtYourServiceFactory
"""
import unittest
from unittest import mock

class TestAtYourServiceFactory(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_factory(self):
        """
        Test creating new factory
        """
        with mock.patch("JumpScale.j") as j_mock:
            from JumpScale import j
            import JumpScale.baselib.atyourservice.AtYourServiceFactory
            JumpScale.baselib.atyourservice.AtYourServiceFactory.j = j
            from JumpScale.baselib.atyourservice.AtYourServiceFactory import AtYourServiceFactory
            ays_factory = AtYourServiceFactory()
            self.assertTrue(j.core.db.get.called)
            self.assertTrue(j.logger.get.called)


    def test_findAYSRepos(self):
        """
        Test finding ays repos
        """
        with mock.patch("JumpScale.j") as j_mock:
            with mock.patch("os.walk") as walk_mock:
                from JumpScale import j
                import JumpScale.baselib.atyourservice.AtYourServiceFactory
                JumpScale.baselib.atyourservice.AtYourServiceFactory.j = j
                from JumpScale.baselib.atyourservice.AtYourServiceFactory import AtYourServiceFactory
                ays_factory = AtYourServiceFactory()
                walk_mock.return_value = (('/opt/code/test1/test', [], ['.ays']), ('/opt/code/test2/test', [], ['.ays']), ('/opt/code/test3/test', [], []))
                actual_result = ays_factory.findAYSRepos()
                self.assertEquals(len(list(actual_result)), 2)


    def test_repos(self):
        """
        Test accessing the repos properties
        """
        with mock.patch("JumpScale.j") as j_mock:
            with mock.patch("JumpScale.baselib.atyourservice.AtYourServiceRepo.AtYourServiceRepo") as ays_repo_mock:
                from JumpScale import j
                from JumpScale.baselib.atyourservice.AtYourServiceRepo import AtYourServiceRepo
                import JumpScale.baselib.atyourservice.AtYourServiceFactory
                JumpScale.baselib.atyourservice.AtYourServiceFactory.j = j
                JumpScale.baselib.atyourservice.AtYourServiceFactory.AtYourServiceRepo = AtYourServiceRepo
                from JumpScale.baselib.atyourservice.AtYourServiceFactory import AtYourServiceFactory
                ays_factory = AtYourServiceFactory()
                j.atyourservice.findAYSRepos.return_value = ['/opt/code/test1/test', '/opt/code/test2/test']
                j.sal.fs.getBaseName.side_effect = ['test', 'test']
                actual_result = ays_factory.repos
                self.assertEquals(len(actual_result), 2)

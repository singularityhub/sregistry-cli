#!/usr/bin/python

# Copyright (C) 2019 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from sregistry.utils import get_installdir
import unittest
import tempfile
import shutil
import json
import os

print("############################################################ test_utils")

class TestUtils(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
       
    def test_write_read_files(self):
        '''test_write_read_files will test the functions write_file and read_file
        '''
        print("Testing utils.write_file...")
        from sregistry.utils import write_file
        tmpfile = tempfile.mkstemp()[1]
        os.remove(tmpfile)
        write_file(tmpfile,"hello!")
        self.assertTrue(os.path.exists(tmpfile))        

        print("Testing utils.read_file...")
        from sregistry.utils import read_file
        content = read_file(tmpfile)[0]
        self.assertEqual("hello!",content)

        from sregistry.utils import write_json
        print("Testing utils.write_json...")
        print("...Case 1: Providing bad json")
        bad_json = {"Wakkawakkawakka'}":[{True},"2",3]}
        tmpfile = tempfile.mkstemp()[1]
        os.remove(tmpfile)        
        with self.assertRaises(TypeError):
            write_json(bad_json,tmpfile)

        print("...Case 2: Providing good json")        
        good_json = {"Wakkawakkawakka":[True,"2",3]}
        tmpfile = tempfile.mkstemp()[1]
        os.remove(tmpfile)
        write_json(good_json,tmpfile)
        with open(tmpfile,'r') as filey:
            content = json.loads(filey.read())
        self.assertTrue(isinstance(content,dict))
        self.assertTrue("Wakkawakkawakka" in content)


    def test_check_install(self):
        '''check install is used to check if a particular software is installed.
        If no command is provided, singularity is assumed to be the test case'''
        print("Testing utils.check_install")
        from sregistry.utils import check_install
        is_installed = check_install()
        self.assertTrue(not is_installed) # Not installed Singularity yet
        is_not_installed = check_install('fakesoftwarename')
        self.assertTrue(not is_not_installed)


    def test_get_installdir(self):
        '''get install directory should return the base of where singularity
        is installed
        '''
        print("Testing utils.get_installdir")
        whereami = get_installdir()
        print(whereami)
        self.assertTrue(whereami.endswith('sregistry'))


    def test_remove_uri(self):
        print("Testing utils.remove_uri")
        from sregistry.utils import remove_uri
        self.assertEqual(remove_uri('docker://ubuntu'),'ubuntu')
        self.assertEqual(remove_uri('shub://vanessa/singularity-images'),'vanessa/singularity-images')


    def ubuntu_check(self, names):
        self.assertEqual(names['image'], 'ubuntu')
        self.assertEqual(names['collection'], 'library')
        self.assertEqual(names['registry'], None)
        self.assertEqual(names['tag'], 'latest')
        self.assertEqual(names['tag_uri'], 'library/ubuntu:latest')


    def test_parse_image_name(self):
        print("Testing utils.parse_image_name")
        from sregistry.utils import parse_image_name        
        names = parse_image_name('ubuntu')
        self.ubuntu_check(names)
        names = parse_image_name('ubuntu:latest')
        self.ubuntu_check(names)
        names = parse_image_name('library/ubuntu:latest')
        self.ubuntu_check(names)
        names = parse_image_name('library/ubuntu:latest@version')
        self.assertEqual(names['tag_uri'], 'library/ubuntu:latest@version')
        self.assertEqual(names['version'], 'version')
             
if __name__ == '__main__':
    unittest.main()

#!/usr/bin/python

# Copyright (C) 2017-2019 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import shutil
import pytest


def test_write_read_files(tmp_path):
    '''test_write_read_files will test the functions write_file and read_file
    '''
    print("Testing utils.write_file...")
    from sregistry.utils import write_file
    tmpfile = str(tmp_path / 'written_file.txt')
    assert not os.path.exists(tmpfile)
    write_file(tmpfile, "hello!")
    assert os.path.exists(tmpfile)

    print("Testing utils.read_file...")
    from sregistry.utils import read_file
    content = read_file(tmpfile)[0]
    assert content == "hello!"

def test_write_bad_json(tmp_path):
    from sregistry.utils import write_json
    bad_json = {"Wakkawakkawakka'}": [{True}, "2", 3]}
    tmpfile = str(tmp_path / 'json_file.txt')
    assert not os.path.exists(tmpfile)   
    with pytest.raises(TypeError):
        write_json(bad_json, tmpfile)

def test_write_json(tmp_path):
    import json
    from sregistry.utils import write_json, read_json
    good_json = {"Wakkawakkawakka": [True, "2", 3]}
    tmpfile = str(tmp_path / 'good_json_file.txt')
    assert not os.path.exists(tmpfile)
    write_json(good_json, tmpfile)
    with open(tmpfile, 'r') as f:
        content = json.loads(f.read())
    assert isinstance(content, dict)
    assert "Wakkawakkawakka" in content
    content = read_json(tmpfile)
    assert "Wakkawakkawakka" in content

def test_check_install():
    '''check install is used to check if a particular software is installed.
    If no command is provided, singularity is assumed to be the test case'''
    print("Testing utils.check_install")
    from sregistry.utils import check_install
    is_installed = check_install('echo')
    assert is_installed
    is_not_installed = check_install('fakesoftwarename')
    assert not is_not_installed

def test_get_installdir():
    '''get install directory should return the base of where sregistry
       is installed
    '''
    print("Testing utils.get_installdir")
    from sregistry.utils import get_installdir
    whereami = get_installdir()
    print(whereami)
    assert whereami.endswith('sregistry')


def test_remove_uri():
    print("Testing utils.remove_uri")
    from sregistry.utils import remove_uri
    assert remove_uri('docker://ubuntu') == 'ubuntu'
    assert remove_uri('shub://vanessa/singularity-images') == 'vanessa/singularity-images'
    assert remove_uri('vanessa/singularity-images') == 'vanessa/singularity-images'


def ubuntu_check(names, original):
    assert names['image'] == 'ubuntu'
    assert names['collection'] == 'library'
    assert names['registry'] is None
    assert names['version'] is None
    assert names['tag'] == 'latest'
    assert names['url'] == "library/ubuntu"
    assert names['uri'] == 'library/ubuntu:latest'
    assert names['original'] == original
    assert names['storage'] == 'library/ubuntu:latest.sif'

def test_parse_image_name():
    print("Testing utils.parse_image_name")
    from sregistry.utils import parse_image_name        
    names = parse_image_name('ubuntu')
    ubuntu_check(names, 'ubuntu')
    names = parse_image_name('ubuntu:latest')
    ubuntu_check(names, 'ubuntu:latest')
    names = parse_image_name('library/ubuntu:latest')
    ubuntu_check(names, 'library/ubuntu:latest')

    # Version should include same with version
    names = parse_image_name('library/ubuntu:latest@version')
    assert names['version'] == 'version'
    assert names['uri'] == "library/ubuntu:latest@version"
    assert names['image'] == 'ubuntu'
    assert names['collection'] == 'library'
    assert names['registry'] is None
    assert names['tag'] == 'latest'
    assert names['url'] == "library/ubuntu"
    assert names['uri'] == 'library/ubuntu:latest@version'
    assert names['original'] == 'library/ubuntu:latest@version'
    assert names['storage'] == 'library/ubuntu:latest@version.sif'


def test_recipe_tag():
    print("Testing utils.get_recipe_tag")
    from sregistry.utils import get_recipe_tag
    assert get_recipe_tag("Singularity") == "latest"
    assert get_recipe_tag("/path/to/Singularity") == "latest"
    assert get_recipe_tag("/path/to/Singularity.tag") == "tag"
    assert get_recipe_tag("/path/to/Dockerfile") is None


def test_run_command():
    print("Testing utils.run_command")
    from sregistry.utils import run_command
    result = run_command(["echo", "hello"])
    assert result['message'] == "hello\n"
    assert result['return_code'] == 0

def test_get_thumbnail():
    print("Testing utils.get_thumbnail")
    from sregistry.utils import get_thumbnail
    assert os.path.exists(get_thumbnail())
    assert get_thumbnail().endswith('robot.png')

def test_which():
    print("Testing utils.which")
    from sregistry.utils import which
    result = which('echo')
    assert result['message'].endswith('echo')
    assert result['return_code'] == 0
    result = which('singularityaaaa')
    assert result['message'] == ''
    assert result['return_code'] == 1


def test_get_file_hash():
    print("Testing utils.get_file_hash")
    from sregistry.utils import get_file_hash
    here = os.path.dirname(os.path.abspath(__file__))
    testdata = os.path.join(here, 'testdata', 'hashtest.txt')
    assert get_file_hash(testdata) == '6bb92117bded3da774363713657a629a9f38eac2e57cd47e1dcda21d3445c67d'
    assert get_file_hash(testdata, 'md5') == 'e5d376ca96081dd561ff303c3a631fd5'


def test_get_uri():
    print("Testing utils.get_uri")
    from sregistry.utils import get_uri
    assert get_uri('docker://ubuntu') == 'docker'
    assert 'hub' in get_uri('shub://vanessa/singularity-images')
    assert get_uri('notvalid://') is None
    assert get_uri('nowvalid://', validate=False) == 'nowvalid'


def test_get_userhome():
    print("Testing utils.get_userhome")
    from sregistry.utils import get_userhome
    home = get_userhome()
    assert home in os.environ.get('HOME')

def test_read_tar(tmp_path):
    print("Testing utils.extract_tar")
    from sregistry.utils import extract_tar
    here = os.path.dirname(os.path.abspath(__file__))
    testdata = os.path.join(here, 'testdata', 'hashtest.tar.gz')
    dirname = str(tmp_path / "destination")
    os.mkdir(dirname)
    extract_tar(testdata, dirname)
    assert os.path.exists(dirname)
    assert "hashtest.txt" in [os.path.basename(x) for x in os.listdir(dirname)]

def test_copyfile(tmp_path):
    print("Testing utils.copyfile")
    from sregistry.utils import copyfile, write_file
    original = str(tmp_path / 'location1.txt')
    dest = str(tmp_path / 'location2.txt')
    print(original)
    print(dest)
    write_file(original, "CONTENT IN FILE")
    copyfile(original, dest)
    assert os.path.exists(original)
    assert os.path.exists(dest)

def test_get_tmpdir_tmpfile():
    print("Testing utils.get_tmpdir, get_tmpfile")
    from sregistry.utils import get_tmpdir, get_tmpfile
    tmpdir = get_tmpdir()
    assert os.path.exists(tmpdir)
    assert os.path.basename(tmpdir).startswith('sregistry')
    shutil.rmtree(tmpdir)
    tmpdir = get_tmpdir(prefix='name')
    assert os.path.basename(tmpdir).startswith('name')
    shutil.rmtree(tmpdir)
    tmpfile = get_tmpfile()
    assert 'sregistry' in tmpfile
    os.remove(tmpfile)
    tmpfile = get_tmpfile(prefix="pancakes")
    assert 'pancakes' in tmpfile
    os.remove(tmpfile)

def test_mkdir_p(tmp_path):
    print("Testing utils.mkdir_p")
    from sregistry.utils import mkdir_p
    dirname = str(tmp_path / "input")
    result = os.path.join(dirname, "level1", "level2", "level3")
    mkdir_p(result)
    assert os.path.exists(result)   

def test_print_json():
    print("Testing utils.print_json")
    from sregistry.utils import print_json
    result = print_json({1:1})
    assert result == '{\n    "1": 1\n}'

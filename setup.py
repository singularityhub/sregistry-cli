from setuptools import setup, find_packages
import codecs
import os

################################################################################
# HELPER FUNCTIONS #############################################################
################################################################################

def get_lookup():
    '''get version by way of sregistry.version, returns a 
    lookup dictionary with several global variables without
    needing to import singularity
    '''
    lookup = dict()
    version_file = os.path.join('sregistry', 'version.py')
    with open(version_file) as filey:
        exec(filey.read(), lookup)
    return lookup


# Read in requirements
def get_reqs(lookup=None, key='INSTALL_REQUIRES'):
    '''get requirements, mean reading in requirements and versions from
    the lookup obtained with get_lookup'''

    if lookup == None:
        lookup = get_lookup()

    install_requires = []
    for module in lookup[key]:
        module_name = module[0]
        module_meta = module[1]
        if "exact_version" in module_meta:
            dependency = "%s==%s" %(module_name,module_meta['exact_version'])
        elif "min_version" in module_meta:
            if module_meta['min_version'] == None:
                dependency = module_name
            else:
                dependency = "%s>=%s" %(module_name,module_meta['min_version'])
        install_requires.append(dependency)
    return install_requires



# Make sure everything is relative to setup.py
install_path = os.path.dirname(os.path.abspath(__file__)) 
os.chdir(install_path)

# Get version information from the lookup
lookup = get_lookup()
VERSION = lookup['__version__']
NAME = lookup['NAME']
AUTHOR = lookup['AUTHOR']
AUTHOR_EMAIL = lookup['AUTHOR_EMAIL']
PACKAGE_URL = lookup['PACKAGE_URL']
KEYWORDS = lookup['KEYWORDS']
DESCRIPTION = lookup['DESCRIPTION']
LICENSE = lookup['LICENSE']
with open('README.md') as filey:
    LONG_DESCRIPTION = filey.read()

################################################################################
# MAIN #########################################################################
################################################################################

if __name__ == "__main__":

    INSTALL_REQUIRES = get_reqs(lookup)

    # These requirement DON'T include sqlalchemy, only client

    INSTALL_BASIC_ALL = get_reqs(lookup,'INSTALL_BASIC_ALL')
    AWS_BASIC = get_reqs(lookup,'INSTALL_BASIC_AWS')
    S3_BASIC = get_reqs(lookup,'INSTALL_BASIC_S3')
    DROPBOX_BASIC = get_reqs(lookup,'INSTALL_BASIC_DROPBOX')
    REGISTRY_BASIC = get_reqs(lookup,'INSTALL_BASIC_REGISTRY')
    GLOBUS_BASIC = get_reqs(lookup,'INSTALL_BASIC_GLOBUS')
    GOOGLE_STORAGE_BASIC = get_reqs(lookup,'INSTALL_BASIC_GOOGLE_STORAGE')
    GOOGLE_DRIVE_BASIC = get_reqs(lookup,'INSTALL_BASIC_GOOGLE_DRIVE')
    GOOGLE_BUILD_BASIC = get_reqs(lookup,'INSTALL_BASIC_GOOGLE_BUILD')
    GOOGLE_COMPUTE_BASIC = get_reqs(lookup,'INSTALL_BASIC_GOOGLE_COMPUTE')
    SWIFT_BASIC = get_reqs(lookup,'INSTALL_BASIC_SWIFT')
    TESTS_REQUIRES = get_reqs(lookup, 'TESTS_REQUIRES')

    # These requirement sets include sqlalchemy, for client+storage

    INSTALL_REQUIRES_ALL = get_reqs(lookup,'INSTALL_REQUIRES_ALL')
    AWS = get_reqs(lookup,'INSTALL_REQUIRES_AWS')
    S3 = get_reqs(lookup,'INSTALL_REQUIRES_S3')
    DROPBOX = get_reqs(lookup,'INSTALL_REQUIRES_DROPBOX')
    REGISTRY = get_reqs(lookup,'INSTALL_REQUIRES_REGISTRY')
    GLOBUS = get_reqs(lookup,'INSTALL_REQUIRES_GLOBUS')
    GOOGLE_STORAGE = get_reqs(lookup,'INSTALL_REQUIRES_GOOGLE_STORAGE')
    GOOGLE_DRIVE = get_reqs(lookup,'INSTALL_REQUIRES_GOOGLE_DRIVE')
    GOOGLE_COMPUTE = get_reqs(lookup,'INSTALL_REQUIRES_GOOGLE_COMPUTE')
    GOOGLE_BUILD = get_reqs(lookup,'INSTALL_REQUIRES_GOOGLE_BUILD')
    SWIFT = get_reqs(lookup,'INSTALL_REQUIRES_SWIFT')

    setup(name=NAME,
          version=VERSION,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          maintainer=AUTHOR,
          maintainer_email=AUTHOR_EMAIL,
          packages=find_packages(), 
          include_package_data=True,
          zip_safe=False,
          url=PACKAGE_URL,
          license=LICENSE,
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,
          long_description_content_type="text/markdown",
          keywords=KEYWORDS,
          setup_requires=["pytest-runner"],
          install_requires = INSTALL_REQUIRES,
          tests_require=TESTS_REQUIRES,
          extras_require={
              'all-basic': [INSTALL_BASIC_ALL],
              'aws-basic': [AWS_BASIC],
              'dropbox-basic': [DROPBOX_BASIC],
              'google-compute-basic': [GOOGLE_COMPUTE_BASIC],
              'google-storage-basic': [GOOGLE_STORAGE_BASIC],
              'google-drive-basic': [GOOGLE_DRIVE_BASIC],
              'google-build-basic': [GOOGLE_BUILD_BASIC],
              'globus-basic': [GLOBUS_BASIC],
              'registry-basic': [REGISTRY_BASIC],
              's3-basic': [S3_BASIC],
              'swift-basic': [SWIFT_BASIC],
              'all': [INSTALL_REQUIRES_ALL],
              'aws': [AWS],
              'dropbox': [DROPBOX],
              'google-compute': [GOOGLE_COMPUTE],
              'google-storage': [GOOGLE_STORAGE],
              'google-drive': [GOOGLE_DRIVE],
              'google-build': [GOOGLE_BUILD],
              'globus': [GLOBUS],
              'registry': [REGISTRY],
              's3': [S3],
              'swift': [SWIFT]

          },
          scripts=['sregistry/main/docker/blob2oci'],
          classifiers=[
              'Intended Audience :: Science/Research',
              'Intended Audience :: Developers',
              'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
              'Programming Language :: C',
              'Programming Language :: Python',
              'Topic :: Software Development',
              'Topic :: Scientific/Engineering',
              'Operating System :: Unix',
              'Programming Language :: Python :: 3.3',
          ],
          entry_points = {'console_scripts': ['sregistry=sregistry.client:main']})

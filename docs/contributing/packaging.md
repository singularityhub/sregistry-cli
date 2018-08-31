---
layout: default
title: Special Packaging
pdf: true
permalink: /contribute-packaging
toc: false
---

If you are in need of more than a [traditional install](/sregistry-cli/install)
You've come to the right place! Here are some helpers to do custom packaging 
for the Singularity Registry Client. We have provided basic scripts that are used
to generate files [in the release](https://github.com/singularityhub/sregistry-cli/tree/master/release)
directory.

## PyPi

The Python packaging index is what stores packages for installation with pip.
Whenever we have a new version, we run a simple command to generate and upload the
package, which you can see [here](https://github.com/singularityhub/sregistry-cli/tree/master/release/pypi.sh)

```
python setup.py sdist upload -r pypi
```

Credentials are stored in the `.pypirc` on the host HOME folder. If you were to just
run the `python setup.py sdist` command without the upload, it would just generate
a directory with your builds. Give it a try if you want to see it in action!

## RPM

Python setuptools actually has an easy way to build an rpm. In the example below,
we will walk through doing this in a clean environment (in a Docker container)
but you could imagine doing it on your host.

### Step 1. Prepare

Let's shell into a fresh centos container!

```bash
docker run --rm -it centos bash
```

Install some dependencies

```
yum update && yum install -y python-devel git python-setuptools
```

### Step 2. Download Source

Now clone the repository

```
git clone https://www.github.com/singularityhub/sregistry-cli.git /tmp/sregistry-cli
```

You can also download one of the [releases](https://pypi.org/project/sregistry/#history)
and you would need to install wget with `yum install -y wget`.

Go to where you cloned it, and then create the rpm. If you want to customize it,
there are some [useful docs here](https://docs.python.org/2.0/dist/creating-rpms.html).

### Step 3. Generate the RPM

The base command is this:

```
python setup.py bdist_rpm
```

And here are all the options you have to work with.

```
Options for 'bdist_rpm' command:
  --bdist-base         base directory for creating built distributions
  --rpm-base           base directory for creating RPMs (defaults to "rpm"
                       under --bdist-base; must be specified for RPM 2)
  --dist-dir (-d)      directory to put final RPM files in (and .spec files if
                       --spec-only)
  --python             path to Python interpreter to hard-code in the .spec
                       file (default: "python")
  --fix-python         hard-code the exact path to the current Python
                       interpreter in the .spec file
  --spec-only          only regenerate spec file
  --source-only        only generate source RPM
  --binary-only        only generate binary RPM
  --use-bzip2          use bzip2 instead of gzip to create source distribution
  --distribution-name  name of the (Linux) distribution to which this RPM
                       applies (*not* the name of the module distribution!)
  --group              package classification [default:
                       "Development/Libraries"]
  --release            RPM release number
  --serial             RPM serial number
  --vendor             RPM "vendor" (eg. "Joe Blow <joe@example.com>")
                       [default: maintainer or author from setup script]
  --packager           RPM packager (eg. "Jane Doe
                       <jane@example.net>")[default: vendor]
  --doc-files          list of documentation files (space or comma-separated)
  --changelog          RPM changelog
  --icon               name of icon file
  --provides           capabilities provided by this package
  --requires           capabilities required by this package
  --conflicts          capabilities which conflict with this package
  --build-requires     capabilities required to build this package
  --obsoletes          capabilities made obsolete by this package
  --no-autoreq         do not automatically calculate dependencies
  --keep-temp (-k)     don't clean up RPM build directory
  --no-keep-temp       clean up RPM build directory [default]
  --use-rpm-opt-flags  compile with RPM_OPT_FLAGS when building from source
                       RPM
  --no-rpm-opt-flags   do not pass any RPM CFLAGS to compiler
  --rpm3-mode          RPM 3 compatibility mode (default)
  --rpm2-mode          RPM 2 compatibility mode
  --prep-script        Specify a script for the PREP phase of RPM building
  --build-script       Specify a script for the BUILD phase of RPM building
  --pre-install        Specify a script for the pre-INSTALL phase of RPM
                       building
  --install-script     Specify a script for the INSTALL phase of RPM building
  --post-install       Specify a script for the post-INSTALL phase of RPM
                       building
  --pre-uninstall      Specify a script for the pre-UNINSTALL phase of RPM
                       building
  --post-uninstall     Specify a script for the post-UNINSTALL phase of RPM
                       building
  --clean-script       Specify a script for the CLEAN phase of RPM building
  --verify-script      Specify a script for the VERIFY phase of the RPM build
  --force-arch         Force an architecture onto the RPM build process
  --quiet (-q)         Run the INSTALL phase of RPM building in quiet mode

usage: setup.py [global_opts] cmd1 [cmd1_opts] [cmd2 [cmd2_opts] ...]
   or: setup.py --help [cmd1 cmd2 ...]
   or: setup.py --help-commands
   or: setup.py cmd --help

```

So, for example, here is what you could do. This would generate the files in the `dist`  folder.

```bash
python setup.py bdist_rpm --pre-install release/pre-install.sh

# Generate only the spec file
python setup.py bdist_rpm  --spec-only --pre-install release/pre-install.sh

# Change the distribution directory
python setup.py bdist_rpm --dist-dir release/rpm --pre-install release/pre-install.sh
```

### Step 4. Install the RPM

Now we are back in the centos container! Here is how you would install it.

```
rpm -i dist/sregistry-0.0.94-1.noarch.rpm
```

I'm not sure how/why to get the "pre-install" scripts running, but you would do
it manually like this to install dependencies:

```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
pip install -r requirements.txt
```
```
sregistry --version
# sregistry --version
WARNING Database disabled. Install sqlalchemy for full functionality
WARNING Singularity is not installed, function might be limited.
usage: sregistry [-h] [--debug] [--quiet]
                 {version,backend,shell,inspect,get,search,pull} ...
sregistry: error: too few arguments
```

And you can of course install `sqlalchemy` for full functionality.

```
pip install sqlalchemy
```

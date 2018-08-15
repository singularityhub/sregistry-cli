# https://www.ibm.com/developerworks/library/l-rpm1/
#
# spec file for package sregistry-cli
# credit for work goes to the amazing @griznog, John Hanks
#
Name:           sregistry-cli
Version:        0.0.92
Release:        0
Url:            http://www.github.com/singularityhub/sregistry-cli
Summary:        Command line tool for working with container storage
License:        LICENSE (FIXME:No SPDX)
Group:          Development/Languages/Python
Source:         https://files.pythonhosted.org/packages/source/s/sregistry/sregistry-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python-devel
%description
# Singularity Global Client
Hi Friends! Are your containers lonely? Singularity containers thrive in happiness when they are shared. This means that wherever you might have them in these cloudy places, they are easy to find and move around.
## What is this?
Singularity Global Client is an interface to interact with Singularity containers in many different storage locations. We are able to use modern APIs by way of providing and using the software within a Singularity container!
See our [installation guide](https://singularityhub.github.io/sregistry-cli/install) to get started.
## License
This code is licensed under the Affero GPL, version 3.0 or later [LICENSE](LICENSE).
%prep
%setup -q -n %{name}-%{version}
%build
python setup.py build
%install
python setup.py install --prefix=%{_prefix} --root=%{buildroot}
%clean
rm -rf %{buildroot}
%files
%defattr(-,root,root,-)
%{python_sitelib}/*
/usr/bin/sregistry
%changelog

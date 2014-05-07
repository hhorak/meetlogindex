Name:		meetlogindex
Version:	0.1
Release:	0.2%{?dist}
Summary:	Tool for automatical gathering of meetbot logs

Group:		Development/Tools
License:	MIT
URL:		/dev/null
Source0:	meetlogindex-%{version}.tar.gz

BuildRequires:	python-devel
Requires:	python

%description
Tool reads the configuration from Fedora wiki page, gathered new logs
from specified date and uploads the links to the new logs to the wiki,
into the specified pages.

%prep
%setup -q


%build
%{__python} setup.py build

%install
%{__python} setup.py install --skip-build --root %{buildroot}

%files
%doc README.md LICENSE dist-scripts/meetlogindex.cfg
%ghost %config(noreplace) %{_sysconfdir}/meetlogindex.cfg
%{_bindir}/%{name}
%{python_sitelib}/%{name}/*.py*
%{python_sitelib}/%{name}-%{version}-py?.?.egg-info


%changelog
* Wed May 07 2014 Honza Horak <hhorak@redhat.com> - 0.1-0.2
- Package the config file

* Sun Mar 02 2014 Honza Horak <hhorak@redhat.com> - 0.1-0.1
- Initial packaging


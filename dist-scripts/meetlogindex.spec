Name:		meetlogindex
Version:	0.1
Release:	0.1%{?dist}
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
mkdir -p %{buildroot}%{_sysconfdir}
install -m 0660 dist-scripts/meetlogindex.cfg %{buildroot}%{_sysconfdir}/%{name}.cfg

%files
%doc README.md LICENSE
%config(noreplace) %{_sysconfdir}/%{name}.cfg
%{_bindir}/%{name}
%{python_sitelib}/%{name}/*.py*
%{python_sitelib}/%{name}-%{version}-py?.?.egg-info


%changelog
* Sun Mar 02 2014 Honza Horak <hhorak@redhat.com> - 0.1-0.1
- Initial packaging


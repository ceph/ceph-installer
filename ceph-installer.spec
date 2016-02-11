%if "%{?scl}" == "ruby193"
    %global scl_prefix %{scl}-
    %global scl_ruby /usr/bin/ruby193-ruby
%else
    %global scl_ruby /usr/bin/ruby
%endif

Name:       ceph-installer
Version:    0.1.1
Release:    1%{?dist}
Summary:    HTTP API for a streamlined Ceph installer using Ansible
License:    GPLv3+
URL:        https://github.com/ceph/ceph-installer

#Source0:    https://github.com/ceph/%{name}/archive/%{version}.tar.gz
Source0:    %{name}-%{version}.tar.gz

BuildArch:  noarch

Requires:   %{?scl_prefix}foreman-installer >= 1.7.0
Requires:   takora

%description
This is a Ceph installer service that allows you to provision a cluster with an HTTP API
and a command line tool using Ansible playbooks.

%prep
%setup -q

%build
#replace shebangs for SCL
%if %{?scl:1}%{!?scl:0}
  sed -ri '1sX(/usr/bin/ruby|/usr/bin/env ruby)X%{scl_ruby}X' bin/ceph-installer
%endif

%install
#install -d -m0755 %{buildroot}%{_datadir}/foreman-installer
#cp -Rp hooks modules %{buildroot}%{_datadir}/foreman-installer
install -d -m0755 %{buildroot}%{_sbindir}
cp -p bin/* %{buildroot}%{_sbindir}
install -d -m0755 %{buildroot}%{_sysconfdir}/foreman/
cp -p config/* %{buildroot}%{_sysconfdir}/foreman

%files
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc README.md docs
%config %attr(600, root, root) %{_sysconfdir}/foreman/%{name}.yaml
%config(noreplace) %attr(600, root, root) %{_sysconfdir}/foreman/%{name}.answers.yaml
%{_sbindir}/ceph-installer
#%{_datadir}/foreman-installer/*

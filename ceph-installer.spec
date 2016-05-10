%global commitdate @COMMITDATE@
%global commit @COMMIT@
%global shortcommit %(c=%{commit}; echo ${c:0:7})

%define srcname ceph-installer

Name:           ceph-installer
Version:        @VERSION@
Release:        1.%{commitdate}git%{shortcommit}%{?dist}
Summary:        A service to provision Ceph clusters
License:        MIT
URL:            https://github.com/ceph/ceph-installer
Source0:        https://github.com/ceph/%{srcname}/archive/%{commit}/%{srcname}-%{version}-%{shortcommit}.tar.gz

BuildArch:      noarch

Requires: ansible
Requires: ceph-ansible >= 1.0.2
Requires: openssh
Requires: python-celery
Requires: python-gunicorn
Requires: python-notario >= 0.0.11
Requires: python-pecan >= 1
Requires: python-pecan-notario
Requires: python-requests
Requires: python-sqlalchemy
Requires: python-tambo
Requires: rabbitmq-server
Requires(pre):    shadow-utils
Requires(preun):  systemd
Requires(postun): systemd
Requires(post):   systemd

BuildRequires: systemd
BuildRequires: openssh
BuildRequires: python2-devel
BuildRequires: pytest
BuildRequires: python-celery
BuildRequires: python-docutils
BuildRequires: python-pecan >= 1
BuildRequires: python-pecan-notario
BuildRequires: python-sqlalchemy

%description
An HTTP API to provision and control the deployment process of Ceph clusters.

%prep
%autosetup -p1 -n %{srcname}-%{commit}

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

install -p -D -m 644 systemd/ceph-installer.service \
                     %{buildroot}%{_unitdir}/ceph-installer.service

install -p -D -m 644 systemd/ceph-installer-celery.service \
                     %{buildroot}%{_unitdir}/ceph-installer-celery.service

install -p -D -m 644 systemd/ceph-installer.sysconfig \
                     %{buildroot}%{_sysconfdir}/sysconfig/ceph-installer

install -p -D -m 644 systemd/80-ceph-installer.preset \
                     %{buildroot}%{_prefix}/lib/systemd/system-preset/80-ceph-installer.preset

install -p -D -m 644 firewalld/ceph-installer.xml \
                     %{buildroot}%{_prefix}/lib/firewalld/services/ceph-installer.xml

install -p -D -m 644 config/config.py \
                     %{buildroot}%{_sysconfdir}/ceph-installer/config.py

mkdir -p %{buildroot}%{_var}/lib/ceph-installer

mkdir -p %{buildroot}%{_mandir}/man8
rst2man docs/source/man/index.rst > \
        %{buildroot}%{_mandir}/man8/ceph-installer.8
gzip %{buildroot}%{_mandir}/man8/ceph-installer.8

%check
py.test-%{python2_version} -v ceph_installer/tests

%pre
getent group ceph-installer >/dev/null || groupadd -r ceph-installer
getent passwd ceph-installer >/dev/null || \
    useradd -r -g ceph-installer -d %{_var}/lib/ceph-installer \
    -s /bin/bash \
    -c "system account for ceph-installer REST API" ceph-installer
exit 0

%post
if [ $1 -eq 1 ] ; then
   su - ceph-installer -c "/bin/pecan populate /etc/ceph-installer/config.py"
fi
%systemd_post ceph-installer.service
%systemd_post ceph-installer-celery.service
systemctl start ceph-installer.service >/dev/null 2>&1 || :
test -f %{_bindir}/firewall-cmd && firewall-cmd --reload --quiet || true

%preun
%systemd_preun ceph-installer.service
%systemd_preun ceph-installer-celery.service

%postun
%systemd_postun_with_restart ceph-installer.service
%systemd_postun_with_restart ceph-installer-celery.service

%files
%doc README.rst
%license LICENSE
%{_bindir}/ceph-installer
%{python2_sitelib}/*
%{_mandir}/man8/ceph-installer.8*
%{_unitdir}/ceph-installer.service
%{_unitdir}/ceph-installer-celery.service
%{_prefix}/lib/systemd/system-preset/80-ceph-installer.preset
%config(noreplace) %{_sysconfdir}/sysconfig/ceph-installer
%config(noreplace) %{_sysconfdir}/ceph-installer/config.py
%exclude %{_sysconfdir}/ceph-installer/config.pyc
%exclude %{_sysconfdir}/ceph-installer/config.pyo
%dir %attr (-, ceph-installer, ceph-installer) %{_var}/lib/ceph-installer
%dir %attr(0750, root, root) %{_prefix}/lib/firewalld/services
%{_prefix}/lib/firewalld/services/ceph-installer.xml

%changelog

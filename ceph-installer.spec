%global commitdate @COMMITDATE@
%global commit @COMMIT@
%global shortcommit %(c=%{commit}; echo ${c:0:7})

%define srcname ceph-installer

%if 0%{?fedora} || 0%{?rhel}
# get selinux policy version
%{!?_selinux_policy_version: %global _selinux_policy_version %(sed -e 's,.*selinux-policy-\\([^/]*\\)/.*,\\1,' /usr/share/selinux/devel/policyhelp 2>/dev/null || echo 0.0.0)}
%global selinux_types %(%{__awk} '/^#[[:space:]]*SELINUXTYPE=/,/^[^#]/ { if ($3 == "-") printf "%s ", $2 }' /etc/selinux/config 2>/dev/null)
%global selinux_variants %([ -z "%{selinux_types}" ] && echo mls targeted || echo %{selinux_types})
%endif

Name:           ceph-installer
Version:        @VERSION@
Release:        1.%{commitdate}git%{shortcommit}%{?dist}
Summary:        A service to provision Ceph clusters
License:        MIT
URL:            https://github.com/ceph/ceph-installer
Source0:        https://github.com/ceph/%{srcname}/archive/%{commit}/%{srcname}-%{version}-%{shortcommit}.tar.gz

BuildArch:      noarch

Requires: ansible < 2
Requires: ceph-ansible >= 1.0.5
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

%if 0%{?rhel} || 0%{?fedora}
# SELinux deps
Requires:       policycoreutils, libselinux-utils
Requires(post): selinux-policy >= %{_selinux_policy_version}, policycoreutils
Requires(postun): policycoreutils
BuildRequires:  checkpolicy
BuildRequires:  selinux-policy-devel
BuildRequires:  /usr/share/selinux/devel/policyhelp
BuildRequires:  hardlink
%endif

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
%if 0%{?fedora} || 0%{?rhel}
cd selinux
for selinuxvariant in %{selinux_variants}
do
make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile
mv ceph-installer.pp ceph-installer.pp.${selinuxvariant}
make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile clean
done
cd -
%endif

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
%if 0%{?fedora} || 0%{?rhel}
# Install SELinux policy
for selinuxvariant in %{selinux_variants}
do
    install -d %{buildroot}%{_datadir}/selinux/${selinuxvariant}
    install -p -m 644 selinux/ceph-installer.pp.${selinuxvariant} \
    %{buildroot}%{_datadir}/selinux/${selinuxvariant}/ceph-installer.pp
done
/usr/sbin/hardlink -cv %{buildroot}%{_datadir}/selinux
%endif

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
%if 0%{?fedora} || 0%{?rhel}
ceph_installer_selinux()
{
    # Set some SELinux booleans
    #setsebool httpd_can_network_connect=on
    #setsebool httpd_can_network_connect_db=on

    # Load the policy
    for selinuxvariant in %{selinux_variants}
    do
        /usr/sbin/semodule -s ${selinuxvariant} -i \
        %{_datadir}/selinux/${selinuxvariant}/ceph-installer.pp &> /dev/null || :
    done
    # Relabel files
    /sbin/restorecon -Rv \
        %{_bindir}/ceph-installer{,-gunicorn,-celery} \
        %{_prefix}/lib/systemd/system-preset/80-ceph-installer.preset \
        %{_prefix}/lib/systemd/system/ceph-installer{,-celery}.service \
        %{_var}/lib/ceph-installer &> /dev/null || :
}

ceph_installer_selinux
%endif
if [ $1 -eq 1 ] ; then
   su - ceph-installer -c "/bin/pecan populate /etc/ceph-installer/config.py" &> /dev/null
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
%if 0%{?fedora} || 0%{?rhel}
if [ $1 == 0 ] ; then
    for selinuxvariant in %{selinux_variants}
    do
        /usr/sbin/semodule -s ${selinuxvariant} -r ceph-installer &> /dev/null || :
    done
fi
%endif

%files
%doc README.rst
%license LICENSE
%{_bindir}/ceph-installer
%{_bindir}/ceph-installer-celery
%{_bindir}/ceph-installer-gunicorn
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
%if 0%{?fedora} || 0%{?rhel}
%doc selinux/*
%{_datadir}/selinux/*/ceph-installer.pp
%endif

%changelog

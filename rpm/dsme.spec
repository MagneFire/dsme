Name:       dsme
Summary:    Device State Management Entity
Version:    0.79.5
Release:    0
Group:      System/System Control
License:    LGPLv2+
URL:        https://github.com/nemomobile/dsme
Source0:    %{name}-%{version}.tar.gz
Source1:    dsme.service
Source2:    dsme-rpmlintrc
Requires:   systemd
Requires:   ngfd
Requires:   libdsme >= 0.66.0
Requires(preun): systemd
Requires(post): systemd
Requires(postun): systemd
BuildRequires:  pkgconfig(glib-2.0) >= 2.32.0
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(dbus-glib-1)
BuildRequires:  pkgconfig(libiphb) >= 1.2.0
BuildRequires:  pkgconfig(dsme) >= 0.66.0
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(mce) >= 1.12.3
BuildRequires:  pkgconfig(libngf0) >= 0.24
BuildRequires:  python
BuildRequires:  autoconf
BuildRequires:  libtool
BuildRequires:  automake
BuildRequires:  pkgconfig(libcryptsetup)

%description
Device State Management Entity (with debug symbols). This package contains the Device State Management Entity which provides state management features such as service monitoring, process watchdog and inactivity tracking.

%package tests
Summary:    DSME test cases
Group:      Development/System
BuildArch:  noarch
Requires:   %{name} = %{version}-%{release}
Requires:   dbus

%description tests
Test cases and xml test description for DSME

%prep
%setup -q -n %{name}-%{version}

%build
unset LD_AS_NEEDED
./verify_version.sh
test -e Makefile || ./autogen.sh
test -e Makefile || (%configure --disable-static \
    --disable-poweron-timer \
    --disable-upstart \
    --enable-runlevel \
    --enable-systemd \
    --enable-pwrkeymonitor \
    --disable-validatorlistener \
    --enable-abootsettings)

make %{?_smp_mflags}

%install
rm -rf %{buildroot}
%make_install

install -d %{buildroot}%{_sysconfdir}/dsme/
install -D -m 644 reboot-via-dsme.sh %{buildroot}/etc/profile.d/reboot-via-dsme.sh
install -D -m 644 %{SOURCE1} %{buildroot}/lib/systemd/system/%{name}.service
install -d %{buildroot}/lib/systemd/system/multi-user.target.wants/
ln -s ../%{name}.service %{buildroot}/lib/systemd/system/multi-user.target.wants/%{name}.service
install -d %{buildroot}/var/lib/dsme
[ ! -f %{buildroot}/var/lib/dsme/alarm_queue_status ] && echo 0 > %{buildroot}/var/lib/dsme/alarm_queue_status

%preun
if [ "$1" -eq 0 ]; then
  systemctl stop %{name}.service || :
fi

%post
systemctl daemon-reload || :
systemctl reload-or-try-restart %{name}.service || :

%postun
systemctl daemon-reload || :

%files
%defattr(-,root,root,-)
%dir %{_libdir}/dsme
%{_libdir}/dsme/*
%attr(755,root,root)%{_sbindir}/*
%dir %{_sysconfdir}/dsme
%config %{_sysconfdir}/dbus-1/system.d/dsme.conf
%license debian/copyright COPYING
/lib/systemd/system/%{name}.service
/lib/systemd/system/multi-user.target.wants/%{name}.service
/var/lib/dsme
%config(noreplace) /var/lib/dsme/alarm_queue_status
/etc/profile.d/reboot-via-dsme.sh

%files tests
%defattr(-,root,root,-)
/opt/tests/dsme-tests

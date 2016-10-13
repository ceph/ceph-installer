# Makefile for constructing RPMs.
# Try "make" (for SRPMS) or "make rpm"

NAME = ceph-installer
VERSION := $(shell PYTHONPATH=. python -c \
             'import ceph_installer; print ceph_installer.__version__')
COMMIT := $(shell git rev-parse HEAD)
SHORTCOMMIT := $(shell echo $(COMMIT) | cut -c1-7)
RELEASE := $(shell git describe --match 'v*' \
             | sed 's/^v//' \
             | sed 's/^[^-]*-//' \
             | sed 's/-/./')
ifeq ($(VERSION),$(RELEASE))
  RELEASE = 0
endif
NVR := $(NAME)-$(VERSION)-$(RELEASE).el7

all: srpm

# Testing only
echo:
	echo COMMIT $(COMMIT)
	echo VERSION $(VERSION)
	echo RELEASE $(RELEASE)
	echo NVR $(NVR)

clean:
	rm -rf dist/
	rm -rf ceph-installer-$(VERSION)-$(SHORTCOMMIT).tar.gz
	rm -rf $(NVR).src.rpm

dist:
	python setup.py sdist \
	  && mv dist/ceph-installer-$(VERSION).tar.gz \
          ceph-installer-$(VERSION)-$(SHORTCOMMIT).tar.gz

spec:
	sed ceph-installer.spec.in \
	  -e 's/@COMMIT@/$(COMMIT)/' \
	  -e 's/@VERSION@/$(VERSION)/' \
	  -e 's/@RELEASE@/$(RELEASE)/' \
	  > ceph-installer.spec

srpm: dist spec
	fedpkg --dist epel7 srpm

rpm: dist srpm
	mock -r ktdreyer-ceph-installer rebuild $(NVR).src.rpm

.PHONY: dist rpm srpm

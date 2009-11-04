# Name
NAME=gmonitor

# Version
VERSION=0.1.0

# Plugin name, must match X-KDE-PluginInfo-Name
PLUGIN_NAME=pysnippet-${NAME}

# The package filename
PLASMOID_PKG=${NAME}-${VERSION}.plasmoid

# Python sources to include in the package
PY_SRC := $(shell find . -name *.py)

# All files that should be included in the .plasmoid zip
FILES := metadata.desktop ${PY_SRC}

.PHONY: uninstall, view, clean

all: ${PLASMOID_PKG}

install: ${PLASMOID_PKG}
	plasmapkg -i $?

uninstall:
	plasmapkg -r ${PLASMOID_PKG}

update: ${PLASMOID_PKG}
	plasmapkg -u $?

view:
	plasmoidviewer ${CURDIR}

clean:
	rm -f ${PLASMOID_PKG}

${PLASMOID_PKG}: ${FILES}
	zip -r $@ $?

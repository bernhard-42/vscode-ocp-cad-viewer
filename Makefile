.PHONY: clean_notebooks wheel install tests check_version dist check_dist upload_test upload \
		bump release create-release docker docker_upload dist tests reload reload-tcv \
		reload-core prepare

PYCACHE := $(shell find . -name '__pycache__')
EGGS := $(wildcard *.egg-info)
CURRENT_VERSION := $(shell awk '/current_version =/ {print substr($$3, 2, length($$3)-2)}' pyproject.toml)

# https://github.com/jupyter/nbconvert/issues/637

clean:
	@echo "=> Cleaning"
	@rm -fr build dist $(EGGS) $(PYCACHE)

prepare: clean
	git add .
	git status
	git commit -m "cleanup before release"

# Version commands
bump:
	@echo Current version: $(CURRENT_VERSION)
ifdef part
	bump-my-version bump $(part) --allow-dirty && grep current pyproject.toml
else ifdef version
	bump-my-version bump --allow-dirty --new-version $(version) && grep current pyproject.toml
else
	@echo "Provide part=major|minor|patch|release|build and optionally version=x.y.z..."
	exit 1
endif

dist: clean
	@echo Version: $(CURRENT_VERSION)
	# Nothing to copy: the page is read from resources/ by the extension and
	# the JavaScript from node_modules, both at runtime. The copies that used
	# to be made here were for the standalone, which is `ocp_viewer` now.

	@python -m build -n
	vsce package --yarn
	@ls -l dist/


vsix: dist
	@echo Version: $(CURRENT_VERSION)
	vsce package --yarn
	@ls -l *.vsix

install-vsix: vsix
	code --uninstall-extension bernhard-42.ocp-cad-viewer
	code --install-extension ocp-cad-viewer-$(CURRENT_VERSION).vsix
	
release:
	git add .
	git status
	git diff-index --quiet HEAD || git commit -m "Latest release: $(CURRENT_VERSION)"
	git tag -a v$(CURRENT_VERSION) -m "Latest release: $(CURRENT_VERSION)"
	
create-release:
	@git push
	@git push --tags
	@gh release create v$(CURRENT_VERSION) \
		ocp-cad-viewer-$(CURRENT_VERSION).vsix \
		dist/ocp_vscode-$(CURRENT_VERSION)-py3-none-any.whl \
		dist/ocp_vscode-$(CURRENT_VERSION).tar.gz \
		--title "ocp_vscode-$(CURRENT_VERSION)" \
		--notes "v$(CURRENT_VERSION)" \
		--target main

# The two tarball dependencies. `yarn cache clean` is not optional: yarn caches a
# file dependency by name and version, so a rebuilt tarball whose version has not
# moved installs the stale copy from the cache instead.

reload-tcv:
	yarn remove three-cad-viewer
	yarn cache clean
	yarn add ./$(shell ls three-cad-viewer-v*.tgz | sort -V | tail -n 1)

reload-core:
	yarn remove ocp-viewer-core
	yarn cache clean
	yarn add ./$(shell ls ocp-viewer-core-v*.tgz | sort -V | tail -n 1)

reload: reload-tcv install-vsix
	@echo done

# install: dist
# 	@echo "=> Installing jupyter_cadquery"
# 	@pip install --upgrade .

# check_dist:
# 	@twine check dist/*

tests:
	OCP_VSCODE_PYTEST=1 OCP_VIEWER_PYTEST=1 pytest -s -W ignore tests/ 

upload:
	@twine upload dist/*

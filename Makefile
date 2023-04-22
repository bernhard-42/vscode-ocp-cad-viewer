.PHONY: clean_notebooks wheel install tests check_version dist check_dist upload_test upload bump release create-release docker docker_upload dist

PYCACHE := $(shell find . -name '__pycache__')
EGGS := $(wildcard *.egg-info)
CURRENT_VERSION := $(shell awk '/version/ {print substr($$2, 2, length($$2)-3)}' setup.py)

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

ifdef part
ifdef version
	bumpversion --allow-dirty --new-version $(version) $(part) && grep current setup.cfg
else
	bumpversion --allow-dirty $(part) && grep current setup.cfg
endif
else
	@echo "Provide part=major|minor|patch|release|build and optionally version=x.y.z..."
	exit 1
endif

dist:
	@echo Version: $(CURRENT_VERSION)
	@python setup.py sdist bdist_wheel
	vsce package --yarn
	@ls -l dist/


vsix:
	@echo Version: $(CURRENT_VERSION)
	vsce package --yarn
	@ls -l *.vsix

release:
	git add .
	git status
	git diff-index --quiet HEAD || git commit -m "Latest release: $(CURRENT_VERSION)"
	git tag -a v$(CURRENT_VERSION) -m "Latest release: $(CURRENT_VERSION)"
	
create-release:
	@git push
	@git push --tags
	@github-release release -u bernhard-42 -r vscode-ocp-cad-viewer -t v$(CURRENT_VERSION) -n ocp-cad-viewer-$(CURRENT_VERSION)
	@sleep 2
	@github-release upload  -u bernhard-42 -r vscode-ocp-cad-viewer -t v$(CURRENT_VERSION) -n ocp-cad-viewer-$(CURRENT_VERSION).vsix -f ocp-cad-viewer-$(CURRENT_VERSION).vsix
	@github-release upload  -u bernhard-42 -r vscode-ocp-cad-viewer -t v$(CURRENT_VERSION) -n ocp_vscode-$(CURRENT_VERSION)-py3-none-any.whl -f dist/ocp_vscode-$(CURRENT_VERSION)-py3-none-any.whl 
	@github-release upload  -u bernhard-42 -r vscode-ocp-cad-viewer -t v$(CURRENT_VERSION) -n ocp_vscode-$(CURRENT_VERSION).tar.gz -f dist/ocp_vscode-$(CURRENT_VERSION).tar.gz 

# install: dist
# 	@echo "=> Installing jupyter_cadquery"
# 	@pip install --upgrade .

# check_dist:
# 	@twine check dist/*

upload:
	@twine upload dist/*

.PHONY: clean_notebooks wheel install tests check_version dist check_dist upload_test upload bump release create-release docker docker_upload dist tests

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

dist:
	@echo Version: $(CURRENT_VERSION)
	@echo "Copying html, css and js file to standalone locations"
	@cp resources/viewer.html ocp_vscode/templates
	@cp node_modules/three-cad-viewer/dist/three-cad-viewer.esm.js ocp_vscode/static/js
	@cp node_modules/three-cad-viewer/dist/three-cad-viewer.css ocp_vscode/static/css
	
	@python -m build -n
	vsce package --yarn
	@ls -l dist/


vsix:
	@echo Version: $(CURRENT_VERSION)
	vsce package --yarn
	@ls -l *.vsix

install-vsix:
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

tests:
	NATIVE_TESSELLATOR=0 OCP_VSCODE_PYTEST=1 pytest -v -s pytests/

native_tests:
	NATIVE_TESSELLATOR=1 OCP_VSCODE_PYTEST=1 pytest -v -s pytests/

upload:
	@twine upload dist/*

# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

serve:
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) --watch ../nwb_linkml/src/nwb_linkml --watch ../nwb_schema_language/src/nwb_schema_language

serve_fast:
	sphinx-autobuild -a "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) --watch ../nwb_linkml/src/nwb_linkml --watch ../nwb_schema_language/src/nwb_schema_language



models:
	export SPHINX_APIDOC_OPTIONS="members,show-inheritance,exclude-members ConfiguredBaseClass"
	rm ./api/models/*
	sphinx-apidoc -e --force \
		--templatedir=./_templates \
		--implicit-namespaces \
		-o ./api/models/ \
		../nwb_linkml/src/nwb_linkml/ \
		"*[!models]*"

	find ./api/models/ -type f ! -name '*models*' -delete
	# fix names so they're not so dang long
	find ./api/models -type f -name '*.rst' -exec gsed -i -e 's/^.*\.\(.*\) package/\1 /g' {} \;
	find ./api/models -type f -name '*.rst' -exec gsed -i -e 's/^.*\.\(.*\) module/\1 /g' {} \;


# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)


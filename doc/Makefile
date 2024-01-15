# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = -j auto -W --color
SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

.install-deps:
	@pip freeze | grep -q "sphinx-autoapi @ git+https://github.com/ansys/sphinx-autoapi" && is_custom_sphinx_autoapi_installed="yes" || is_custom_sphinx_autoapi_installed="no"
	@if [ "$$is_custom_sphinx_autoapi_installed" != "yes" ]; then \
		pip uninstall --yes sphinx-autoapi; \
		pip install "sphinx-autoapi @ git+https://github.com/ansys/sphinx-autoapi@feat/single-page-stable"; \
	fi

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: .install-deps Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Customized clean due to examples gallery
clean: .install-deps
	rm -rf $(BUILDDIR)/*
	find . -type d -name "api" -exec rm -rf {} +

# Create PDF
pdf: .install-deps
	@$(SPHINXBUILD) -M latex "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	cd $(BUILDDIR)/latex && latexmk -r latexmkrc -pdf *.tex -interaction=nonstopmode || true
	(test -f $(BUILDDIR)/latex/*.pdf && echo pdf exists) || exit 1

# Build HTML files and generate examples as .py files
html: .install-deps
	@$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	cd $(BUILDDIR)/html/examples
	for d in */ ; do
		cd $d
		for f in ./*.ipynb; do
			jupytext --to py $f
		done
		cd -
	done

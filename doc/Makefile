# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = -j auto -W --color
SPHINXBUILD   = sphinx-build
APIDIR        = api
SOURCEDIR     = source
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Customized clean due to examples gallery
clean:
	rm -rf $(BUILDDIR)/*
	find . -type d -name $(APIDIR) -exec rm -rf {} +

# Create PDF
pdf:
	@$(SPHINXBUILD) -M latex "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	cd $(BUILDDIR)/latex && latexmk -r latexmkrc -pdf *.tex -interaction=nonstopmode || true
	(test -f $(BUILDDIR)/latex/*.pdf && echo pdf exists) || exit 1

# Build HTML files and generate examples as .py files
html:
	@$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	# TODO: migrate this logic as a sphinx-hook declared in the conf.py file
	cd $(BUILDDIR)/html/examples
	for d in */ ; do
		cd $d
		for f in ./*.ipynb; do
			jupytext --to py $f
		done
		cd -
	done

# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = -j 1 -W --color
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
	cd $(BUILDDIR)/latex && for file in *.tex; do lualatex --interaction=nonstopmode "$$file"; done
	(test -f $(BUILDDIR)/latex/ansys-geometry-core.pdf && echo pdf exists) || exit 1

# Build HTML files and generate examples as .py files
html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Linkcheck
linkcheck:
	@$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Single example target
single-example:
	@if [ -z "$(example)" ]; then \
		echo "No example specified."; \
		echo "Usage --> make single-example example=examples/01_getting_started/01_math.mystnb"; \
		exit 1; \
	fi
	@echo "Building single example --> $(example)"
	@BUILD_API=false BUILD_CHEATSHEET=false $(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" -j 1 $(O) -D "include_patterns=index.rst,examples.rst,$(example)"

# Basic docs target (skip examples and cheatsheet)
basic-docs:
	@echo "Building basic documentation (skipping examples and cheatsheet)..."
	@BUILD_API=true BUILD_EXAMPLES=false BUILD_CHEATSHEET=false $(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

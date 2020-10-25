# White Paper

This folder contains the LaTeX for the white paper that accompanies the mRDPf Python module.

## IEEE Template

The LaTeX is based on the [IEEE Manuscript Template for Conference Proceedings](https://www.ieee.org/conferences/publishing/templates.html). IEEE templates are also available on [Overleaf](https://www.overleaf.com/gallery/tagged/ieee-official).

The following modifications have been made to the provided template, distributed under the LaTeX Project Public License (LPPL) (http://www.latex-project.org/) version 1.3:
- IEEEtran_HOWTO.pdf: removed
- bare_adv.tex: removed
- bare_conf.tex: removed
- bare_jrnl.tex: removed
- bare_conf_compsoc.tex: removed
- bare_jrnl_compsoc.tex: removed

To retrieve an unmodified copy of the data above, please see the IEEE and Overleaf sources above.

## Compiling

To compile the TeX file to a PDF, please execute the following commands:
```
pdflatex mrdpf_whitepaper.tex
bibtex mrdpf_whitepaper.aux
pdflatex mrdpf_whitepaper.tex
pdflatex mrdpf_whitepaper.tex
```

Alternatively, you can execute the `make.bat` helper script on Windows.

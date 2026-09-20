# 强制 latexmk 使用 xelatex（cumcmthesis.cls 要求 xelatex）
# 即使 VSCode LaTeX Workshop 在命令行传 -pdf，这里覆盖 $pdf_mode 和 $pdflatex 让其走 xelatex。
$pdf_mode  = 5;
$pdflatex  = 'xelatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';
$lualatex  = 'xelatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';
$xelatex   = 'xelatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';

# 所有产物放进 out/，让 latexmk 自动同步 log/aux 路径
$out_dir   = 'out';
$aux_dir   = 'out';

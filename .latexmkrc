# latexmk 的 PDF 模式 5 使用 XeLaTeX；模式 4 才使用 LuaLaTeX。
$pdf_mode = 5;
$lualatex = 'lualatex -synctex=1 -shell-restricted -interaction=nonstopmode -halt-on-error -file-line-error %O %S';
$xelatex = 'xelatex -synctex=1 -shell-restricted -interaction=nonstopmode -halt-on-error -file-line-error %O %S';
$max_repeat = 8;
# 每个页码保留独立的术语锚点，不合并为自动页码区间。
use File::Basename qw(dirname);
use Cwd qw(abs_path);
my $my_root = dirname(abs_path(__FILE__));
$do_cd = 1;
@default_files = ('book/textbook/textbook.tex');
# 每次构建一个入口，按源码位置选择输出目录，避免不同章节互相覆盖。
my %my_output_dirs;
my $my_chapter_name;
my @my_sources = grep { /\.tex\z/ && !/\A-/ } @ARGV;
@my_sources = @default_files unless @my_sources;
for my $my_source (@my_sources) {
    my $my_source_path = abs_path($my_source);
    next unless defined $my_source_path;
    if ($my_source_path eq "$my_root/book/textbook/textbook.tex") {
        $my_output_dirs{"$my_root/build/textbook"} = 1;
    } elsif ($my_source_path eq "$my_root/book/workbook/workbook.tex") {
        $my_output_dirs{"$my_root/build/workbook"} = 1;
    } elsif ($my_source_path =~ /\A\Q$my_root\E\/book\/textbook\/chapters\/([^\/]+)\.tex\z/) {
        $my_output_dirs{"$my_root/build/chapters/$1"} = 1;
        $my_chapter_name = $1;
    }
}
die "Build each textbook, workbook or chapter entry separately.\n"
    if keys(%my_output_dirs) > 1;
($out_dir) = keys %my_output_dirs if %my_output_dirs;
if (defined $my_chapter_name) {
    # subfiles loads the main preamble while its class is still initializing.
    # Load fontspec before the class so the shared font probe can run safely.
    $pre_tex_code = '\RequirePackage{fontspec}';
    $lualatex = 'lualatex -synctex=1 -shell-restricted -interaction=nonstopmode -halt-on-error -file-line-error -jobname=' . $my_chapter_name . ' %O %P';
    $xelatex = 'xelatex -synctex=1 -shell-restricted -interaction=nonstopmode -halt-on-error -file-line-error -jobname=' . $my_chapter_name . ' %O %P';
}
my $my_term_index_style = $my_root . '/book/term-index.ist';
$makeindex = 'makeindex -r -s "' . $my_term_index_style . '" %O -o %D %S';

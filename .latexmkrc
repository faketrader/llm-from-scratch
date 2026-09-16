$pdf_mode = 5;
$lualatex = 'lualatex -synctex=1 -shell-restricted -interaction=nonstopmode -halt-on-error -file-line-error %O %S';
$xelatex = 'xelatex -synctex=1 -shell-restricted -interaction=nonstopmode -halt-on-error -file-line-error %O %S';
$max_repeat = 5;
# 每个页码保留独立的术语锚点，不合并为自动页码区间。
use File::Basename qw(dirname);
use Cwd qw(abs_path);
my $lfs_root = dirname(abs_path(__FILE__));
$do_cd = 1;
@default_files = ('book/textbook/textbook.tex');
# 每次构建一个入口，按源码位置选择输出目录，避免不同章节互相覆盖。
my %lfs_output_dirs;
my @lfs_sources = grep { /\.tex\z/ && !/\A-/ } @ARGV;
@lfs_sources = @default_files unless @lfs_sources;
for my $lfs_source (@lfs_sources) {
    my $lfs_source_path = abs_path($lfs_source);
    next unless defined $lfs_source_path;
    if ($lfs_source_path eq "$lfs_root/book/textbook/textbook.tex") {
        $lfs_output_dirs{"$lfs_root/build/textbook"} = 1;
    } elsif ($lfs_source_path eq "$lfs_root/book/workbook/workbook.tex") {
        $lfs_output_dirs{"$lfs_root/build/workbook"} = 1;
    } elsif ($lfs_source_path =~ /\A\Q$lfs_root\E\/book\/textbook\/chapters\/([^\/]+)\.tex\z/) {
        $lfs_output_dirs{"$lfs_root/build/chapters/$1"} = 1;
    }
}
die "Build each textbook, workbook or chapter entry separately.\n"
    if keys(%lfs_output_dirs) > 1;
($out_dir) = keys %lfs_output_dirs if %lfs_output_dirs;
my $lfs_cn_index_style = $lfs_root . '/book/term-index-cn.ist';
$makeindex = 'makeindex -r -s "' . $lfs_cn_index_style . '" %O -o %D %S';

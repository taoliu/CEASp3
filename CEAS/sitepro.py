import argparse


def get_parser():
    usage = "sitepro -- Average profile around given genomic sites"
    parser = argparse.ArgumentParser(
        description=usage,
        add_help=False,
    )
    parser.add_argument(
        "-h", "--help", action="help", help="Show this help message and exit."
    )
    parser.add_argument(
        "-f",
        "--format",
        dest="format",
        choices=["bigwig", "wig"],
        default="bigwig",
        help="Input file format (bigwig or wig).",
    )
    parser.add_argument(
        "-w",
        "--wig",
        "--bw",
        dest="wig",
        action="append",
        help=(
            "input wig or bigwig file. Multiple files can be given individually"
            " (eg -w WIG1 -w WIG2). WARNING! multiple wig and bed files are not"
            " allowed."
        ),
    )
    parser.add_argument(
        "-b",
        "--bed",
        dest="bed",
        action="append",
        help=(
            "BED file of regions of interest. Multiple files can be given"
            " individually (eg -b BED1 -b BED2). WARNING! multiple wig and bed"
            " files are not allowed."
        ),
    )
    parser.add_argument(
        "--span",
        dest="span",
        type=int,
        default=1000,
        help="Span from the center of each BED region in both directions(+/-)",
    )
    parser.add_argument(
        "--pf-res",
        dest="pf_res",
        type=int,
        default=50,
        help="Profiling resolution",
    )
    parser.add_argument(
        "--dir",
        action="store_true",
        dest="dir",
        help="If set, the direction (+/-) is considered in profiling.",
        default=False,
    )
    parser.add_argument(
        "--dump",
        action="store_true",
        dest="dump",
        help="If set, profiles are dumped as a TXT file",
        default=False,
    )
    parser.add_argument(
        "--confid",
        action="store_true",
        dest="confidence",
        help="If set, it will draw 95% confidence interval for each step.",
        default=False,
    )
    parser.add_argument(
        "--name",
        dest="name",
        help="Name of this run. If not given, the body of the bed file name will be used,",
    )
    parser.add_argument(
        "-l",
        "--label",
        dest="label",
        action="append",
        help=(
            "Labels of the wig/bigwig files. If given, they are used as the"
            " legends of the plot and in naming the TXT files of profile dumps;"
            " otherwise, the file names will be used as the labels. Multiple"
            " labels can be given individually. WARNING! The number and order of"
            " the labels must be the same as the wig files."
        ),
        default=None,
    )
    return parser

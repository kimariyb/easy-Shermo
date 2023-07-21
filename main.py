from service import parser
from service.parser import ParserFactory
from service.single_point import get_orca_sp, get_gaussian_sp
from unit.config import read_config


def main():
    ParserFactory().create_parser().get_sp()


if __name__ == '__main__':
    main()

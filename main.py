from service.parser import ParserFactory
from utils.config import read_config


def main():
    config = read_config("settings.yaml")
    parser = ParserFactory().create_parser(config)
    parser.get_sp()


if __name__ == '__main__':
    main()

from service.parser import ParserFactory
from utils.config import read_config


def main():
    config = read_config("settings.yaml")
    parser = ParserFactory().create_parser(config)
    energies = parser.get_sp()
    for tuple_elem in energies:
        print(tuple_elem[0])
        print(str(tuple_elem[1]))



if __name__ == '__main__':
    main()

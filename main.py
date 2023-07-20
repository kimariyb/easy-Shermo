from service.single_point import get_orca_sp, get_gaussian_sp
from unit.config import read_config


def main():
    yaml_data = read_config('settings.yaml')
    # energies = get_orca_sp()
    energies = get_orca_sp()
    print(energies)
    print(yaml_data)


if __name__ == '__main__':
    main()

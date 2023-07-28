import configparser
import os.path


class ShermoConfig:
    def __init__(self):
        self.__settings_path = os.path.join(os.path.dirname(__file__), "settings.ini")
        # 创建 ini config 对象
        self.config = configparser.ConfigParser()
        # 设置注释前缀
        self.config.comment_prefixes = ';'
        # 读取 ini 文件的配置
        self.config.read(self.__settings_path)
        # 将配置返回成对象
        self.shermo_config = self.config['Shermo']
        # 获取配置项
        self.shermoPath = self.shermo_config.get('shermoPath')
        self.spFile = self.shermo_config.get('spFile')
        self.prtvib = self.config.get('Shermo', 'prtvib')
        self.T = self.config.get('Shermo', 'T')
        self.P = self.config.get('Shermo', 'P')
        self.sclZPE = self.config.get('Shermo', 'sclZPE')
        self.sclheat = self.config.get('Shermo', 'sclheat')
        self.sclS = self.config.get('Shermo', 'sclS')
        self.sclCV = self.config.get('Shermo', 'sclCV')
        self.ilowfreq = self.config.get('Shermo', 'ilowfreq')
        self.ravib = self.config.get('Shermo', 'ravib')
        self.imode = self.config.get('Shermo', 'imode')
        self.conc = self.config.get('Shermo', 'conc')
        self.outshm = self.config.get('Shermo', 'outshm')
        self.defmass = self.config.get('Shermo', 'defmass')

    def __str__(self):
        return f"The ShermoConfig is: shermoPath={self.shermoPath}, spFile={self.spFile}, prtvib={self.prtvib}, T={self.T}, " \
               f"P={self.P}, sclZPE={self.sclZPE}, sclheat={self.sclheat}, sclS={self.sclS}, sclCV={self.sclCV}, " \
               f"ilowfreq={self.ilowfreq}, ravib={self.ravib}, imode={self.imode}, conc={self.conc}, outshm={self.outshm}, " \
               f"defmass={self.defmass}"

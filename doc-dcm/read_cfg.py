# -*- coding: utf-8 -*-
import os, ConfigParser
from UserDict import UserDict

class Configs(UserDict):
    """класс работы с файлом конфигурации. считывает настройки из файла в тек. директории,
        если файл не существует - создает с дефолтными настройками"""
    config = ConfigParser.ConfigParser()

    def __init__(self, iniFile):
        self.d=self._load(iniFile)
        if not len(self.d): #ини.файл не найден, создаем новый
            print 'no ini file found!'
            self.createcfg(iniFile)
            self.d =self._load(iniFile)
                    
        self.__dict__.update(self.d)
        #self.data=self.d #?

    def _load(self, iniFile='sample.ini', raw=False, vars=None):
        """Convert an INI file to a dictionary"""
        self.config.read(iniFile)
        result = {}
        for section in self.config.sections(): ###?????
            for option in self.config.options(section):
                value = self.config.get(section, option, raw, vars)
                result[option] = value
        return result

    def createcfg(self,iniFile):
        config = ConfigParser.ConfigParser()
        #config_dict = self.data
        c='cfg'
        config.add_section(c)
        config.set(c, 'httpdport', '9966')
        config.set(c, 'httpdhost', 'localhost')
        config.set(c, 'logfn', './store.log')
	config.set(c, 'workdir', './')
        config.set(c, 'dcmhost', 'localhost')
        config.set(c, 'dcmport', '11112')
        config.set(c, 'dcmaetitle', 'DCM4CHEE')
        config.write(open(iniFile, 'w'))

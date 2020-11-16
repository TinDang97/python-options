# python-options
Make python class with option base on property. Using build option for client like kafka, command option like ffmpeg.

Support: python 3.6+

Feature: 
- Build options (config) easily. 
- Clone option (changing not effect with other config which initial from single class)
- (Optional) Filter value on set.
- (Optional) Auto fill default value if delete old value.

Example:
    
    from typing import Any, Type
    from pyopt import Options, UnsetOption, option
    
    
    def filter_type(_type: Type):
        def _filter_wrapper(instance: Any):
            if not isinstance(instance, _type):
                raise TypeError(f"Instance must be `{_type.__name__}`")
            return instance
        return _filter_wrapper
    
    
    class Config(Options):
        server = option("url", filter_type(str), doc="URL of server host.")

    if __name__ == '__main__':
        conf = Config()
        try:
            conf.server = 1  # raise TypeError
        except TypeError as e:
            print(f"ERROR: {e}")
    
        try:
            print(conf.server)
        except UnsetOption as e:
            print(f"Unset: {e}")
    
        conf.server = "127.0.0.1:9090"
        print(conf.__repr__())
        print(conf.build())
     
     
    >>> config = Config()

    >>> config.server = 1
    TypeError: Instance must be `str`

    >>> conf.server
    The option `url` of Config hasn't been set.

    >>> config.server = "127.0.0.1:9090"
    >>> print(conf)
    Config:
        - server         | "url" = "127.0.0.1:9090"                    | Doc: URL of server host.

    >>> print(conf.build())
    {'url': '127.0.0.1:9090'}


### Info
Author = "Tin Dang"  
Copyright = "Copyright (C) 2020 DPS"  
Version = "1.0"  
Doc = "Options base on property which help build dict name=value with value filter."
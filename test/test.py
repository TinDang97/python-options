from typing import Any, Type

from pyopt import Options, UnsetOption, option


def filter_type(_type: Type):
    def _filter_wrapper(instance: Any):
        if not isinstance(instance, _type):
            raise TypeError(f"Instance must be `{_type.__name__}`")
        return instance
    return _filter_wrapper


class Config(Options):
    """
    Config server

    Examples:
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
    """
    server = option("url", filter_type(str), doc="URL of server host.")


class ConfigDefault(Config):
    """
    Config server

    Examples:
        >>> config = Config()

        >>> config.server = 1
        Raises: TypeError: Instance must be `str`

        >>> print(conf)
        Config:
            - server         | "url" = "127.0.0.1:9090"                    | Doc: URL of server host.

        >>> conf.server = "192.168.1.100:9090"

        >>> print(conf)
        Config:
            - server         | "url" = "192.168.1.100:9090"                    | Doc: URL of server host.

        >>> print(conf.build())
        {'url': '1111'}
    """
    server = option("url", filter_type(str), default_value="127.0.0.1:9090", doc="URL of server host.")


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

__author__ = "Tin Dang"
__copyright__ = "Copyright (C) 2020 DPS"
__version__ = "1.0"
__doc__ = "Options base on property which help build dict name=value with value filter."
__all__ = [
    'Options', 'Option', 'option', 'readonly_option', 'clone_options',
    'InterruptedSetOption', 'UnsetOption',
    "__doc__", "__version__", "__copyright__", "__author__"
]

import inspect
from copy import deepcopy
from typing import Optional, Union, Callable, Any, Sequence, Tuple

SETFUNC_OPTION_TYPE = (bool, type(None), staticmethod, classmethod)


class DuplicateOptionName(Exception):
    pass


class InterruptedSetOption(Exception):
    pass


class UnsetOption(Exception):
    def __init__(self, name, clss=None):
        if clss is None:
            super(UnsetOption, self).__init__(f"The option `{name}` hasn't been set.")
        else:
            super(UnsetOption, self).__init__(f"The option `{name}` of {clss.__name__} hasn't been set.")

    def __bool__(self):
        return False

    def __eq__(self, other):
        return isinstance(other, UnsetOption)


class Option(property):
    """
    Define options as property.
    Implement from property python built-in

    Attributes:
        name: name of option
        doc: option's docstring
        default_value: Default value of option
    """

    def __init__(self, name: str,
                 set_filter: Union[Callable[[Any], Any], bool] = None,
                 default_value: Optional[Any] = None,
                 doc: Optional[str] = None):
        """
        Init Option with at least name param.
        Args:
            name: Key of option. Auto fill if not set.
            set_filter: Filter value before set.
            default_value: Default value of option.
            doc: docstring
        """
        self.__name = name
        self.__doc = doc
        self.__default_value = default_value
        self.__set_filter = set_filter

        if not hasattr(set_filter, "__call__"):
            if not isinstance(set_filter, SETFUNC_OPTION_TYPE):
                raise TypeError(f"Set filter must in {SETFUNC_OPTION_TYPE}. Got {type(set_filter)}")

            elif isinstance(set_filter, (staticmethod, classmethod)):
                set_filter = set_filter.__func__

        if hasattr(set_filter, "__call__"):
            num_args = len(inspect.getfullargspec(set_filter).args)
            if num_args == 0:
                def wrap_set_filter(*args, **kwargs):
                    return set_filter()

            elif num_args == 1:
                def wrap_set_filter(value, *args, **kwargs):
                    return set_filter(value)
            else:
                def wrap_set_filter(_self, value, *args, **kwargs):
                    return set_filter(_self, value)

        elif isinstance(set_filter, bool) and not set_filter:
            wrap_set_filter = ValueError("Read-only options.")
        else:
            wrap_set_filter = None

        def _wrap_setter(_self, value):
            if hasattr(wrap_set_filter, "__call__"):
                try:
                    value = wrap_set_filter(_self=_self, value=value)
                except InterruptedSetOption:
                    return
            elif isinstance(wrap_set_filter, Exception):
                raise wrap_set_filter
            return OptionsBase.fset(_self, self.__name, value)

        def _wrap_getter(_self):
            try:
                return OptionsBase.fget(_self, self.__name)
            except UnsetOption as e:
                if self.__default_value is not None:
                    _wrap_setter(_self, deepcopy(self.__default_value))
                    return OptionsBase.fget(_self, self.__name)
                raise e

        def _wrap_deleter(_self):
            if self.__default_value is not None:
                _wrap_setter(_self, deepcopy(self.__default_value))
            return OptionsBase.fdelete(_self, self.__name)
        super().__init__(_wrap_getter, _wrap_setter, _wrap_deleter)

    def __repr__(self):
        return f'Name: "{self.__name}"\n' \
               f"Writeable: {bool(self.__set_filter)}\n" \
               f'Doc: "{self.__doc}"'

    def __iter__(self):
        yield self.__name
        yield self.__set_filter
        yield self.__default_value
        yield self.__doc

    @property
    def name(self) -> str:
        return self.__name

    @property
    def doc(self) -> str:
        return self.__doc

    @property
    def default_value(self) -> Any:
        return self.__default_value

    @property
    def set_filter(self) -> Callable:
        return self.__set_filter


class OptionsBase(object):
    """OptionBase with full feature set, get, del. Which contain all option name=value in dict"""

    def __init__(self, options: Optional['OptionsBase'] = None):
        """
        Create Option pool contains many Option in attribute class.

        Args:
            options:
        """
        self.__opts = dict()

        if options is not None:
            self.from_options(options)

        name_opts = set()
        for name, opt in self.options():
            if opt.default_value is not None:
                setattr(self, name, deepcopy(opt.default_value))

            if opt.name in name_opts:
                raise DuplicateOptionName(f"Duplicate option's name: `{opt.name}` at {name} option")
            else:
                name_opts.add(opt.name)

    def __repr__(self):
        _repr = list()
        for attr, opt in self.options():
            # attribute name
            _repr.append(f'\n\t-> {attr:12}')

            # option name + value
            try:
                v = getattr(self, attr)
                if isinstance(v, OptionsBase):
                    _repr.append(v.__class__.__name__)
                    if v:
                        _repr.append(f"({v.__str__()})")
                    else:
                        _repr.append(f"({None})")
                else:
                    if not isinstance(v, (int, float)):
                        v = f"'{v}'"
            except UnsetOption:
                v = "[UNSET]"

            v = f'| -{opt.name} {v}'
            _repr.append(f"{v:30}")

            # doc
            if opt.doc:
                _repr.append(f' | {opt.doc}')
        return f"{self.__class__.__name__.upper()}" \
               f"{''.join(_repr)}\n"

    def __str__(self):
        return self.__opts.__str__()

    def __bool__(self):
        return bool(self.__opts)

    def __contains__(self, opt: Option):
        """Check if OptionBase have attr."""
        return bool(self.find_option(opt))

    def __setitem__(self, name, value):
        return self.__setattr__(name, value)

    def __getitem__(self, name):
        return self.__getattribute__(name)

    def __delitem__(self, name):
        return self.__delattr__(name)

    def __iter__(self):
        for attr, _ in self.options():
            yield attr

    def fget(self, name):
        if name not in self.__opts:
            raise UnsetOption(name, self.__class__)
        return self.__opts.__getitem__(name)

    def fset(self, name, value):
        self.__opts.__setitem__(name, value)

    def fdelete(self, name):
        if name not in self.__opts:
            raise UnsetOption(name, self.__class__)
        self.__opts.__delitem__(name)

    def add_opt(self, name: str, opt: Option):
        """
        Add attribute option

        Args:
            name:
            opt:

        Returns:

        """
        if not isinstance(opt, Option):
            raise TypeError("Only support Option type.")
        setattr(self.__class__, name, opt)

    def find_option(self, opt: Option) -> Optional[str]:
        """
        Find option with Option.

        Args:
            opt: class's option

        Returns:
            Attribute if option existed.

        Raises:
            TypeError: unless opt class is Option
        """
        if not isinstance(opt, Option):
            raise TypeError("opt must be Option.")

        for _attr, _opt in self.options():
            if _opt.name == opt.name:
                return _attr
        return None

    def get_value(self, opt: Option) -> Any:
        return self.__getattribute__(self.find_option(opt))

    def is_set(self, name: Union[str, Option]) -> bool:
        """
        Option had set.

        Args:
            name: name of attribute or Option attribute.

        Returns:
            True if set.

        Raises:
            TypeError: unless name is `Option` or `str`
        """
        if not isinstance(name, (str, Option)):
            raise TypeError("name params must be `str` or `Option`.")

        if isinstance(name, Option):
            name = name.name
        return self.__opts.__contains__(name)

    def clear(self):
        """Clear all set data."""
        self.__opts.clear()

    def diff(self, other: 'OptionsBase') -> dict:
        """
        Get options not exist in other Options.

        Args:
            other: Options

        Returns:
            Difference options.

        Raises:
            TypeError: type of other isn't supported.
        """
        if not isinstance(other, type(self)):
            raise TypeError(f"Type `{type(other)}` can't compare.")

        diff = {}
        for k in set(self.__opts.keys()).difference(other.__opts):
            diff[k] = self.__opts[k]

        for k in set(other.__opts.keys()).difference(self.__opts):
            diff[k] = other.__opts[k]
        return diff

    def from_options(self, _options: 'OptionsBase'):
        """
        Copy option from another option if exist.

        Args:
            _options: other Options

        Raises:
            TypeError: type of other isn't supported.
        """
        if not isinstance(_options, OptionsBase) or not isinstance(self, type(_options)):
            raise TypeError(f"Type `{type(_options)}` can't get options.")
        self.__opts.update(_options.__opts)

    def build(self) -> dict:
        """Return dict of option (name=value)"""
        return dict(**self.__opts)

    def options(self) -> Sequence[Tuple[str, Option]]:
        """Return list of options."""
        options = list()
        for attr in dir(self):
            if attr.startswith("_"):
                continue

            opt = getattr(self.__class__, attr)
            if not isinstance(opt, Option):
                continue

            options.append((attr, opt))
        return options


class OptionType(type):
    def __repr__(self):
        _repr = list()
        for opt in dir(self):
            attr = getattr(self, opt)
            if not isinstance(attr, Option):
                continue
            _repr.append(f"- {opt}\n{attr.__repr__()}")
        return "\n\n".join(_repr)


class Options(OptionsBase, metaclass=OptionType):
    """
    Option Container without get, set and del attributes.
    """

    def fget(self, *args, **kwargs):
        raise AttributeError

    def fset(self, *args, **kwargs):
        raise AttributeError

    def fdelete(self, *args, **kwargs):
        raise AttributeError


def option(name: str,
           set_filter: Union[Callable[[Any], Any], bool, None] = None,
           default_value: Optional[Any] = None,
           doc: Optional[str] = None) -> Option:
    """Option decorator

    Args:
        name: Key of option. Auto fill if not set.
        set_filter: Filter value before set.
        default_value: Default value of option. It isn't filtered by filter.
        doc: docstring

    Examples:
        class Test(Options):
            test = option("test")

    """
    if isinstance(name, Option):
        name = name.name
    return Option(name, set_filter=set_filter, default_value=default_value, doc=doc)


def readonly_option(name,
                    default_value: Optional[Any] = None,
                    doc: Optional[str] = None) -> Option:
    """Readonly option decorator

        Args:
            name: Key of option. Auto fill if not set.
            default_value: Default value of option. It isn't filtered by filter.
            doc: docstring
    """
    return option(name, False, default_value, doc)


def clone_options(opts: Union[Options, OptionType], clss_name: Optional[str] = None):
    if isinstance(opts, Options):
        opts = type(opts)

    if not isinstance(opts, OptionType):
        raise TypeError(f"options must be OptionType.")

    if clss_name is None:
        name = str(opts.__name__)
    else:
        name = str(clss_name)

    _dict = opts.__dict__.copy()
    _bases = tuple(opts.__bases__)
    return OptionType(name, _bases, _dict)()

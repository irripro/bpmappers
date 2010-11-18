# vim:fileencoding=utf-8
class BaseField(object):
    def __init__(self, callback=None, after_callback=None, *args, **kwargs):
        self.key = None
        self._callback = callback
        self._after_callback = after_callback

    def callback_value(self, value):
        # callbackは割り込み用
        if self._callback is None:
            return value
        return self._callback(value)

    def after_callback_value(self, value):
        if self._after_callback is None:
            return value
        return self._after_callback(value)

    def get_value(self, value):
        return self.after_callback_value(self.as_value(self.callback_value(value)))

    def as_value(self, value):
        raise NotImplementedError

    @property
    def is_nonkey(self):
        raise NotImplementedError

class NonKeyField(BaseField):
    def as_value(self, value=None):
        return value

    @property
    def is_nonkey(self):
        return True

class Field(BaseField):
    def __init__(self, key=None, callback=None, *args, **kwargs):
        super(Field, self).__init__(callback, *args, **kwargs)
        self.key = key

    @property
    def is_nonkey(self):
        return False

class RawField(Field):
    def as_value(self, value):
        return value

class ChoiceField(Field):
    def __init__(self, choices, key=None, callback=None, *args, **kwargs):
        super(ChoiceField, self).__init__(key, callback, *args, **kwargs)
        self.choices = choices

    def as_value(self, value):
        # TODO:イテレータに対応する
        return self.choices[value]

class DelegateField(Field):
    """
    指定したMapperにデリゲートするフィールド
    """
    def __init__(self, mapper_class, key=None, callback=None, before_filter=None, required=True, *args, **kwargs):
        super(DelegateField, self).__init__(key, callback, *args, **kwargs)
        self._before_filter = before_filter
        self.mapper_class = mapper_class
        self.required = required

    def before_filter(self, value):
        if self._before_filter:
            return self._before_filter(value)
        return value

    def as_value(self, value):
        val = self.before_filter(value)
        if val is None:
            if not self.required:
                return
        return self.mapper_class(val).as_dict()

class ListDelegateField(DelegateField):
    """
    指定したMapperにリストとしてデリゲートするフィールド
    """
    def __init__(self, mapper_class, key=None, callback=None, filter=None, after_filter=None, *args, **kwargs):
        super(ListDelegateField, self).__init__(mapper_class, key, callback, *args, **kwargs)
        self._filter = filter
        self._after_filter = after_filter

    def filter(self, value):
        if self._filter:
            return self._filter(value)
        return value

    def after_filter(self, value):
        if self._after_filter:
            return self._after_filter(value)
        return value

    def as_value(self, value):
        parsed = []
        # filterは割り込み用
        value = self.filter(value)
        if value is None:
            if not self.required:
                return
        # TODO:イテレータを返す方が良い？
        for v in value:
            parsed.append(self.after_filter(super(ListDelegateField, self).as_value(self.callback_value(v))))
        return parsed

class NonKeyDelegateField(NonKeyField):
    def __init__(self, mapper_class, callback=None, *args, **kwargs):
        super(NonKeyDelegateField, self).__init__(callback, *args, **kwargs)
        self.mapper_class = mapper_class

    def as_value(self, value=None):
        return self.mapper_class(value).as_dict()

class NonKeyListDelegateField(NonKeyDelegateField):
    def __init__(self, mapper_class, callback=None, filter=None, *args, **kwargs):
        super(NonKeyListDelegateField, self).__init__(mapper_class, callback, *args, **kwargs)
        self._filter = filter

    def filter(self, value=None):
        if self._filter:
            return self._filter(value)
        return value

    def as_value(self, value=[]):
        parsed = []
        # filterは割り込み用
        value = self.filter(value)
        for v in value:
            parsed.append(super(NonKeyListDelegateField, self).as_value(self.callback_value(v)))
        return parsed
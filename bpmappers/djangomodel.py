# vim:fileencoding=utf-8
from bpmappers.fields import RawField, DelegateField, ListDelegateField
from bpmappers.mappers import Options, BaseMapper, Mapper

from django.db import models

class MetaModelError(Exception):
    "Invalid mapper Meta"

DEFAULT_MAPPER_FIELD = RawField

# Djangoのフィールドに対応したMapperField
DEFINED_MODEL_MAPPER_FIELDS = {
    models.AutoField: DEFAULT_MAPPER_FIELD,
    models.CharField: DEFAULT_MAPPER_FIELD,
    models.TextField: DEFAULT_MAPPER_FIELD,
    models.IntegerField: DEFAULT_MAPPER_FIELD,
    models.DateTimeField: DEFAULT_MAPPER_FIELD,
    models.DateField: DEFAULT_MAPPER_FIELD,
    models.TimeField: DEFAULT_MAPPER_FIELD,
    models.BooleanField: DEFAULT_MAPPER_FIELD,
}

def create_model_mapper(model_class, model_fields=None, model_exclude=None):
    class _mapper_class(ModelMapper):
        class Meta:
            model = model_class
            fields = model_fields
            exclude = model_exclude
    return _mapper_class

class ModelMapperMetaclass(BaseMapper):
    def __new__(cls, name, bases, attrs):
        #for base_class in bases:
        #    if hasattr(base_class, '_meta'):
        #        base_meta = base_class._meta.copy()
        #        attrs['_meta'] = base_meta
        if not '_meta' in attrs:
            opt = Options()
            attrs['_meta'] = opt
        else:
            opt = attrs['_meta']
        # BaseMapperの処理が後に来るので
        # ここで先にoptを拡張する
        mapper_meta = attrs.get('Meta')
        if not mapper_meta is None:
            model = getattr(mapper_meta, 'model', None)
            # Meta.modelが無い場合はエラー
            if model is None:
                raise MetaModelError
            #if name=='TaggedItemModelMapper':
            #    import pdb;pdb.set_trace()
            for model_field in model._meta.fields + model._meta.many_to_many:
                # Meta.fields
                if hasattr(mapper_meta, 'fields'):
                    if not mapper_meta.fields is None and not model_field.name in mapper_meta.fields:
                        continue
                # Meta.exclude
                if hasattr(mapper_meta, 'exclude'):
                    if not mapper_meta.exclude is None and model_field.name in mapper_meta.exclude:
                        continue
                # モデルのフィールドに対応したField追加
                if model_field.rel:
                    # 同じモデルを参照しようとした場合はスキップする
                    if model == model_field.rel.to:
                        continue
                    if isinstance(model_field, models.ForeignKey):
                        # ForeignKey
                        related_model_mapper = create_model_mapper(model_field.rel.to)
                        opt.add_field(model_field.name, DelegateField(related_model_mapper, key=model_field.name))
                    elif isinstance(model_field, models.ManyToManyField):
                        # ManyToManyField
                        related_model_mapper = create_model_mapper(model_field.rel.to)
                        opt.add_field(model_field.name, ListDelegateField(related_model_mapper, key=model_field.name, filter=lambda manager:manager.all()))
                else:
                    for defined_field in DEFINED_MODEL_MAPPER_FIELDS:
                        if isinstance(model_field, defined_field):
                            mapper_field = DEFINED_MODEL_MAPPER_FIELDS[defined_field]
                            opt.add_field(model_field.name, mapper_field(key=model_field.name))
                    else:
                        opt.add_field(model_field.name, DEFAULT_MAPPER_FIELD(key=model_field.name))
        attrs['_meta'] = opt
        return BaseMapper.__new__(cls, name, bases, attrs)

class ModelMapper(Mapper):
    """
    djangoモデルに対して使えるMapper
    """
    __metaclass__ = ModelMapperMetaclass


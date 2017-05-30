=========
bpmappers
=========

|build-status| |pypi| |docs|

bpmappersは、Pythonの辞書の値やオブジェクトのプロパティを別の辞書へマッピングするPythonモジュールです。

インストール
============

pip を使ってインストールします。

::

   $ pip install bpmappers

使い方
======

Personクラスのインスタンスを辞書に変換する例です:

.. doctest::

   >>> class Person:
   ...     def __init__(self, name, age):
   ...         self.name = name
   ...         self.age = age
   ...     def __repr__(self):
   ...         return "<Person name={}, age={}>".format(self.name, self.age)
   ...
   >>> p = Person("Spam", 25)
   >>> p
   <Person name=Spam, age=25>
   >>> from bpmappers import Mapper, RawField
   >>> class PersonMapper(Mapper):
   ...     mapped_name = RawField('name')
   ...     mapped_age = RawField('age')
   ...
   >>> PersonMapper(p).as_dict()
   {'mapped_age': 25, 'mapped_name': 'Spam'}

動作要件
========

- Pythonのバージョン 2.7, 3.4, 3.5, 3.6
- Django>=1.8 (Djangoサポートを使用する場合)

ライセンス
==========

MITライセンス

ドキュメント
============

最新のドキュメントはReadTheDocsでホストされています。

https://bpmappers.readthedocs.io/en/latest/

開発
====

このプロジェクトはGitHubでホストされています: https://github.com/beproud/bpmappers

作者
====

- BeProud, Inc

メンテナ
========

- Shinya Okano <tokibito@gmail.com>

.. |build-status| image:: https://travis-ci.org/beproud/bpmappers.svg?branch=master
   :target: https://travis-ci.org/beproud/bpmappers
.. |docs| image:: https://readthedocs.org/projects/bpmappers/badge/?version=latest
   :target: https://readthedocs.org/projects/bpmappers/
.. |pypi| image:: https://badge.fury.io/py/bpmappers.svg
   :target: http://badge.fury.io/py/bpmappers
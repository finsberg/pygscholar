import pygscholar
from polyfactory.factories.pydantic_factory import ModelFactory


class PublicationFactory(ModelFactory):
    __model__ = pygscholar.Publication


class AuthorFactory(ModelFactory):
    __model__ = pygscholar.Author


class AuthorInfoFactory(ModelFactory):
    __model__ = pygscholar.author.AuthorInfo

import pygscholar
from pydantic_factories import ModelFactory


class PublicationFactory(ModelFactory):
    __model__ = pygscholar.Publication


class PublicationBibFactory(ModelFactory):
    __model__ = pygscholar.publication.PublicationBib


class FullPublicationFactory(ModelFactory):
    __model__ = pygscholar.FullPublication


class FullPublicationBibFactory(ModelFactory):
    __model__ = pygscholar.publication.FullPublicationBib


class AuthorFactory(ModelFactory):
    __model__ = pygscholar.Author

import pyscholar
from pydantic_factories import ModelFactory


class PublicationFactory(ModelFactory):
    __model__ = pyscholar.Publication


class PublicationBibFactory(ModelFactory):
    __model__ = pyscholar.publication.PublicationBib


class AuthorFactory(ModelFactory):
    __model__ = pyscholar.Author


class DepartmentFactory(ModelFactory):
    ___model__ = pyscholar.Department

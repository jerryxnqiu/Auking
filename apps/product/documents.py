from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch import Elasticsearch

from .models import ProductSKU

@registry.register_document
class ProductSKUDocument(Document):

    class Index:
        name = "productsku"

    class Django:
        model = ProductSKU

        fields = ["id", "nameEN",]
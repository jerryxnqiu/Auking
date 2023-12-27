from haystack import indexes
from .models import ProductSKU


class ProductSKUIndex(indexes.SearchIndex, indexes.Indexable):

    # indexing fields from the model, "use_template" specifies which fields in the table
    # to create an index file and which fields to index in a file.
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return ProductSKU

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
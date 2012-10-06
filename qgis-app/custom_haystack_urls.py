# Custom haystack search to match partial strings

from haystack.views import SearchView
from haystack.query import SearchQuerySet
from django.conf.urls.defaults import *

class SearchWithRequest(SearchView):

    __name__ = 'SearchWithRequest'

    def build_form(self, form_kwargs=None):
        if form_kwargs is None:
            form_kwargs = {}

        if self.searchqueryset is None:
            sqs1 = SearchQuerySet().filter(description_auto=self.request.GET.get('q', ''))
            sqs2 = SearchQuerySet().filter(name_auto=self.request.GET.get('q', ''))
            sqs3 = SearchQuerySet().filter(text=self.request.GET.get('q', ''))
            form_kwargs['searchqueryset'] = sqs1 | sqs2 | sqs3

        return super(SearchWithRequest, self).build_form(form_kwargs)

    def get_results(self):
        """
        Fetches the results
        """
        return self.form.searchqueryset


urlpatterns = patterns('haystack.views',
    url(r'^$', SearchWithRequest(load_all=False), name='haystack_search'), 
)

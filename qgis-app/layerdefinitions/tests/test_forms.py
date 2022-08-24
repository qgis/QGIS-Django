from base.forms.processing_forms import ResourceBaseReviewForm
from django.test import TestCase


class TestFormResourceBaseReviewForm(TestCase):
    def test_review_form_comment_includes_resource_name(self):
        form = ResourceBaseReviewForm(resource_name="test resource")
        self.assertIn(
            'placeholder="Please provide clear feedback if you decided to not '
            'approve this test resource." required id="id_comment"',
            form.as_table(),
        )

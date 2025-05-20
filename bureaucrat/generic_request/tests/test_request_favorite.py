from .common import RequestCase


class TestRequestFavorite(RequestCase):
    """Tests for Request Favorites functionality"""

    def test_request_favorite_toggle(self):
        """Test addition/removal to/from favorites"""
        Request = self.env['request.request']
        user = self.env.ref('generic_request.user_demo_request')

        # Create a request to test with
        request = Request.sudo().create({
            'type_id': self.simple_type.id,
            'category_id': self.general_category.id,
            'request_text': 'Test favorite functionality',
        })

        # Check that request is not in favorites initially
        self.assertFalse(
            request.sudo().favourite_user_ids.ids,
            "Newly created request must not be in favorites")

        # Add to favorites
        request.sudo().with_user(user).toggle_favourite()

        # Check that request is now in favorites
        self.assertTrue(
            user.id in request.sudo().favourite_user_ids.ids,
            "User should be in favourite_user_ids after adding to favorites")

        # Remove from favorites
        request.sudo().with_user(user).toggle_favourite()

        # Check that request is no longer in favorites
        self.assertFalse(
            request.sudo().favourite_user_ids.ids,
            "User should not be in favourite_user_ids "
            "after removing from favorites")

    def test_favorite_multi_user(self):
        """Test that favorites work independently for different users"""
        Request = self.env['request.request']
        user1 = self.env.ref('generic_request.user_demo_request')
        user2 = self.env.ref('generic_request.user_demo_request_manager')

        # Create a request to test with
        request = Request.sudo().create({
            'type_id': self.simple_type.id,
            'category_id': self.general_category.id,
            'request_text': 'Test favorite multi-user',
        })

        # Add to favorites for user1
        request.sudo().with_user(user1).toggle_favourite()

        # Check that request is in favorites for user1 but not for user2
        self.assertTrue(
            user1.id in request.sudo().favourite_user_ids.ids,
            "Request must be in favorites for the first user")
        self.assertFalse(
            user2.id in request.sudo().favourite_user_ids.ids,
            "Request must not be in favorites for the second user")

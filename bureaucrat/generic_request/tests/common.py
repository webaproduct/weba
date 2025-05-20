import logging
import pytz
from odoo import models
from odoo.tests.common import TransactionCase
from odoo.addons.generic_mixin.tests.common import (
    ReduceLoggingMixin,
    AccessRulesFixMixinST,
)
from odoo.addons.generic_system_event.tests.common import (
    GenericSystemTestUtils,
)


try:
    # pylint: disable=unused-import
    from freezegun import freeze_time  # noqa
except ImportError:  # pragma: no cover
    logging.getLogger(__name__).warning(
        "freezegun not installed. Tests will not work!")


def ensure_classifier(env, *,
                      service=None, category=None,
                      request_type=None, active=None):
    """ Ensure that requested classifier exists, or create new one if not
    """
    # pylint: disable=too-many-branches
    if isinstance(service, str):
        service_id = env.ref(service).id
    elif isinstance(service, models.BaseModel):
        service_id = service.id
    elif isinstance(service, int):
        service_id = service
    elif not service:
        service_id = False
    else:
        raise AssertionError("Unknown format of service")

    if isinstance(category, str):
        category_id = env.ref(category).id
    elif isinstance(category, models.BaseModel):
        category_id = category.id
    elif isinstance(category, int):
        category_id = category
    elif not category:
        category_id = False
    else:
        raise AssertionError("Unknown format of category")

    if isinstance(request_type, str):
        type_id = env.ref(request_type).id
    elif isinstance(request_type, models.BaseModel):
        type_id = request_type.id
    elif isinstance(request_type, int):
        type_id = request_type
    elif not request_type:
        type_id = False
    else:
        raise AssertionError("Unknown format of request type")

    classifier = env['request.classifier'].with_context(
        active_test=False
    ).search([
        ('service_id', '=', service_id),
        ('category_id', '=', category_id),
        ('type_id', '=', type_id),
    ], limit=1)
    if not classifier:
        classifier = env['request.classifier'].create({
            'service_id': service_id,
            'category_id': category_id,
            'type_id': type_id,
        })
    if active is not None and classifier.active != active:
        classifier.write({'active': active})
    return classifier


def get_utc_datetime(timezone, dt):
    """
    Convert a datetime to UTC, given a timezone.

    Parameters:
    - timezone (str or pytz.tzinfo.BaseTzInfo):
        A string representing the timezone or a pytz timezone object.
    - dt (datetime): The datetime object to be converted.

    Returns:
    - datetime: The UTC datetime.

    Raises:
    - ValueError: If the timezone argument is neither a string
        nor a pytz timezone object.

    Note:
    The returned UTC datetime will not have a timezone information attached.
    """
    if isinstance(timezone, str):
        target_timezone = pytz.timezone(timezone)
    elif isinstance(timezone, pytz.tzinfo.BaseTzInfo):
        target_timezone = timezone
    else:
        raise ValueError(
            "Invalid timezone argument. "
            "Please provide a valid timezone string or timezone object.")
    localized_datetime = target_timezone.localize(dt)
    utc_datetime = localized_datetime.astimezone(pytz.utc)

    return utc_datetime.replace(tzinfo=None)


class RequestCloseMixin:
    """ Simple mixin that provides convenient method to close requests.
    """

    def _close_request(self, request, stage, response_text=False, user=None):
        if user is None:
            user = self.env.user

        close_route = self.env['request.stage.route'].with_user(user).search([
            ('request_type_id', '=', request.type_id.id),
            ('stage_from_id', '=', request.stage_id.id),
            ('stage_to_id', '=', stage.id),
        ])
        close_route.ensure_one()

        act = request.action_close_request()
        wiz = self.env[act['res_model']].with_user(user).with_context(
            **act['context'],
        ).create({
            'close_route_id': close_route.id,
            'response_text': response_text,
        })
        wiz.action_close_request()

        self.assertEqual(request.stage_id, stage)
        self.assertEqual(request.response_text, response_text)


class RequestClassifierUtilsMixin:
    """ This mixin provides some utility methods to deal with
        request classifiers in tests
    """

    def ensure_classifier(self, *, service=None, category=None,
                          request_type=None, active=None, **kw):
        """ Ensure that requested classifier exists, or create new one if not
        """
        return ensure_classifier(
            self.env,
            service=service,
            category=category,
            request_type=request_type,
            active=active)


class RequestCase(AccessRulesFixMixinST,
                  ReduceLoggingMixin,
                  GenericSystemTestUtils,
                  RequestCloseMixin,
                  RequestClassifierUtilsMixin,
                  TransactionCase):
    """ BAse tests case for tests related to generic request
    """

    @classmethod
    def setUpClass(cls):
        super(RequestCase, cls).setUpClass()
        cls.Classifier = cls.env['request.classifier']

        cls.general_category = cls.env.ref(
            'generic_request.request_category_demo_general')
        cls.resource_category = cls.env.ref(
            'generic_request.request_category_demo_resource')
        cls.tec_configuration_category = cls.env.ref(
            'generic_request.request_category_demo_technical_configuration')

        # Request type
        cls.simple_type = cls.env.ref('generic_request.request_type_simple')
        cls.sequence_type = cls.env.ref(
            'generic_request.request_type_sequence')
        cls.non_ascii_type = cls.env.ref(
            'generic_request.request_type_non_ascii')
        cls.access_type = cls.env.ref(
            'generic_request.request_type_access')

        # Stages
        cls.stage_draft = cls.env.ref(
            'generic_request.request_stage_type_simple_draft')
        cls.stage_sent = cls.env.ref(
            'generic_request.request_stage_type_simple_sent')
        cls.stage_confirmed = cls.env.ref(
            'generic_request.request_stage_type_simple_confirmed')
        cls.stage_rejected = cls.env.ref(
            'generic_request.request_stage_type_simple_rejected')
        cls.stage_new = cls.env.ref(
            'generic_request.request_stage_type_sequence_new')
        # Routes
        cls.route_draft_to_sent = cls.env.ref(
            'generic_request.request_stage_route_type_simple_draft_to_sent')
        cls.non_ascii_route_draft_to_sent = cls.env.ref(
            'generic_request.request_stage_route_type_non_ascii_draft_to_sent')

        # Requests
        cls.request_1 = cls.env.ref(
            'generic_request.request_request_type_simple_demo_1')
        cls.request_2 = cls.env.ref(
            'generic_request.request_request_type_access_demo_1')

        # Users
        cls.demo_user = cls.env.ref('base.user_demo')
        cls.request_user = cls.env.ref(
            'generic_request.user_demo_request')
        cls.request_manager = cls.env.ref(
            'generic_request.user_demo_request_manager')
        cls.request_manager_2 = cls.env.ref(
            'generic_request.user_demo_request_manager_2')

        # Creation template
        cls.creation_template = cls.env.ref(
            'generic_request.demo_request_creation_template')

        # Request kind
        cls.request_kind = cls.env.ref('generic_request.request_kind_demo')


class AccessRightsCase(AccessRulesFixMixinST,
                       ReduceLoggingMixin,
                       TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(AccessRightsCase, cls).setUpClass()
        cls.simple_type = cls.env.ref('generic_request.request_type_simple')

        # Users
        cls.demo_user = cls.env.ref('generic_request.user_demo_request')
        cls.demo_manager = cls.env.ref(
            'generic_request.user_demo_request_manager')

        # Envs
        cls.uenv = cls.env(user=cls.demo_user)   # pylint: disable=not-callable
        cls.menv = cls.env(   # pylint: disable=not-callable
            user=cls.demo_manager)

        # Request Type
        cls.usimple_type = cls.uenv.ref('generic_request.request_type_simple')
        cls.msimple_type = cls.menv.ref('generic_request.request_type_simple')

        # Request category
        cls.ucategory_demo_general = cls.uenv.ref(
            'generic_request.request_category_demo_general')
        cls.mcategory_demo_general = cls.menv.ref(
            'generic_request.request_category_demo_general')

        # Request view action
        cls.request_action = cls.env.ref(
            'generic_request.action_request_window')

    def _read_request_fields(self, user, request):
        fields = list(
            self.env['request.request'].with_user(
                user
            ).get_views(
                self.request_action.views
            )['models']['request.request']
        )
        return request.with_user(user).read(fields)

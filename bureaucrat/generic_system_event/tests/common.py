import logging
from odoo.osv import expression

try:
    # pylint: disable=unused-import
    from freezegun import freeze_time  # noqa
except ImportError:  # pragma: no cover
    logging.getLogger(__name__).warning(
        "freezegun not installed. Tests will not work!")


class GenericSystemTestUtils:
    """ This is mixin class, that have to be mixed to real test cases
    """

    def _get_events(self, record, limit=None,
                    exclude_codes=None,
                    only_codes=None,
                    count=False):
        """ Find all events for specified record

            :param int limit: Maximum number of events to fetch
            :param list[str] exclude_codes: event codes to ignore
            :param list[str] only_codes: find only events with mentioned codes
            :param bool count: only compute count of events
        """
        self.assertEqual(len(record), 1)
        event_model_name = self.env[
            'generic.system.event.source'
        ].get_event_data_model(record._name)
        domain = [('event_source_record_id', '=', record.id)]
        if exclude_codes:
            domain = expression.AND([
                domain,
                [('event_type_id.code', 'not in', tuple(exclude_codes))],
            ])
        if only_codes:
            domain = expression.AND([
                domain,
                [('event_type_id.code', 'in', tuple(only_codes))],
            ])
        res = self.env[event_model_name].search(
            domain,
            limit=limit,
            order='event_date DESC, id DESC',
        )

        return len(res) if count else res

    def _get_event_count(self, record,
                         exclude_codes=None,
                         only_codes=None):
        """ Get count of events

            :param list[str] exclude_codes: event codes to ignore
            :param list[str] only_codes: find only events with mentioned codes
        """
        return self._get_events(
            record,
            exclude_codes=exclude_codes,
            only_codes=only_codes,
            count=True)

    def _get_last_event(self, record, exclude_codes=None):
        """ Get last event for record
        """
        return self._get_events(record, limit=1, exclude_codes=exclude_codes)

    def _trigger_cron_job(self, job_xmlid):
        cron_job = self.env.ref(job_xmlid)
        self.assertEqual(cron_job._name, 'ir.cron')
        cron_job.ensure_one()
        cron_job.method_direct_trigger()

    def assertEventCount(self, record, expected_count, *,
                         exclude_codes=None,
                         only_codes=None):
        """ Asset that record has specified event count.
        """
        self.assertEqual(
            self._get_event_count(
                record, exclude_codes=exclude_codes, only_codes=only_codes),
            expected_count)

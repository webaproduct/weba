import logging
from odoo.addons.generic_mixin.tools.migration_utils import ensure_version

_logger = logging.getLogger(__name__)


@ensure_version('4.37.23')
def migrate(cr, version):
    # 1. Create a temporary table to store the data during migration
    cr.execute("""
        DROP TABLE IF EXISTS temp_classifier_tag_categories;
    """)
    cr.execute("""
        CREATE TABLE temp_classifier_tag_categories (
            classifier_id integer,
            tag_category_id integer,
            PRIMARY KEY (classifier_id, tag_category_id)
        )
    """)

    # 2. Get all classifiers with their related types, categories, and services
    cr.execute("""
            SELECT
            classifier.id as classifier_id,
            classifier.type_id as type_id,
            classifier.category_id as category_id,
            classifier.service_id as service_id
        FROM request_classifier classifier
        WHERE classifier.type_id IS NOT NULL
    """)
    classifiers = cr.fetchall()
    _logger.info('Found %d classifiers to process', len(classifiers))

    # Process each classifier
    for classifier in classifiers:
        classifier_id = classifier[0]
        type_id = classifier[1]
        category_id = classifier[2]
        service_id = classifier[3]

        # Initialize an empty set to collect tag category IDs
        tag_category_ids = set()

        # 3. Get tag categories from request type
        if type_id:
            cr.execute("""
                SELECT rtc.category_id
                FROM request_type_tag_category_rel rtc
                WHERE rtc.type_id = %s
            """, (type_id,))
            type_tag_categories = cr.fetchall()
            if type_tag_categories:
                type_tag_category_ids = [tc[0] for tc in type_tag_categories]
                tag_category_ids.update(type_tag_category_ids)
                _logger.info(
                    'Collecting %d tag categories from request type (ID: %s)',
                    len(type_tag_category_ids), type_id
                )

        # 4. Get tag categories from request category
        if category_id:
            cr.execute("""
                SELECT rcc.category_id
                FROM request_category_tag_category_rel rcc
                WHERE rcc.request_category_id = %s
            """, (category_id,))
            category_tag_categories = cr.fetchall()
            if category_tag_categories:
                category_tag_category_ids = [
                    tc[0] for tc in category_tag_categories]
                tag_category_ids.update(category_tag_category_ids)
                _logger.info(
                    'Collecting %d tag categories '
                    'from request category (ID: %s)',
                    len(category_tag_category_ids), category_id
                )

        # 5. Get tag categories from service
        if service_id:
            cr.execute("""
                SELECT gsc.category_id
                FROM request_service_tag_category_rel gsc
                WHERE gsc.service_id = %s
            """, (service_id,))
            service_tag_categories = cr.fetchall()
            if service_tag_categories:
                service_tag_category_ids = [
                    tc[0] for tc in service_tag_categories]
                tag_category_ids.update(service_tag_category_ids)
                _logger.info(
                    'Collecting %d tag categories from service (ID: %s)',
                    len(service_tag_category_ids), service_id
                )

        # 6. Save collected categories to temporary table
        if tag_category_ids:
            _logger.info(
                'Saving %d tag categories for classifier '
                '(ID: %s) to temporary table',
                len(tag_category_ids), classifier_id
            )
            for tag_category_id in tag_category_ids:
                # Use INSERT ON CONFLICT DO NOTHING to handle duplicates
                cr.execute("""
                    INSERT INTO temp_classifier_tag_categories
                    (classifier_id, tag_category_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """, (classifier_id, tag_category_id))
        else:
            _logger.info(
                'No tag categories found for classifier (ID: %s)',
                classifier_id
            )

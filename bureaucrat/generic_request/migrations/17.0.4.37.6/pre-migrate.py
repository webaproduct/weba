import logging
from odoo.addons.generic_mixin.tools.migration_utils import ensure_version

_logger = logging.getLogger(__name__)


@ensure_version('4.37.6')
def migrate(cr, installed_version):
    # Check for duplicate classifiers in request_classifier
    # and halt migration if they exists
    cr.execute("""
        SELECT
            service_id,
            category_id,
            type_id,
            COUNT(*) AS duplicate_count
        FROM
            request_classifier
        GROUP BY
            service_id, category_id, type_id
        HAVING
            COUNT(*) > 1
            AND COUNT(*) = COUNT(
                CASE
                    WHEN service_id IS NOT DISTINCT FROM service_id
                    AND category_id IS NOT DISTINCT FROM category_id
                    AND type_id IS NOT DISTINCT FROM type_id
                    THEN 1
                    ELSE NULL
                END
            );
    """)
    duplicate_classifiers = cr.fetchall()

    if duplicate_classifiers:
        for serv_id, cat_id, type_id, duplicate_count in duplicate_classifiers:
            _logger.error(
                f"Duplicate classifier found for "
                f"service_id={serv_id}, "
                f"category_id={cat_id}, "
                f"type_id={type_id}. "
                f"Count: {duplicate_count}"
            )

        raise Exception(
            "Migration aborted: Duplicate classifiers found. "
            "Please remove duplicates before proceeding.")

    # Check for missing classifiers in created requests
    # and halt migration if it exists
    cr.execute("""
        SELECT DISTINCT
            rr.service_id,
            rr.category_id,
            rr.type_id
        FROM
            request_request rr
        WHERE NOT EXISTS (
            SELECT 1 FROM request_classifier rc
            WHERE
                rc.service_id IS NOT DISTINCT FROM rr.service_id
                AND rc.category_id IS NOT DISTINCT FROM rr.category_id
                AND rc.type_id IS NOT DISTINCT FROM rr.type_id
        );
    """)
    missing_classifiers = cr.fetchall()

    if missing_classifiers:
        _logger.info(f"Found {len(missing_classifiers)} missing classifiers.")
        for serv_id, cat_id, type_id in missing_classifiers:
            cr.execute("""
                    INSERT INTO request_classifier
                    (service_id, category_id, type_id, active)
                    VALUES (%s, %s, %s, %s)
                """, (serv_id, cat_id, type_id, True))
            _logger.info(
                f"Created missing classifier for "
                f"service_id={serv_id}, "
                f"category_id={cat_id}, "
                f"type_id={type_id}."
            )

        _logger.info("All missing classifiers have been created.")

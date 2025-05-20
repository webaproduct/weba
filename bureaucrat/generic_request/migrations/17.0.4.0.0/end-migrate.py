from odoo.tools.sql import table_exists
from odoo.addons.generic_mixin.tools.migration_utils import ensure_version


def migrate_data_to_classificators(cr):
    cr.execute("""
        INSERT INTO request_classifier
               (type_id, category_id, service_id, active)
        SELECT type_id, category_id, service_id, True
        FROM (
            -- In case when type has related categories and services, we have
            -- to add all allowed combinations of them.
            SELECT DISTINCT
                st.type_id     AS type_id,
                sc.category_id AS category_id,
                sc.service_id  AS service_id
            FROM
                generic_service_request_type_rel AS st,
                request_type_category_rel AS tc,
                service_category_rel AS sc
            WHERE st.service_id = sc.service_id
              AND st.type_id = tc.type_id
              AND sc.category_id = tc.category_id
              AND st.type_id IS NOT NULL
            -----
            UNION
            -----
            -- In case when type does not have related services and categories,
            -- we have to write only one row with only type and no service and
            -- no category.
            SELECT
                rt.id   AS type_id,
                NULL    AS category_id,
                NULL    AS service_id
            FROM request_type AS rt
            WHERE NOT EXISTS (
                    SELECT 1 FROM generic_service_request_type_rel AS st
                    WHERE st.type_id = rt.id)
              AND NOT EXISTS (
                    SELECT 1 FROM request_type_category_rel AS tc
                    WHERE tc.type_id = rt.id)
            ----
            UNION
            -----
            -- In case when type has related categories but no services.
            SELECT
                id                  AS type_id,
                rtcl.category_id    AS category_id,
                NULL                AS service_id
            FROM request_type rt
            LEFT JOIN request_type_category_rel AS rtcl
                ON rt.id = rtcl.type_id AND NOT EXISTS (
                    SELECT 1 FROM service_category_rel AS sc
                    WHERE sc.category_id = rtcl.category_id)
            WHERE
                rtcl.category_id IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM generic_service_request_type_rel AS st
                    WHERE st.type_id = rt.id
                )
            -----
            UNION
            -----
            -- In case when type has related service, but no related categories
            SELECT
                id                AS type_id,
                NULL              AS category_id,
                rsrtr.service_id  AS service_id
            FROM request_type rt
            LEFT JOIN generic_service_request_type_rel AS rsrtr
                ON rt.id = rsrtr.type_id
            WHERE
                rsrtr.service_id IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM request_type_category_rel AS tc
                    WHERE tc.type_id = rt.id
                )
            -----
            UNION
            -----
            -- Create classifiers for request creation templates.
            -- If there is template for such combination exists,
            -- then it is possible to create request with such combination
            -- of service, category and type
            SELECT request_type_id     AS type_id,
                   request_category_id AS category_id,
                   request_service_id  AS service_id
            FROM request_creation_template
        ) AS t
        ON CONFLICT DO NOTHING;

        UPDATE request_creation_template
        SET request_classifier_id = rc.id
        FROM request_classifier AS rc
        WHERE ((rc.service_id IS NULL AND request_service_id IS NULL)
               OR rc.service_id = request_service_id)
          AND ((rc.category_id IS NULL AND request_category_id IS NULL)
               OR rc.category_id = request_category_id)
          AND rc.type_id = request_type_id;
    """)


def migrate_data_to_classificators_no_service(cr):
    cr.execute("""
        INSERT INTO request_classifier
               (type_id, category_id, service_id, active)
        SELECT type_id, category_id, NULL, True
        FROM (
            -- In case when type has related categories, we have
            -- to add all allowed combinations of them.
            SELECT DISTINCT
                tc.type_id     AS type_id,
                tc.category_id AS category_id
            FROM request_type_category_rel AS tc
            -----
            UNION
            -----
            -- In case when type does not have related categories,
            -- we have to write only one row with only type and no service and
            -- no category.
            SELECT
                rt.id   AS type_id,
                NULL    AS category_id
            FROM request_type AS rt
            WHERE NOT EXISTS (
                    SELECT 1 FROM request_type_category_rel AS tc
                    WHERE tc.type_id = rt.id)
            -----
            UNION
            -----
            -- Create classifiers for request creation templates.
            -- If there is template for such combination exists,
            -- then it is possible to create request with such combination
            -- of service, category and type
            SELECT request_type_id     AS type_id,
                   request_category_id AS category_id
            FROM request_creation_template
        ) AS t
        ON CONFLICT DO NOTHING;

        UPDATE request_creation_template
        SET request_classifier_id = rc.id
        FROM request_classifier AS rc
        WHERE (rc.service_id IS NULL)
          AND ((rc.category_id IS NULL AND request_category_id IS NULL)
               OR rc.category_id = request_category_id)
          AND rc.type_id = request_type_id;
    """)


@ensure_version('4.0.0')
def migrate(cr, installed_version):
    if (table_exists(cr, 'generic_service_request_type_rel') and
            table_exists(cr, 'service_category_rel')):
        # If there are existing tables for relation between
        # service and category and type, then we do full migration.
        # In this case, that services were just merged into generic_request
        migrate_data_to_classificators(cr)
    else:
        # Otherwise, it seems that it is pretty old installation
        # of generic_request without services, thus there are no relatins
        # for type <-> service and category <-> service,
        # thus we can run simplified migration
        migrate_data_to_classificators_no_service(cr)

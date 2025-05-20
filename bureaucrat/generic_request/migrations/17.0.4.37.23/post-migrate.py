import logging
from odoo.addons.generic_mixin.tools.migration_utils import ensure_version
import psycopg2

_logger = logging.getLogger(__name__)


@ensure_version('4.37.23')
def migrate(cr, version):
    # Check if temporary table exists
    cr.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'temp_classifier_tag_categories'
        )
    """)
    temp_table_exists = cr.fetchone()[0]

    if not temp_table_exists:
        _logger.warning(
            'Temporary table temp_classifier_tag_categories not found. '
            'Skipping tag category migration.'
        )
        return

    # Get all data from temporary table
    try:
        cr.execute("SELECT classifier_id, tag_category_id "
                   "FROM temp_classifier_tag_categories")
        tag_mappings = cr.fetchall()
        _logger.info('Found %d tag category mappings to transfer',
                     len(tag_mappings))

        if not tag_mappings:
            _logger.info('No tag categories to transfer')
            return
        # Transfer data to the new relation table
        successful_inserts = 0
        for mapping in tag_mappings:
            classifier_id = mapping[0]
            tag_category_id = mapping[1]
            try:
                # Insert with conflict handling
                cr.execute("""
                    INSERT INTO request_classifier_tag_category_rel
                    (classifier_id, category_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """, (classifier_id, tag_category_id))
                cr.connection.commit()  # Commit each successful insert
                successful_inserts += 1
            except Exception as e:
                cr.connection.rollback()  # Rollback on error
                _logger.error(
                    'Error inserting tag category %s for classifier %s: %s',
                    tag_category_id, classifier_id, str(e)
                )
        # Report successful migrations
        _logger.info('Successfully migrated %d tag category mappings',
                     successful_inserts)
        # Drop temporary table if we have successfully migrated all records
        if successful_inserts == len(tag_mappings):
            _logger.info('Dropping temporary table')
            cr.execute("DROP TABLE temp_classifier_tag_categories")
            cr.connection.commit()
        else:
            _logger.warning(
                'Only %d of %d mappings were migrated. '
                'Keeping temp table for reference.',
                successful_inserts, len(tag_mappings)
            )
    except psycopg2.Error as e:
        cr.connection.rollback()
        _logger.error('Database error during migration: %s', str(e))
    except Exception as e:
        cr.connection.rollback()
        _logger.error('Unexpected error during migration: %s', str(e))

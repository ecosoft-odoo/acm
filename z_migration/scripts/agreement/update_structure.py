"""
This method will create structure (recitals, sections, clauses, appendices)
in agreement
"""
import sys
import os
try:
    agreement_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.dirname(agreement_path)
    migration_path = os.path.dirname(script_path)
    controller_path = '%s/controller' % migration_path
    sys.path.insert(0, controller_path)
    from connection import connection
    import log
except Exception:
    pass

# Model
Agreement = connection.get_model('agreement')

# Domain
dom = [('is_template', '=', False)]

# Search Agreement
agreements = Agreement.search_read(dom)

log_agreement_ids = [[], []]
logger = log.setup_custom_logger('update_structure')
logger.info('Start process')
logger.info('Total agreement: %s' % len(agreements))
for agreement in agreements:
    try:
        # Make sure no have line in recital, section, clause, appendix
        Agreement.mock_unlink_recital_structure([agreement['id']])
        Agreement.mock_unlink_section_structure([agreement['id']])
        Agreement.mock_unlink_clause_structure([agreement['id']])
        # Agreement.mock_unlink_appendix_structure([agreement['id']])
        # Update structure
        Agreement.mock_copy_recital_structure([agreement['id']])
        Agreement.mock_copy_section_structure([agreement['id']])
        # Agreement.mock_copy_appendix_structure([agreement['id']])
        # Write log
        log_agreement_ids[0].append(agreement['id'])
        logger.info('Pass ID: %s' % agreement['id'])
    except Exception as ex:
        log_agreement_ids[1].append(agreement['id'])
        logger.error('Fail ID: %s (reason: %s)' % (agreement['id'], ex))
summary = 'Summary: pass %s%s and fail %s%s' \
          % (len(log_agreement_ids[0]),
             log_agreement_ids[0] and ' %s' % str(tuple(log_agreement_ids[0]))
             or '', len(log_agreement_ids[1]),
             log_agreement_ids[1] and ' %s' % str(tuple(log_agreement_ids[1]))
             or '')
logger.info(summary)
logger.info('End process')

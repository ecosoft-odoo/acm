#!/bin/bash
pg_container="postgres"
pg_user="odoo"
db="ACM_TEST"
psql="docker exec -it $pg_container psql -U $pg_user $db"

# Contracts & Agreements
$psql -c "delete from account_analytic_distribution"
$psql -c "delete from account_analytic_line"
$psql -c "delete from account_analytic_account"
$psql -c "delete from agreement where is_template is False"

# Batch Invoices
$psql -c "delete from acm_batch_invoice_line"
$psql -c "delete from acm_batch_invoice"

# Accounts
$psql -c "delete from account_invoice"
$psql -c "delete from account_payment"
$psql -c "delete from account_partial_reconcile"
$psql -c "delete from account_full_reconcile"
$psql -c "delete from account_move"

# Message
$psql -c "delete from mail_message"
$psql -c "delete from mail_followers"

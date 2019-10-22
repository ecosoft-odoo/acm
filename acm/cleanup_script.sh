#!/bin/bash
pg_container="postgres"
pg_user="odoo"
db="ACM"
psql="docker exec -it $pg_container psql -U $pg_user $db"

# Contracts & Agreements
$psql -c "delete from account_analytic_line"
$psql -c "delete from account_analytic_account"
$psql -c "delete from agreement where is_template is False"

# Accounts
$psql -c "delete from account_invoice"
$psql -c "delete from account_payment"
$psql -c "delete from account_partial_reconcile"
$psql -c "delete from account_full_reconcile"
$psql -c "delete from account_move"

# Message
$psql -c "delete from mail_message"
$psql -c "delete from mail_followers"

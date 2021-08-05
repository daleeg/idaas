# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pandora.models import Company
from pandora.utils.cacheutils import get_company_info, set_company_info
import logging

LOG = logging.getLogger(__name__)


def get_companies():
    return Company.objects.all()


def get_company_object(company_id):
    company = get_company_info(company_id)
    if not company:
        try:
            company = Company.objects.get(uid=company_id)
            set_company_info(company_id, company)
        except (company.DoesNotExist, company.MultipleObjectsReturned) as e:
            LOG.error("Get company {} Failed, {}".format(company_id, e))
        except Exception as e:
            LOG.error("Bad company {} Params, {}".format(company_id, e))
    return company

# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.query_builder.functions import Sum
from frappe.utils import cint, flt, get_link_to_form


class JobOffer(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from hrms.hr.doctype.job_offer_term.job_offer_term import JobOfferTerm

		amended_from: DF.Link | None
		applicant_email: DF.Data | None
		applicant_name: DF.Data
		company: DF.Link
		designation: DF.Link
		job_applicant: DF.Link
		job_offer_term_template: DF.Link | None
		letter_head: DF.Link | None
		offer_date: DF.Date
		offer_terms: DF.Table[JobOfferTerm]
		select_print_heading: DF.Link | None
		select_terms: DF.Link | None
		status: DF.Literal["Awaiting Response", "Accepted", "Rejected", "Cancelled"]
		terms: DF.TextEditor | None
	# end: auto-generated types

	def onload(self):
		employee = frappe.db.get_value("Employee", {"job_applicant": self.job_applicant}, "name") or ""
		self.set_onload("employee", employee)

	def validate(self):
		self.validate_vacancies()
		job_offer = frappe.db.exists(
			"Job Offer", {"job_applicant": self.job_applicant, "docstatus": ["!=", 2]}
		)
		if job_offer and job_offer != self.name:
			frappe.throw(
				_("Job Offer: {0} is already for Job Applicant: {1}").format(
					frappe.bold(job_offer), frappe.bold(self.job_applicant)
				)
			)
		self.calculate_salary_breakdown()


	def calculate_salary_breakdown(self):
		m_gross = flt(self.custom_monthly_remuneration) or flt(self.custom_gross_salary)
		raw_ctc = flt(self.custom_ctc)

		b_pct = flt(self.custom_formula_basic_pct) or 50.0
		hra_pct = flt(self.custom_formula_hra_pct) or 50.0
		bonus_pct = flt(self.custom_formula_bonus_pct) or 8.33
		conv_pct = flt(self.custom_formula_conveyance_pct) or 10.0
		pf_ceiling = flt(self.custom_formula_pf_ceiling) or 25000.0
		pf_rate = flt(self.custom_formula_pf_er_rate) or 12.0
		pf_ee_rate = flt(self.custom_formula_pf_ee_rate) or 12.0
		esi_ceiling = flt(self.custom_formula_esi_ceiling) or 21000.0
		esi_rate = flt(self.custom_formula_esi_er_rate) or 4.0
		grat_pct = flt(self.custom_formula_gratuity_pct) or 4.81
		med_amt = flt(self.custom_formula_medical_amt) if self.custom_formula_medical_amt is not None and str(self.custom_formula_medical_amt).strip() != "" else 2000.0

		if not self.custom_probation:
			self.custom_probation = "6 Months"
		if not self.custom_notice_period:
			self.custom_notice_period = "1 Month"

		# If CTC is provided but Gross isn't, calculate Gross from CTC (matching Excel structure)
		if not m_gross and raw_ctc:
			m_ctc = raw_ctc / 12.0 if raw_ctc > 60000 else raw_ctc
			if m_ctc <= (21000 * 1.12405 + med_amt):
				g = (m_ctc - med_amt) / 1.12405
			elif m_ctc <= (50000 * 1.08405 + med_amt):
				g = (m_ctc - med_amt) / 1.08405
			else:
				g = (m_ctc - (25000 * 0.12 + med_amt)) / 1.02405
			m_gross = round(max(0, g))
			self.custom_monthly_remuneration = m_gross
			self.custom_gross_salary = m_gross

		if not m_gross:
			return

		# If components are empty, auto-populate all components
		if not flt(self.custom_basic):
			m_basic = round(m_gross * (b_pct / 100.0))
			m_hra = round(m_basic * (hra_pct / 100.0))
			m_bonus = round(m_basic * (bonus_pct / 100.0))
			m_conv = round(m_basic * (conv_pct / 100.0))
			m_other = round(m_gross - m_bonus - m_conv - (m_basic + m_hra))
			if m_other < 0:
				m_other = 0

			pf_wage = min(m_basic, pf_ceiling)
			m_pf_er = round(pf_wage * (pf_rate / 100.0))
			m_pf_ee = round(pf_wage * (pf_ee_rate / 100.0))

			m_esi_total = 0 if m_gross > esi_ceiling else round(m_gross * (esi_rate / 100.0))
			m_esi_ee = 0 if m_gross > esi_ceiling else round(m_gross * 0.0075)

			m_gratuity = round((grat_pct * m_basic) / 100.0)
			m_medical = round(med_amt)

			m_fixed_comp = round(m_gross + m_pf_er + m_esi_total + m_gratuity + m_medical)
			ann_ctc = round(m_fixed_comp * 12)
			m_take_home = round(m_gross - m_pf_er - m_gratuity - m_esi_total)

			self.custom_basic = m_basic
			self.custom_hra = m_hra
			self.custom_bonus = m_bonus
			self.custom_conveyance = m_conv
			self.custom_other_allowances = m_other
			self.custom_gross_salary = m_gross
			self.custom_monthly_remuneration = m_gross
			self.custom_pf_employer = m_pf_er
			self.custom_pf_employee = m_pf_ee
			self.custom_esi_employer = m_esi_total
			self.custom_esi_employee = m_esi_ee
			self.custom_gratuity = m_gratuity
			self.custom_medical = m_medical
			self.custom_fixed_compensation = m_fixed_comp
			self.custom_ctc = ann_ctc
			self.custom_net_salary = m_take_home
		else:
			# Components exist (or were edited by hand), re-tally totals
			b = flt(self.custom_basic)
			hra = flt(self.custom_hra)
			bonus = flt(self.custom_bonus)
			conv = flt(self.custom_conveyance)
			other = flt(self.custom_other_allowances)
			gross = round(b + hra + bonus + conv + other)

			pf_er = flt(self.custom_pf_employer)
			esi_total = flt(self.custom_esi_employer)
			gratuity = flt(self.custom_gratuity)
			medical = flt(self.custom_medical)

			fixed_comp = round(gross + pf_er + esi_total + gratuity + medical)
			ann_ctc = round(fixed_comp * 12)
			take_home = round(gross - pf_er - gratuity - esi_total)

			self.custom_gross_salary = gross
			self.custom_monthly_remuneration = gross
			self.custom_fixed_compensation = fixed_comp
			if not self.custom_ctc:
				self.custom_ctc = ann_ctc
			self.custom_net_salary = take_home

	def validate_vacancies(self):
		staffing_plan = get_staffing_plan_detail(self.designation, self.company, self.offer_date)
		check_vacancies = frappe.get_single("HR Settings").check_vacancies
		if staffing_plan and check_vacancies:
			job_offers = self.get_job_offer(staffing_plan.from_date, staffing_plan.to_date)
			if not staffing_plan.get("vacancies") or cint(staffing_plan.vacancies) - len(job_offers) <= 0:
				error_variable = "for " + frappe.bold(self.designation)
				if staffing_plan.get("parent"):
					error_variable = frappe.bold(get_link_to_form("Staffing Plan", staffing_plan.parent))

				frappe.throw(_("There are no vacancies under staffing plan {0}").format(error_variable))

	def on_change(self):
		update_job_applicant(self.status, self.job_applicant)

	def get_job_offer(self, from_date, to_date):
		"""Returns job offer created during a time period"""
		return frappe.get_all(
			"Job Offer",
			filters={
				"offer_date": ["between", (from_date, to_date)],
				"designation": self.designation,
				"company": self.company,
				"docstatus": 1,
			},
			fields=["name"],
		)

	def on_discard(self):
		self.db_set("status", "Cancelled")


def update_job_applicant(status, job_applicant):
	if status in ("Accepted", "Rejected"):
		frappe.set_value("Job Applicant", job_applicant, "status", status)


def get_staffing_plan_detail(designation, company, offer_date):
	spd = frappe.qb.DocType("Staffing Plan Detail")
	sp = frappe.qb.DocType("Staffing Plan")

	detail = (
		frappe.qb.from_(spd)
		.inner_join(sp)
		.on(spd.parent == sp.name)
		.select(
			spd.parent,
			sp.from_date.as_("from_date"),
			sp.to_date.as_("to_date"),
			sp.name,
			Sum(spd.vacancies).as_("vacancies"),
			spd.designation,
		)
		.distinct()
		.where(
			(sp.docstatus == 1)
			& (spd.designation == designation)
			& (sp.company == company)
			& (sp.from_date <= offer_date)
			& (offer_date <= sp.to_date)
		)
		.groupby(spd.parent, sp.from_date, sp.to_date, sp.name, spd.designation)
	).run(as_dict=1)

	return frappe._dict(detail[0]) if (detail and detail[0].parent) else None


@frappe.whitelist()
def make_employee(source_name: str, target_doc: str | Document | None = None):
	def set_missing_values(source, target):
		target.personal_email, target.first_name = frappe.db.get_value(
			"Job Applicant", source.job_applicant, ["email_id", "applicant_name"]
		)

	doc = get_mapped_doc(
		"Job Offer",
		source_name,
		{
			"Job Offer": {
				"doctype": "Employee",
				"field_map": {"applicant_name": "employee_name", "offer_date": "scheduled_confirmation_date"},
			}
		},
		target_doc,
		set_missing_values,
	)
	return doc


@frappe.whitelist()
def get_offer_acceptance_rate(company: str | None = None, department: str | None = None):
	frappe.has_permission("Job Offer", throw=True)

	filters = {"docstatus": 1}
	if company:
		filters["company"] = company
	if department:
		filters["department"] = department

	total_offers = frappe.db.count("Job Offer", filters=filters)

	filters["status"] = "Accepted"
	total_accepted = frappe.db.count("Job Offer", filters=filters)

	return {
		"value": flt(total_accepted) / flt(total_offers) * 100 if total_offers else 0,
		"fieldtype": "Percent",
	}

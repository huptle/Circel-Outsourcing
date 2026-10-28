// Client Script for DocType: Job Offer
// Name: Job Offer-Form
// Enabled: 1

frappe.ui.form.on('Job Offer', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            // Download PDF button
            frm.add_custom_button(__('📄 Download Offer Letter (PDF)'), function() {
                const url = '/api/method/frappe.utils.print_format.download_pdf?doctype=Job%20Offer&name=' + encodeURIComponent(frm.doc.name) + '&format=Exact%20Corporate%20Offer%20Letter&no_letterhead=0';
                window.open(url, '_blank');
            }).addClass('btn-primary');

            // View Print Format Preview
            frm.add_custom_button(__('👁️ View Offer Letter Print'), function() {
                frappe.set_route('print', 'Job Offer', frm.doc.name);
            });
        }

        // Formula editing & calculation buttons
        frm.add_custom_button(__('⚙️ Edit Calculation Formulas'), function() {
            open_formula_modal(frm);
        }, __('Formulas'));

        frm.add_custom_button(__('🌐 Global Formula Settings'), function() {
            frappe.set_route('Form', 'Offer Letter Formula Settings');
        }, __('Formulas'));

        frm.add_custom_button(__('⚡ Re-Apply Formulas to Breakdown'), function() {
            calculate_and_set_breakdown(frm, true);
        });

        // Initialize formula defaults if empty
        ensure_formula_defaults(frm);
    },

    custom_ctc: function(frm) {
        if (frm.__updating) return;
        calculate_and_set_breakdown(frm, false);
    },

    custom_monthly_remuneration: function(frm) {
        if (frm.__updating) return;
        if (frm.doc.custom_monthly_remuneration && !frm.doc.custom_ctc) {
            frm.__updating = true;
            frm.set_value('custom_ctc', Math.round(frm.doc.custom_monthly_remuneration * 12)).then(() => {
                frm.__updating = false;
                calculate_and_set_breakdown(frm, false);
            });
        }
    },

    // Formula changes trigger re-calculation
    custom_formula_basic_pct: function(frm) { if (!frm.__updating) calculate_and_set_breakdown(frm, true); },
    custom_formula_min_basic: function(frm) { if (!frm.__updating) calculate_and_set_breakdown(frm, true); },
    custom_formula_hra_pct: function(frm) { if (!frm.__updating) calculate_and_set_breakdown(frm, true); },
    custom_formula_bonus_pct: function(frm) { if (!frm.__updating) calculate_and_set_breakdown(frm, true); },
    custom_formula_pf_ceiling: function(frm) { if (!frm.__updating) calculate_and_set_breakdown(frm, true); },
    custom_formula_pf_ee_rate: function(frm) { if (!frm.__updating) calculate_and_set_breakdown(frm, true); },
    custom_formula_pf_er_rate: function(frm) { if (!frm.__updating) calculate_and_set_breakdown(frm, true); },
    custom_formula_esi_ceiling: function(frm) { if (!frm.__updating) calculate_and_set_breakdown(frm, true); },
    custom_formula_esi_ee_rate: function(frm) { if (!frm.__updating) calculate_and_set_breakdown(frm, true); },
    custom_formula_esi_er_rate: function(frm) { if (!frm.__updating) calculate_and_set_breakdown(frm, true); },

    // Manual component adjustments update totals
    custom_basic: function(frm) { if (!frm.__updating) recalculate_totals_from_fields(frm); },
    custom_hra: function(frm) { if (!frm.__updating) recalculate_totals_from_fields(frm); },
    custom_bonus: function(frm) { if (!frm.__updating) recalculate_totals_from_fields(frm); },
    custom_other_allowances: function(frm) { if (!frm.__updating) recalculate_totals_from_fields(frm); },
    custom_pf_employee: function(frm) { if (!frm.__updating) recalculate_totals_from_fields(frm); },
    custom_esi_employee: function(frm) { if (!frm.__updating) recalculate_totals_from_fields(frm); },
    custom_pf_employer: function(frm) { if (!frm.__updating) recalculate_totals_from_fields(frm); },
    custom_esi_employer: function(frm) { if (!frm.__updating) recalculate_totals_from_fields(frm); }
});

function ensure_formula_defaults(frm) {
    if (!frm.doc.custom_formula_basic_pct) {
        frappe.db.get_doc('Offer Letter Formula Settings').then(settings => {
            frm.__updating = true;
            frm.set_value({
                custom_formula_basic_pct: settings.basic_percentage || 50.0,
                custom_formula_min_basic: settings.min_statutory_basic || 16025.0,
                custom_formula_hra_pct: settings.hra_percentage || 40.0,
                custom_formula_bonus_pct: settings.bonus_percentage || 8.33,
                custom_formula_pf_ceiling: settings.pf_wage_ceiling || 15000.0,
                custom_formula_pf_ee_rate: settings.pf_employee_rate || 12.0,
                custom_formula_pf_er_rate: settings.pf_employer_rate || 13.0,
                custom_formula_esi_ceiling: settings.esi_wage_ceiling || 21000.0,
                custom_formula_esi_ee_rate: settings.esi_employee_rate || 0.75,
                custom_formula_esi_er_rate: settings.esi_employer_rate || 3.25
            }).then(() => {
                frm.__updating = false;
            });
        });
    }
}

function calculate_and_set_breakdown(frm, force) {
    const raw_ctc = flt(frm.doc.custom_ctc) || (flt(frm.doc.custom_monthly_remuneration) * 12);
    if (!raw_ctc) return;

    const ann_ctc = raw_ctc > 60000 ? raw_ctc : (raw_ctc * 12);
    const m_ctc = Math.round(ann_ctc / 12);

    // Read configured formula parameters
    const basic_pct = flt(frm.doc.custom_formula_basic_pct) || 50.0;
    const min_basic = flt(frm.doc.custom_formula_min_basic) || 16025.0;
    const hra_pct = flt(frm.doc.custom_formula_hra_pct) || 40.0;
    const bonus_pct = flt(frm.doc.custom_formula_bonus_pct) || 8.33;
    const pf_ceiling = flt(frm.doc.custom_formula_pf_ceiling) || 15000.0;
    const pf_ee_rate = flt(frm.doc.custom_formula_pf_ee_rate) || 12.0;
    const pf_er_rate = flt(frm.doc.custom_formula_pf_er_rate) || 13.0;
    const esi_ceiling = flt(frm.doc.custom_formula_esi_ceiling) || 21000.0;
    const esi_ee_rate = flt(frm.doc.custom_formula_esi_ee_rate) || 0.75;
    const esi_er_rate = flt(frm.doc.custom_formula_esi_er_rate) || 3.25;

    let m_basic = 0, m_hra = 0;
    if (m_ctc >= 30000) {
        m_basic = Math.round(m_ctc * (basic_pct / 100.0));
        m_hra = Math.round(m_basic * (hra_pct / 100.0));
    } else if (m_ctc >= 20000) {
        m_basic = Math.max(min_basic, Math.round(m_ctc * (basic_pct / 100.0)));
        m_hra = (hra_pct > 0 && m_ctc >= 25000) ? Math.round(m_basic * (hra_pct / 100.0)) : 0;
    } else {
        m_basic = Math.round(m_ctc * Math.max(0.50, basic_pct / 100.0));
        m_hra = 0;
    }

    const m_bonus = Math.round(m_basic * (bonus_pct / 100.0));
    const pf_wage = Math.min(m_basic, pf_ceiling);
    const m_pf_ee = Math.round(pf_wage * (pf_ee_rate / 100.0));
    const m_pf_er = Math.round(pf_wage * (pf_er_rate / 100.0));

    const gross_approx = m_ctc - m_pf_er;
    let m_esi_er = 0, m_esi_ee = 0, m_gross = 0;
    if (gross_approx <= esi_ceiling) {
        m_esi_er = Math.round(gross_approx * (esi_er_rate / 100.0));
        m_gross = m_ctc - m_pf_er - m_esi_er;
        m_esi_ee = Math.round(m_gross * (esi_ee_rate / 100.0));
    } else {
        m_gross = m_ctc - m_pf_er;
    }

    let m_other = m_gross - m_basic - m_hra - m_bonus;
    if (m_other < 0) {
        m_other = 0;
        m_gross = m_basic + m_hra + m_bonus;
    }
    const m_net = m_gross - m_pf_ee - m_esi_ee;

    frm.__updating = true;
    frm.set_value({
        custom_ctc: ann_ctc,
        custom_monthly_remuneration: m_gross,
        custom_basic: m_basic,
        custom_hra: m_hra,
        custom_bonus: m_bonus,
        custom_other_allowances: m_other,
        custom_gross_salary: m_gross,
        custom_pf_employee: m_pf_ee,
        custom_esi_employee: m_esi_ee,
        custom_net_salary: m_net,
        custom_pf_employer: m_pf_er,
        custom_esi_employer: m_esi_er
    }).then(() => {
        frm.__updating = false;
    });
}

function recalculate_totals_from_fields(frm) {
    const b = flt(frm.doc.custom_basic);
    const hra = flt(frm.doc.custom_hra);
    const bonus = flt(frm.doc.custom_bonus);
    const other = flt(frm.doc.custom_other_allowances);
    const gross = Math.round(b + hra + bonus + other);

    const pf_ee = flt(frm.doc.custom_pf_employee);
    const esi_ee = flt(frm.doc.custom_esi_employee);
    const net = Math.round(gross - pf_ee - esi_ee);

    const pf_er = flt(frm.doc.custom_pf_employer);
    const esi_er = flt(frm.doc.custom_esi_employer);
    const m_ctc = Math.round(gross + pf_er + esi_er);
    const ann_ctc = Math.round(m_ctc * 12);

    frm.__updating = true;
    frm.set_value({
        custom_gross_salary: gross,
        custom_net_salary: net,
        custom_monthly_remuneration: gross,
        custom_ctc: ann_ctc
    }).then(() => {
        frm.__updating = false;
    });
}

function open_formula_modal(frm) {
    const d = new frappe.ui.Dialog({
        title: __('⚙️ Edit Breakdown Calculation Formulas'),
        fields: [
            { fieldtype: 'Section Break', label: __('Earnings Formulas & Percentages') },
            { fieldtype: 'Percent', fieldname: 'basic_pct', label: __('Basic Salary % of CTC'), default: frm.doc.custom_formula_basic_pct || 50.0 },
            { fieldtype: 'Currency', fieldname: 'min_basic', label: __('Minimum Statutory Basic (INR)'), default: frm.doc.custom_formula_min_basic || 16025.0 },
            { fieldtype: 'Percent', fieldname: 'hra_pct', label: __('HRA % of Basic'), default: frm.doc.custom_formula_hra_pct || 40.0 },
            { fieldtype: 'Percent', fieldname: 'bonus_pct', label: __('Statutory Bonus % of Basic'), default: frm.doc.custom_formula_bonus_pct || 8.33 },
            { fieldtype: 'Column Break' },
            { fieldtype: 'Section Break', label: __('Deductions & Retiral Caps') },
            { fieldtype: 'Currency', fieldname: 'pf_ceiling', label: __('PF Wage Ceiling (INR)'), default: frm.doc.custom_formula_pf_ceiling || 15000.0 },
            { fieldtype: 'Percent', fieldname: 'pf_ee_rate', label: __('PF Employee Contribution %'), default: frm.doc.custom_formula_pf_ee_rate || 12.0 },
            { fieldtype: 'Percent', fieldname: 'pf_er_rate', label: __('PF Employer Contribution %'), default: frm.doc.custom_formula_pf_er_rate || 13.0 },
            { fieldtype: 'Currency', fieldname: 'esi_ceiling', label: __('ESI Wage Limit (INR)'), default: frm.doc.custom_formula_esi_ceiling || 21000.0 },
            { fieldtype: 'Percent', fieldname: 'esi_ee_rate', label: __('ESI Employee %'), default: frm.doc.custom_formula_esi_ee_rate || 0.75 },
            { fieldtype: 'Percent', fieldname: 'esi_er_rate', label: __('ESI Employer %'), default: frm.doc.custom_formula_esi_er_rate || 3.25 },
        ],
        primary_action_label: __('Save & Apply Formulas'),
        primary_action: function(values) {
            frm.__updating = true;
            frm.set_value({
                custom_formula_basic_pct: values.basic_pct,
                custom_formula_min_basic: values.min_basic,
                custom_formula_hra_pct: values.hra_pct,
                custom_formula_bonus_pct: values.bonus_pct,
                custom_formula_pf_ceiling: values.pf_ceiling,
                custom_formula_pf_ee_rate: values.pf_ee_rate,
                custom_formula_pf_er_rate: values.pf_er_rate,
                custom_formula_esi_ceiling: values.esi_ceiling,
                custom_formula_esi_ee_rate: values.esi_ee_rate,
                custom_formula_esi_er_rate: values.esi_er_rate
            }).then(() => {
                frm.__updating = false;
                calculate_and_set_breakdown(frm, true);
                d.hide();
                frappe.show_alert({ message: __('Formulas updated and breakdown recalculated!'), indicator: 'green' });
            });
        }
    });
    d.show();
}

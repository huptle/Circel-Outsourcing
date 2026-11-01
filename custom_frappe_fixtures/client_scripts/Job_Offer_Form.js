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

            frm.add_custom_button(__('📄 Download Appointment Letter (PDF)'), function() {
                const url = '/api/method/frappe.utils.print_format.download_pdf?doctype=Job%20Offer&name=' + encodeURIComponent(frm.doc.name) + '&format=Exact%20Corporate%20Appointment%20Letter&no_letterhead=0';
                window.open(url, '_blank');
            });

            // View Print Format Preview
            frm.add_custom_button(__('👁️ View Offer Letter'), function() {
                frappe.set_route('print', 'Job Offer', frm.doc.name);
            });
        }

        // Formula editing & calculation buttons
        frm.add_custom_button(__('⚙️ Customize Salary Formulas & Rules'), function() {
            open_formula_modal(frm);
        }, __('Compensation'));

        frm.add_custom_button(__('⚡ Auto-Calculate from Gross / CTC'), function() {
            calculate_and_set_breakdown(frm, true, frm.doc.custom_ctc ? 'custom_ctc' : 'custom_monthly_remuneration');
        }, __('Compensation'));

        // Initialize formula defaults if empty
        ensure_formula_defaults(frm);
    },

    custom_monthly_remuneration: function(frm) {
        if (frm.__updating) return;
        calculate_and_set_breakdown(frm, false, 'custom_monthly_remuneration');
    },

    custom_ctc: function(frm) {
        if (frm.__updating) return;
        calculate_and_set_breakdown(frm, false, 'custom_ctc');
    },

    // Formula changes trigger re-calculation
    custom_formula_basic_pct: function(frm) { if (!frm.__updating) calculate_and_set_breakdown(frm, true); },
    custom_formula_hra_pct: function(frm) { if (!frm.__updating) calculate_and_set_breakdown(frm, true); },
    custom_formula_bonus_pct: function(frm) { if (!frm.__updating) calculate_and_set_breakdown(frm, true); },
    custom_formula_conveyance_pct: function(frm) { if (!frm.__updating) calculate_and_set_breakdown(frm, true); },
    custom_formula_pf_ceiling: function(frm) { if (!frm.__updating) calculate_and_set_breakdown(frm, true); },
    custom_formula_pf_er_rate: function(frm) { if (!frm.__updating) calculate_and_set_breakdown(frm, true); },
    custom_formula_esi_ceiling: function(frm) { if (!frm.__updating) calculate_and_set_breakdown(frm, true); },
    custom_formula_esi_er_rate: function(frm) { if (!frm.__updating) calculate_and_set_breakdown(frm, true); },
    custom_formula_gratuity_pct: function(frm) { if (!frm.__updating) calculate_and_set_breakdown(frm, true); },
    custom_formula_medical_amt: function(frm) { if (!frm.__updating) calculate_and_set_breakdown(frm, true); },

    // Manual component adjustments update totals reactively without wiping user inputs
    custom_basic: function(frm) { if (!frm.__updating) recalculate_totals_from_fields(frm); },
    custom_hra: function(frm) { if (!frm.__updating) recalculate_totals_from_fields(frm); },
    custom_bonus: function(frm) { if (!frm.__updating) recalculate_totals_from_fields(frm); },
    custom_conveyance: function(frm) { if (!frm.__updating) recalculate_totals_from_fields(frm); },
    custom_other_allowances: function(frm) { if (!frm.__updating) recalculate_totals_from_fields(frm); },
    custom_pf_employer: function(frm) { if (!frm.__updating) recalculate_totals_from_fields(frm); },
    custom_esi_employer: function(frm) { if (!frm.__updating) recalculate_totals_from_fields(frm); },
    custom_gratuity: function(frm) { if (!frm.__updating) recalculate_totals_from_fields(frm); },
    custom_medical: function(frm) { if (!frm.__updating) recalculate_totals_from_fields(frm); }
});

function ensure_formula_defaults(frm) {
    if (!frm.doc.custom_formula_basic_pct) {
        frm.__updating = true;
        frm.set_value({
            custom_formula_basic_pct: 50.0,
            custom_formula_hra_pct: 50.0,
            custom_formula_bonus_pct: 8.33,
            custom_formula_conveyance_pct: 10.0,
            custom_formula_pf_ceiling: 25000.0,
            custom_formula_pf_ee_rate: 12.0,
            custom_formula_pf_er_rate: 12.0,
            custom_formula_esi_ceiling: 21000.0,
            custom_formula_esi_ee_rate: 0.75,
            custom_formula_esi_er_rate: 4.0,
            custom_formula_gratuity_pct: 4.81,
            custom_formula_medical_amt: 2000.0,
            custom_probation: frm.doc.custom_probation || '6 Months',
            custom_notice_period: frm.doc.custom_notice_period || '1 Month'
        }).then(() => {
            frm.__updating = false;
        });
    }
}

function calculate_and_set_breakdown(frm, force, changed_field) {
    const raw_ctc = flt(frm.doc.custom_ctc);
    let m_gross = flt(frm.doc.custom_monthly_remuneration) || flt(frm.doc.custom_gross_salary);

    const med_amt = frm.doc.custom_formula_medical_amt !== undefined && frm.doc.custom_formula_medical_amt !== null && frm.doc.custom_formula_medical_amt !== '' 
                    ? flt(frm.doc.custom_formula_medical_amt) : 2000.0;

    // If CTC was edited, or Gross isn't present, derive Gross from CTC
    if (changed_field === 'custom_ctc' || (!m_gross && raw_ctc)) {
        if (!raw_ctc) return;
        const m_ctc = raw_ctc > 60000 ? (raw_ctc / 12) : raw_ctc;
        let g = 0;
        if (m_ctc <= (21000 * 1.12405 + med_amt)) {
            g = (m_ctc - med_amt) / 1.12405;
        } else if (m_ctc <= (50000 * 1.08405 + med_amt)) {
            g = (m_ctc - med_amt) / 1.08405;
        } else {
            g = (m_ctc - (25000 * 0.12 + med_amt)) / 1.02405;
        }
        m_gross = Math.round(Math.max(0, g));
    }

    if (!m_gross) return;

    // Read configured formula parameters matching Excel Compensation Structure
    const basic_pct = flt(frm.doc.custom_formula_basic_pct) || 50.0;
    const hra_pct = flt(frm.doc.custom_formula_hra_pct) || 50.0;
    const bonus_pct = flt(frm.doc.custom_formula_bonus_pct) || 8.33;
    const conv_pct = flt(frm.doc.custom_formula_conveyance_pct) || 10.0;
    const pf_ceiling = flt(frm.doc.custom_formula_pf_ceiling) || 25000.0;
    const pf_er_rate = flt(frm.doc.custom_formula_pf_er_rate) || 12.0;
    const pf_ee_rate = flt(frm.doc.custom_formula_pf_ee_rate) || 12.0;
    const esi_ceiling = flt(frm.doc.custom_formula_esi_ceiling) || 21000.0;
    const esi_er_rate = flt(frm.doc.custom_formula_esi_er_rate) || 4.0;
    const grat_pct = flt(frm.doc.custom_formula_gratuity_pct) || 4.81;

    // 1. Basic = ROUND(basic_pct * Gross, 0)
    const m_basic = Math.round(m_gross * (basic_pct / 100.0));

    // 2. HRA = ROUND(Basic * (hra_pct / 100), 0)
    const m_hra = Math.round(m_basic * (hra_pct / 100.0));

    // 3. Bonus = ROUND(Basic * (bonus_pct / 100), 0)
    const m_bonus = Math.round(m_basic * (bonus_pct / 100.0));

    // 4. Conveyance Allowance = ROUND(Basic * (conv_pct / 100), 0)
    const m_conv = Math.round(m_basic * (conv_pct / 100.0));

    // 5. Other Allowance = ROUND(Gross - Bonus - Conveyance - (Basic + HRA), 0)
    let m_other = Math.round(m_gross - m_bonus - m_conv - (m_basic + m_hra));
    if (m_other < 0) {
        m_other = 0;
        m_gross = m_basic + m_hra + m_bonus + m_conv;
    }

    // 6. Employer PF Contribution = IF(Basic <= pf_ceiling, Basic * pf_rate%, pf_ceiling * pf_rate%)
    const pf_wage = Math.min(m_basic, pf_ceiling);
    const m_pf_er = Math.round(pf_wage * (pf_rate / 100.0));
    const m_pf_ee = Math.round(pf_wage * (pf_ee_rate / 100.0));

    // 7. ESI Total Contribution (4%) = ROUNDUP(IF(Gross > esi_ceiling, 0, Gross * esi_rate%), 0)
    const m_esi_total = m_gross > esi_ceiling ? 0 : Math.ceil(m_gross * (esi_rate / 100.0));
    const m_esi_ee = m_gross > esi_ceiling ? 0 : Math.round(m_gross * 0.0075);

    // 8. Gratuity = ROUND((grat_pct * Basic) / 100, 0)
    const m_gratuity = Math.round(m_basic * (grat_pct / 100.0));

    // 9. Medical = Fixed (default 2000)
    const m_medical = Math.round(med_amt);

    // 10. Fixed Compensation (A) = Gross + Employer PF + ESI + Gratuity + Medical
    const m_fixed_comp = Math.round(m_gross + m_pf_er + m_esi_total + m_gratuity + m_medical);

    // 11. Total Cost to Company (CTC) Annual = Fixed Compensation * 12
    const ann_ctc = Math.round(m_fixed_comp * 12);

    // 12. Take Home (Exclusive of TDS) = Gross - PF - Gratuity - ESI
    const m_take_home = Math.round(m_gross - m_pf_er - m_gratuity - m_esi_total);

    frm.__updating = true;
    frm.set_value({
        custom_monthly_remuneration: m_gross,
        custom_gross_salary: m_gross,
        custom_basic: m_basic,
        custom_hra: m_hra,
        custom_bonus: m_bonus,
        custom_conveyance: m_conv,
        custom_other_allowances: m_other,
        custom_pf_employer: m_pf_er,
        custom_pf_employee: m_pf_ee,
        custom_esi_employer: m_esi_total,
        custom_esi_employee: m_esi_ee,
        custom_gratuity: m_gratuity,
        custom_medical: m_medical,
        custom_fixed_compensation: m_fixed_comp,
        custom_ctc: ann_ctc,
        custom_net_salary: m_take_home,
        custom_probation: frm.doc.custom_probation || '6 Months',
        custom_notice_period: frm.doc.custom_notice_period || '1 Month'
    }).then(() => {
        frm.__updating = false;
    });
}

function recalculate_totals_from_fields(frm) {
    // When any individual component is manually edited by the user:
    const b = flt(frm.doc.custom_basic);
    const hra = flt(frm.doc.custom_hra);
    const bonus = flt(frm.doc.custom_bonus);
    const conv = flt(frm.doc.custom_conveyance);
    const other = flt(frm.doc.custom_other_allowances);
    const gross = Math.round(b + hra + bonus + conv + other);

    const pf_er = flt(frm.doc.custom_pf_employer);
    const esi_total = flt(frm.doc.custom_esi_employer);
    const gratuity = flt(frm.doc.custom_gratuity);
    const medical = flt(frm.doc.custom_medical);

    // Fixed Compensation (A) = Gross + Employer PF + ESI + Gratuity + Medical
    const fixed_comp = Math.round(gross + pf_er + esi_total + gratuity + medical);
    const ann_ctc = Math.round(fixed_comp * 12);

    // Take Home (Exclusive of TDS) = Gross - PF - Gratuity - ESI
    const take_home = Math.round(gross - pf_er - gratuity - esi_total);

    frm.__updating = true;
    frm.set_value({
        custom_gross_salary: gross,
        custom_monthly_remuneration: gross,
        custom_fixed_compensation: fixed_comp,
        custom_ctc: ann_ctc,
        custom_net_salary: take_home
    }).then(() => {
        frm.__updating = false;
    });
}

function open_formula_modal(frm) {
    const d = new frappe.ui.Dialog({
        title: __('⚙️ Customize Salary Compensation Structure & Rules'),
        fields: [
            { fieldtype: 'Section Break', label: __('Earnings Formulas (% of Gross / Basic)') },
            { fieldtype: 'Percent', fieldname: 'basic_pct', label: __('Basic Salary % of Total Gross'), default: frm.doc.custom_formula_basic_pct || 50.0 },
            { fieldtype: 'Percent', fieldname: 'hra_pct', label: __('HRA % of Basic Salary'), default: frm.doc.custom_formula_hra_pct || 50.0 },
            { fieldtype: 'Percent', fieldname: 'bonus_pct', label: __('Bonus % of Basic Salary'), default: frm.doc.custom_formula_bonus_pct || 8.33 },
            { fieldtype: 'Percent', fieldname: 'conveyance_pct', label: __('Conveyance Allowance % of Basic'), default: frm.doc.custom_formula_conveyance_pct || 10.0 },
            { fieldtype: 'Column Break' },
            { fieldtype: 'Section Break', label: __('Statutory Retirals & Benefits') },
            { fieldtype: 'Currency', fieldname: 'pf_ceiling', label: __('PF Wage Ceiling Limit (INR)'), default: frm.doc.custom_formula_pf_ceiling || 25000.0 },
            { fieldtype: 'Percent', fieldname: 'pf_er_rate', label: __('Employer PF Contribution %'), default: frm.doc.custom_formula_pf_er_rate || 12.0 },
            { fieldtype: 'Currency', fieldname: 'esi_ceiling', label: __('ESI Wage Limit (INR)'), default: frm.doc.custom_formula_esi_ceiling || 21000.0 },
            { fieldtype: 'Percent', fieldname: 'esi_er_rate', label: __('ESI Total Contribution % (4%)'), default: frm.doc.custom_formula_esi_er_rate || 4.0 },
            { fieldtype: 'Percent', fieldname: 'gratuity_pct', label: __('Gratuity % of Basic (4.81%)'), default: frm.doc.custom_formula_gratuity_pct || 4.81 },
            { fieldtype: 'Currency', fieldname: 'medical_amt', label: __('Medical Allowance Monthly (INR)'), default: frm.doc.custom_formula_medical_amt !== undefined ? frm.doc.custom_formula_medical_amt : 2000.0 },
            { fieldtype: 'Section Break', label: __('Terms & Tenures') },
            { fieldtype: 'Data', fieldname: 'probation', label: __('Probation Period'), default: frm.doc.custom_probation || '6 Months' },
            { fieldtype: 'Column Break' },
            { fieldtype: 'Data', fieldname: 'notice_period', label: __('Notice Period'), default: frm.doc.custom_notice_period || '1 Month' }
        ],
        primary_action_label: __('Save & Recalculate Breakdown'),
        primary_action: function(values) {
            frm.__updating = true;
            frm.set_value({
                custom_formula_basic_pct: values.basic_pct,
                custom_formula_hra_pct: values.hra_pct,
                custom_formula_bonus_pct: values.bonus_pct,
                custom_formula_conveyance_pct: values.conveyance_pct,
                custom_formula_pf_ceiling: values.pf_ceiling,
                custom_formula_pf_er_rate: values.pf_er_rate,
                custom_formula_esi_ceiling: values.esi_ceiling,
                custom_formula_esi_er_rate: values.esi_er_rate,
                custom_formula_gratuity_pct: values.gratuity_pct,
                custom_formula_medical_amt: values.medical_amt,
                custom_probation: values.probation,
                custom_notice_period: values.notice_period
            }).then(() => {
                frm.__updating = false;
                calculate_and_set_breakdown(frm, true, frm.doc.custom_ctc ? 'custom_ctc' : 'custom_monthly_remuneration');
                d.hide();
                frappe.show_alert({ message: __('Compensation formulas updated & breakdown recalculated!'), indicator: 'green' });
            });
        }
    });
    d.show();
}

import streamlit as st
import random
import math

# --- Constants for Factor Options ---
STANDARD_FACTORS_VALUES = [10, 100, 1000] 
SCI_FACTORS_MAP = { # Value: (Unicode Label for markdown/text, Plain text label for buttons)
    0.001: ("10⁻³", "10^-3"), 
    0.01: ("10⁻²", "10^-2"),
    0.1: ("10⁻¹", "10^-1"),
    10: ("10¹", "10^1"),
    100: ("10²", "10^2"),
    1000: ("10³", "10^3"),
}

# 1. Conversion Data Store (Multi-step structure with Unicode superscripts for units)
CONVERSIONS = {
    "length": [
        {"from": "m", "to": "km", "base_factor": 1000, "power": 1, "operation_per_step": "÷"},
        {"from": "km", "to": "m", "base_factor": 1000, "power": 1, "operation_per_step": "×"},
        {"from": "cm", "to": "m", "base_factor": 100, "power": 1, "operation_per_step": "÷"},
        {"from": "m", "to": "cm", "base_factor": 100, "power": 1, "operation_per_step": "×"},
        {"from": "mm", "to": "cm", "base_factor": 10, "power": 1, "operation_per_step": "÷"},
        {"from": "cm", "to": "mm", "base_factor": 10, "power": 1, "operation_per_step": "×"},
        {"from": "m", "to": "mm", "base_factor": 1000, "power": 1, "operation_per_step": "×"},
        {"from": "mm", "to": "m", "base_factor": 1000, "power": 1, "operation_per_step": "÷"},
        {"from": "km", "to": "cm", "base_factor": 100000, "power": 1, "operation_per_step": "×"},
        {"from": "cm", "to": "km", "base_factor": 100000, "power": 1, "operation_per_step": "÷"},
    ],
    "mass": [
        {"from": "g", "to": "kg", "base_factor": 1000, "power": 1, "operation_per_step": "÷"},
        {"from": "kg", "to": "g", "base_factor": 1000, "power": 1, "operation_per_step": "×"},
        {"from": "mg", "to": "g", "base_factor": 1000, "power": 1, "operation_per_step": "÷"},
        {"from": "g", "to": "mg", "base_factor": 1000, "power": 1, "operation_per_step": "×"},
        {"from": "kg", "to": "mg", "base_factor": 1000000, "power": 1, "operation_per_step": "×"},
        {"from": "mg", "to": "kg", "base_factor": 1000000, "power": 1, "operation_per_step": "÷"},
    ],
    "volume_liquid": [
        {"from": "mL", "to": "L", "base_factor": 1000, "power": 1, "operation_per_step": "÷"},
        {"from": "L", "to": "mL", "base_factor": 1000, "power": 1, "operation_per_step": "×"},
        {"from": "L", "to": "kL", "base_factor": 1000, "power": 1, "operation_per_step": "÷"},
        {"from": "kL", "to": "L", "base_factor": 1000, "power": 1, "operation_per_step": "×"},
        {"from": "mL", "to": "kL", "base_factor": 1000000, "power": 1, "operation_per_step": "÷"},
        {"from": "kL", "to": "mL", "base_factor": 1000000, "power": 1, "operation_per_step": "×"},
    ],
    "area": [ 
        {"from": "cm²", "to": "m²", "base_factor": 100, "power": 2, "operation_per_step": "÷"},
        {"from": "m²", "to": "cm²", "base_factor": 100, "power": 2, "operation_per_step": "×"},
        {"from": "mm²", "to": "cm²", "base_factor": 10, "power": 2, "operation_per_step": "÷"},
        {"from": "cm²", "to": "mm²", "base_factor": 10, "power": 2, "operation_per_step": "×"},
        {"from": "m²", "to": "km²", "base_factor": 1000, "power": 2, "operation_per_step": "÷"},
        {"from": "km²", "to": "m²", "base_factor": 1000, "power": 2, "operation_per_step": "×"},
        {"from": "mm²", "to": "m²", "base_factor": 1000, "power": 2, "operation_per_step": "÷"},
        {"from": "m²", "to": "mm²", "base_factor": 1000, "power": 2, "operation_per_step": "×"},
    ],
    "volume_metric_cubed": [ 
        {"from": "cm³", "to": "m³", "base_factor": 100, "power": 3, "operation_per_step": "÷"},
        {"from": "m³", "to": "cm³", "base_factor": 100, "power": 3, "operation_per_step": "×"},
        {"from": "mm³", "to": "cm³", "base_factor": 10, "power": 3, "operation_per_step": "÷"},
        {"from": "cm³", "to": "mm³", "base_factor": 10, "power": 3, "operation_per_step": "×"},
        {"from": "m³", "to": "km³", "base_factor": 1000, "power": 3, "operation_per_step": "÷"},
        {"from": "km³", "to": "m³", "base_factor": 1000, "power": 3, "operation_per_step": "×"},
        {"from": "mm³", "to": "m³", "base_factor": 1000, "power": 3, "operation_per_step": "÷"},
        {"from": "m³", "to": "mm³", "base_factor": 1000, "power": 3, "operation_per_step": "×"},
        {"from": "cm³", "to": "mL", "base_factor": 1, "power": 1, "operation_per_step": "×"},
        {"from": "mL", "to": "cm³", "base_factor": 1, "power": 1, "operation_per_step": "×"},
        {"from": "m³", "to": "L", "base_factor": 1000, "power": 1, "operation_per_step": "×"},
        {"from": "L", "to": "m³", "base_factor": 1000, "power": 1, "operation_per_step": "÷"},
    ]
}

# --- Helper Function for Unicode Superscripts ---
def get_unicode_superscript(exponent_val_str):
    superscript_map = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", 
                       "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", 
                       "-": "⁻", "+": "⁺"}
    return "".join(superscript_map.get(char, char) for char in exponent_val_str)

# --- Helper Function for Formatting Numbers ---
def format_number_display(num_val_input, sci_notation_enabled=False, for_button_label=False):
    if isinstance(num_val_input, str) and num_val_input in ["×", "÷"]:
        return num_val_input
    try:
        num_val = float(num_val_input)
    except (ValueError, TypeError):
        return str(num_val_input) 

    if math.isnan(num_val) or math.isinf(num_val):
        return str(num_val)

    integer_tolerance = 1e-9 
    if math.isclose(num_val, round(num_val), rel_tol=0, abs_tol=integer_tolerance):
        num_val = float(round(num_val)) 

    if sci_notation_enabled:
        if num_val == 0: return "0"
        if not math.isclose(num_val, 0, abs_tol=integer_tolerance) and num_val in SCI_FACTORS_MAP:
            unicode_label_markdown, unicode_label_button = SCI_FACTORS_MAP[num_val]
            return unicode_label_button if for_button_label else unicode_label_markdown
        
        exponent = math.floor(math.log10(abs(num_val)))
        mantissa = num_val / (10**exponent)

        if math.isclose(mantissa, round(mantissa), abs_tol=integer_tolerance):
            mantissa_str = str(int(round(mantissa)))
        else:
            if abs(mantissa) >= 100: mantissa_str = f"{mantissa:.0f}"
            elif abs(mantissa) >= 10: mantissa_str = f"{mantissa:.1f}".rstrip('0').rstrip('.')
            elif abs(mantissa) >= 1: mantissa_str = f"{mantissa:.2f}".rstrip('0').rstrip('.')
            else: 
                mantissa_str = f"{mantissa:.2f}".rstrip('0').rstrip('.')
                if mantissa_str == "0" and not math.isclose(mantissa, 0):
                     mantissa_str = f"{mantissa:.3f}".rstrip('0').rstrip('.')
                if mantissa_str == "0" and not math.isclose(mantissa, 0):
                     mantissa_str = f"{mantissa:.4f}".rstrip('0').rstrip('.')
        
        try: # Check for 1 or -1 mantissa to simplify display
            mantissa_float_for_check = float(mantissa_str)
            if math.isclose(mantissa_float_for_check, 1.0, abs_tol=integer_tolerance) and exponent != 0:
                return f"10{get_unicode_superscript(str(exponent))}"
            if math.isclose(mantissa_float_for_check, -1.0, abs_tol=integer_tolerance) and exponent != 0:
                return f"-10{get_unicode_superscript(str(exponent))}"
        except ValueError: pass

        if exponent == 0: return mantissa_str
        return f"{mantissa_str} × 10{get_unicode_superscript(str(exponent))}"
    else: 
        if num_val == int(num_val):
            return f"{int(num_val):,}".replace(",", " ") 
        else:
            if abs(num_val) < 0.00001 and not math.isclose(num_val,0,abs_tol=integer_tolerance): s = f"{num_val:.7f}"
            elif abs(num_val) < 0.001 and not math.isclose(num_val,0,abs_tol=integer_tolerance): s = f"{num_val:.5f}"
            elif abs(num_val) < 1 and not math.isclose(num_val,0,abs_tol=integer_tolerance): s = f"{num_val:.4f}"
            else: s = f"{num_val:.2f}" 
            
            s = s.rstrip('0').rstrip('.')
            if not s or s == "-": s = "0" 
            if '.' in s:
                integer_part_str, decimal_part_str = s.split('.', 1)
                try: 
                    integer_part_formatted = f"{int(float(integer_part_str)):,}".replace(",", " ") if integer_part_str and integer_part_str != "-" else "0"
                    if integer_part_str == "-": integer_part_formatted = "-0" 
                except ValueError: 
                    integer_part_formatted = "0" if not (integer_part_str and integer_part_str.startswith('-')) else "-0"
                return f"{integer_part_formatted}.{decimal_part_str}"
            else: 
                try: return f"{int(float(s)):,}".replace(",", " ")
                except ValueError: return "0"

# --- Streamlit Session State Initialization ---
def init_session_state():
    keys_to_init = {
        'current_question_data': {}, 'feedback_html_content': "", 'game_initialized': False,
        'student_sequence': [], 'sci_notation_enabled': False,
        'student_calculated_display_value': None, 'is_student_answer_correct': None
    }
    for key, default_value in keys_to_init.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# --- Helper to get available step options based on toggle ---
def get_current_available_steps(sci_notation_enabled):
    operations = [("×", "×")] 
    factors = []
    if sci_notation_enabled:
        sorted_sci_factors = sorted(SCI_FACTORS_MAP.items(), key=lambda item: item[0])
        for actual_value, labels_tuple in sorted_sci_factors:
            _, plain_text_label_for_button = labels_tuple 
            factors.append((plain_text_label_for_button, actual_value)) 
    else:
        operations.append(("÷", "÷")) 
        sorted_standard_factors = sorted(STANDARD_FACTORS_VALUES)
        for actual_value in sorted_standard_factors:
            display_label_for_button = format_number_display(actual_value, False, for_button_label=True) 
            factors.append((display_label_for_button, actual_value))
    return operations, factors

# --- Core Application Logic Functions ---
def generate_question():
    st.session_state.feedback_html_content = ""
    st.session_state.student_sequence = [] 
    st.session_state.student_calculated_display_value = None 
    st.session_state.is_student_answer_correct = None    
    
    category_name = random.choice(list(CONVERSIONS.keys()))
    conversion = random.choice(CONVERSIONS[category_name])
    base_factor, power, op_per_step = conversion["base_factor"], conversion["power"], conversion["operation_per_step"]

    if op_per_step == "÷": 
        eff_total_factor = base_factor ** power
        if eff_total_factor > 100000: base_val = random.uniform(0.1, 50) * eff_total_factor * random.choice([0.1, 1, 10])
        elif eff_total_factor > 1000: base_val = random.uniform(1, 500) * eff_total_factor * random.choice([0.01,0.1,1,10])/random.choice([1,10,100])
        else: base_val = random.uniform(1, 1000) * random.choice([0.1,1,10]) * eff_total_factor
    else: 
        if power >=3 and base_factor >=1000: base_val = random.uniform(0.00001, 0.1) 
        elif power >=2 and base_factor >=100: base_val = random.uniform(0.01, 50)
        else: base_val = random.uniform(0.1, 500) / (base_factor ** random.randint(0, power if power > 0 else 1))
        if base_factor > 100 and power > 1 : base_val /= random.choice([1,10]) 

    start_value_raw = base_val 
    if abs(start_value_raw) < 1e-12 and base_val != 0: start_value_raw = 1e-9 if base_val > 0 else -1e-9
    min_val, max_val = 1e-9, 1e12 
    start_value_raw = max(min(start_value_raw, max_val), min_val) if start_value_raw > 0 else start_value_raw
    start_value_raw = min(max(start_value_raw, -max_val), -min_val) if start_value_raw < 0 else start_value_raw

    current_val = start_value_raw
    for _ in range(power):
        if op_per_step == "÷":
            if base_factor == 0: current_val = float('inf'); break
            current_val /= base_factor
        else: current_val *= base_factor
    correct_answer_raw = current_val
    
    st.session_state.current_question_data = {
        "from_unit": conversion['from'], "to_unit": conversion['to'], "start_value_raw": start_value_raw, 
        "base_factor_correct": base_factor, "power_correct": power, "operation_per_step_correct": op_per_step,
        "correct_answer_raw": correct_answer_raw 
    }
    st.session_state.game_initialized = True

def handle_available_option_click(option_actual_value): 
    st.session_state.student_calculated_display_value = None 
    st.session_state.is_student_answer_correct = None
    is_op_clicked = isinstance(option_actual_value, str) and option_actual_value in ["×", "÷"]
    expecting_operator = len(st.session_state.student_sequence) % 2 == 0
    
    valid_append = False
    if expecting_operator:
        if is_op_clicked: 
            if st.session_state.sci_notation_enabled and option_actual_value == "÷":
                st.toast("Division (÷) not used in Sci. Notation. Use × with 10⁻ˣ.", icon="ℹ️")
            else: valid_append = True
        else: st.toast("Invalid. Expected an operation (× or ÷).", icon="🚫")
    else: 
        if not is_op_clicked: valid_append = True
        else: st.toast("Invalid. Expected a numerical factor.", icon="🚫")
    if valid_append: st.session_state.student_sequence.append(option_actual_value)

def remove_from_sequence_callback(index_in_sequence): 
    st.session_state.student_calculated_display_value = None 
    st.session_state.is_student_answer_correct = None
    if 0 <= index_in_sequence < len(st.session_state.student_sequence):
        st.session_state.student_sequence.pop(index_in_sequence)

def on_submit_button_clicked():
    current_feedback_html = "" 
    cqd = st.session_state.current_question_data
    student_seq = st.session_state.student_sequence
    sci_on = st.session_state.sci_notation_enabled
    
    if not student_seq: 
        st.toast("Please build your calculation sequence first.", icon="🤔")
        st.session_state.student_calculated_display_value = "___" 
        st.session_state.is_student_answer_correct = None; return
    if len(student_seq) % 2 != 0 : 
        st.toast("Sequence incomplete. Expected a factor after the last operation.", icon="🤔")
        st.session_state.student_calculated_display_value = "Incomplete"
        st.session_state.is_student_answer_correct = False; return

    current_calc_val = cqd["start_value_raw"]
    submitted_display_sequence_for_feedback = [format_number_display(cqd["start_value_raw"], sci_on)]

    try:
        for i in range(0, len(student_seq), 2):
            op_str = student_seq[i]
            if i + 1 >= len(student_seq): 
                current_feedback_html = "<p style='color:red; font-weight:bold;'>Seq. Error!</p>"
                st.session_state.student_calculated_display_value = "Seq. Error!"
                st.session_state.is_student_answer_correct = False; break 
            factor_actual_value = float(student_seq[i+1]) 
            factor_display_label_in_seq = format_number_display(factor_actual_value, sci_on, for_button_label=True)
            submitted_display_sequence_for_feedback.extend([op_str, factor_display_label_in_seq])

            if op_str == "÷":
                if factor_actual_value == 0: 
                    current_feedback_html = "<p style='color:red;'>Error: Div by zero.</p>"
                    st.session_state.student_calculated_display_value = "Div by 0!"
                    st.session_state.is_student_answer_correct = False; break
                current_calc_val /= factor_actual_value
            elif op_str == "×": current_calc_val *= factor_actual_value
            else: 
                current_feedback_html = f"<p style='color:red;'>Error: Invalid op '{op_str}'.</p>"
                st.session_state.student_calculated_display_value = "Op Error!"
                st.session_state.is_student_answer_correct = False; break
        else: 
            student_final_result_raw = current_calc_val
            correct_answer_raw = cqd["correct_answer_raw"]
            is_correct = math.isclose(student_final_result_raw, correct_answer_raw, rel_tol=1e-7, abs_tol=1e-9)
            st.session_state.is_student_answer_correct = is_correct

            if is_correct: st.session_state.student_calculated_display_value = format_number_display(correct_answer_raw, sci_on)
            else: st.session_state.student_calculated_display_value = format_number_display(student_final_result_raw, sci_on)
            
            current_feedback_html += f"<p>You submitted: {' '.join(submitted_display_sequence_for_feedback)}</p>"
            current_feedback_html += f"<p>Calculating... = {st.session_state.student_calculated_display_value}</p>"
            result_unit, correct_answer_display = cqd['to_unit'], format_number_display(correct_answer_raw, sci_on)

            if is_correct:
                current_feedback_html += f"<p style='color:green; font-weight:bold;'>Result: {st.session_state.student_calculated_display_value} {result_unit}. Correct! 🎉</p>"
            else:
                current_feedback_html += f"<p style='color:red; font-weight:bold;'>Result: {st.session_state.student_calculated_display_value} {result_unit}. Not quite. 🤔</p>"
                current_feedback_html += "<hr><p><strong>Correct steps (ideal):</strong></p>" 
                correct_op, correct_bf_val, power, sv_raw = cqd['operation_per_step_correct'], cqd['base_factor_correct'], cqd['power_correct'], cqd['start_value_raw']
                from_u, to_u = cqd['from_unit'], cqd['to_unit']
                current_step_val_raw = sv_raw
                current_feedback_html += f"<p>1. Start: {format_number_display(sv_raw, sci_on)} {from_u}</p>"
                correct_bf_display = format_number_display(correct_bf_val, sci_on, for_button_label=True) 
                for i_step in range(power):
                    current_feedback_html += f"<p>{i_step+2}. Ideal Step {i_step+1}: ...{'divide by' if correct_op == '÷' else 'multiply by'} {correct_bf_display}.</p>"
                    lhs_disp = format_number_display(current_step_val_raw, sci_on)
                    if correct_op == "÷": current_step_val_raw /= correct_bf_val
                    else: current_step_val_raw *= correct_bf_val
                    rhs_disp = format_number_display(current_step_val_raw, sci_on)
                    current_feedback_html += f"<p>   Calc: {lhs_disp} {correct_op} {correct_bf_display} = {rhs_disp}</p>"
                current_feedback_html += f"<p>{i_step+3}. Ideal Final: <strong>{correct_answer_display} {to_u}</strong></p>"
        st.session_state.feedback_html_content = current_feedback_html
    except ValueError:
        st.session_state.student_calculated_display_value = "Factor Error!"
        st.session_state.is_student_answer_correct = False
        st.session_state.feedback_html_content = "<p style='color:red;'>Error: Invalid factor in sequence.</p>"
    except Exception as e:
        st.session_state.student_calculated_display_value = "App Error!"
        st.session_state.is_student_answer_correct = False
        st.session_state.feedback_html_content = f"<p style='color:red;'>Unexpected error: {e}</p>"

def on_new_question_clicked(): 
    generate_question()
    st.rerun() 

# --- Main App Layout and Execution ---
def main():
    st.set_page_config(page_title="Unit Converter Practice", layout="wide") 
    st.title("👩‍🔬 Interactive Unit Converter 📐")
    init_session_state() 
    st.session_state.sci_notation_enabled = st.toggle(
        "Enable Scientific Notation (e.g., 10², 1.23 × 10⁵)", 
        value=st.session_state.get('sci_notation_enabled', False), key="sci_notation_toggle_widget",
        help="Toggles number display and available factor options. Division (÷) is hidden in scientific mode; use multiplication by negative powers of 10 (e.g., × 10⁻¹)."
    )
    sci_on = st.session_state.sci_notation_enabled 
    st.markdown("Build the conversion step-by-step. Click an item in your calculation to remove it.")

    if not st.session_state.game_initialized: generate_question() 
    cqd = st.session_state.get('current_question_data', {})
    
    if cqd and "start_value_raw" in cqd:
        start_val_disp_q = format_number_display(cqd["start_value_raw"], sci_on)
        st.markdown(f"### Convert: {start_val_disp_q} {cqd['from_unit']} to {cqd['to_unit']}", unsafe_allow_html=True)
    else: 
        st.markdown("### Loading question...")
        if st.button("Start / Reload Question", key="manual_start_btn_main_top_v8"): 
            generate_question(); st.rerun()

    st.markdown("---") 
    st.markdown("**Your current calculation:**")
    
    if cqd and "start_value_raw" in cqd: 
        # --- Display student's calculation sequence (Part 1) ---
        num_sequence_items = len(st.session_state.student_sequence)
        # Define relative widths: start_value wider, buttons narrower
        col_widths_spec_seq = [2] + [1] * num_sequence_items # Start value, then narrower for each button
        
        if col_widths_spec_seq: 
            seq_cols_line1 = st.columns(col_widths_spec_seq)
            with seq_cols_line1[0]:
                st.markdown(f"<div style='padding-top:0.5rem; font-size:1.1em; white-space:nowrap; text-align:left;'>{format_number_display(cqd['start_value_raw'], sci_on)}</div>", unsafe_allow_html=True)
            for i, item_val in enumerate(st.session_state.student_sequence):
                if i + 1 < len(seq_cols_line1): 
                    with seq_cols_line1[i+1]: 
                        st.button(format_number_display(item_val, sci_on, for_button_label=True), 
                                  key=f"rem_btn_seq_{i}", 
                                  on_click=remove_from_sequence_callback, args=(i,), 
                                  help="Remove this step", use_container_width=False) 
        else: 
             st.markdown(f"<div style='padding-top:0.5rem; font-size:1.1em; white-space:nowrap; text-align:left;'>{format_number_display(cqd['start_value_raw'], sci_on)}</div>", unsafe_allow_html=True)

        # --- Display Submit ("=") button, result, and target unit (Part 2, new line) ---
        submit_result_cols = st.columns([0.6, 2, 1.5]) 
        with submit_result_cols[0]: 
            st.button("=", key="submit_equals_button_main_line_v8", on_click=on_submit_button_clicked, 
                      help="Submit your calculation", type="primary", use_container_width=True, disabled=False) 
        with submit_result_cols[1]: 
            res_disp = st.session_state.student_calculated_display_value if st.session_state.student_calculated_display_value is not None else "___"
            res_color = "grey" 
            if st.session_state.is_student_answer_correct is True: res_color = "green"
            elif st.session_state.is_student_answer_correct is False: res_color = "red"
            st.markdown(f"<div style='padding-top:0.5rem; font-weight:bold; font-size:1.1em; color:{res_color}; white-space:nowrap; text-align:left;'>{res_disp}</div>", unsafe_allow_html=True)
        with submit_result_cols[2]: 
            st.markdown(f"<div style='padding-top:0.5rem; font-size:1.1em; white-space:nowrap; text-align:left;'>{cqd['to_unit']}</div>", unsafe_allow_html=True)
    else: 
        st.caption("Waiting for question data to display calculation area.")

    st.markdown("---")
    st.write("**Available Operations & Factors:**")
    
    available_ops_buttons, available_factors_buttons = get_current_available_steps(sci_on)
    op_col, factor_col = st.columns([1, 3.5]) 

    with op_col:
        st.markdown("**Operations**")
        for disp_label, actual_val in available_ops_buttons:
            key_suffix = disp_label.replace("^","p").replace("⁻","m").replace(" ","")
            op_key = f"avail_op_btn_{str(actual_val)}_{key_suffix}_{random.random()}"
            st.button(disp_label, key=op_key, on_click=handle_available_option_click, args=(actual_val,), use_container_width=True, help=f"Add {disp_label}")
            
    with factor_col:
        st.markdown("**Factors**")
        num_factor_cols = 3 
        factor_rows = [available_factors_buttons[i:i + num_factor_cols] for i in range(0, len(available_factors_buttons), num_factor_cols)]
        for r_idx, row_tuples in enumerate(factor_rows):
            cols = st.columns(num_factor_cols)
            for c_idx, (disp_label, actual_val) in enumerate(row_tuples):
                key_suffix = disp_label.replace("^","p").replace("⁻","m").replace(" ","")
                factor_key = f"avail_factor_btn_{str(actual_val)}_{key_suffix}_{r_idx}_{c_idx}_{random.random()}"
                cols[c_idx].button(disp_label, key=factor_key, on_click=handle_available_option_click, args=(actual_val,), use_container_width=True, help=f"Add {disp_label}")
    
    st.markdown("---")
    if st.button("New Question", key="new_q_btn_bottom_v8", use_container_width=True): 
        on_new_question_clicked()
    if st.session_state.feedback_html_content:
        st.markdown("---")
        st.markdown("### Feedback & Calculation Steps:")
        st.markdown(st.session_state.feedback_html_content, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

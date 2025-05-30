import streamlit as st
import random
import time
import math

# 1. Conversion Data Store (Using "×" and "÷")
CONVERSIONS = {
    "length": [
        {"from": "m", "to": "km", "factor": 1000, "operation": "÷"},
        {"from": "km", "to": "m", "factor": 1000, "operation": "×"},
        {"from": "cm", "to": "m", "factor": 100, "operation": "÷"},
        {"from": "m", "to": "cm", "factor": 100, "operation": "×"},
        {"from": "mm", "to": "cm", "factor": 10, "operation": "÷"},
        {"from": "cm", "to": "mm", "factor": 10, "operation": "×"},
        {"from": "m", "to": "mm", "factor": 1000, "operation": "×"},
        {"from": "mm", "to": "m", "factor": 1000, "operation": "÷"},
        {"from": "km", "to": "cm", "factor": 100000, "operation": "×"},
        {"from": "cm", "to": "km", "factor": 100000, "operation": "÷"},
    ],
    "mass": [
        {"from": "g", "to": "kg", "factor": 1000, "operation": "÷"},
        {"from": "kg", "to": "g", "factor": 1000, "operation": "×"},
        {"from": "mg", "to": "g", "factor": 1000, "operation": "÷"},
        {"from": "g", "to": "mg", "factor": 1000, "operation": "×"},
        {"from": "kg", "to": "mg", "factor": 1000000, "operation": "×"},
        {"from": "mg", "to": "kg", "factor": 1000000, "operation": "÷"},
    ],
    "volume": [
        {"from": "mL", "to": "L", "factor": 1000, "operation": "÷"},
        {"from": "L", "to": "mL", "factor": 1000, "operation": "×"},
        {"from": "L", "to": "kL", "factor": 1000, "operation": "÷"},
        {"from": "kL", "to": "L", "factor": 1000, "operation": "×"},
        {"from": "mL", "to": "kL", "factor": 1000000, "operation": "÷"},
        {"from": "kL", "to": "mL", "factor": 1000000, "operation": "×"},
    ]
}

# --- Helper Function for Formatting Numbers ---
def format_number_display(num_val_str):
    if num_val_str in ["×", "÷"]:
        return num_val_str
    try:
        num_val = float(num_val_str)
        if math.isnan(num_val) or math.isinf(num_val): return num_val_str
        if num_val == int(num_val): return str(int(num_val))
        if (abs(num_val) < 0.0001 and num_val != 0) or abs(num_val) > 100000:
            return f"{num_val:.1e}"
        formatted_str = f"{num_val:.4f}".rstrip('0').rstrip('.')
        return formatted_str if formatted_str else "0"
    except ValueError:
        return num_val_str

# --- Streamlit Session State Initialization ---
def init_session_state():
    if 'current_question_data' not in st.session_state:
        st.session_state.current_question_data = {}
    if 'feedback_html_content' not in st.session_state:
        st.session_state.feedback_html_content = ""
    if 'game_initialized' not in st.session_state:
        st.session_state.game_initialized = False
    
    # For "moving buttons" feature
    if 'all_possible_options' not in st.session_state:
        st.session_state.all_possible_options = []
    if 'options_in_slots' not in st.session_state: # Represents the 3 slots: [opt1_val, opt2_val, opt3_val] or None
        st.session_state.options_in_slots = [None, None, None]
    if 'available_options_pool' not in st.session_state: # Options currently in the "available" pool
        st.session_state.available_options_pool = []
    # For highlighting invalid slot attempts
    if 'invalid_slot_attempt_idx' not in st.session_state:
        st.session_state.invalid_slot_attempt_idx = None

# --- Core Application Logic Functions ---

def generate_options_data():
    cqd = st.session_state.current_question_data
    correct_start_val_str = str(cqd["start_value"])
    correct_op_str = cqd["correct_operation_symbol"]
    correct_factor_str = str(cqd["correct_factor"])

    options_set = set()
    options_set.add(correct_start_val_str)
    options_set.add(correct_op_str)
    options_set.add(correct_factor_str)
    options_set.add("×" if correct_op_str == "÷" else "÷")

    numerical_distractors_pool = []
    sv = cqd["start_value"]
    cf = cqd["correct_factor"]
    for val in [sv, cf]:
        if val != 0:
            numerical_distractors_pool.extend([val / 10, val * 10, val / 100, val * 100, val / 2, val * 2])
    numerical_distractors_pool.extend([1, 10, 100, 1000, 0.1, 0.01, 0.5, 2, 5, 20, 50, 250, 500])
    
    random.shuffle(numerical_distractors_pool)
    for dist_num in numerical_distractors_pool:
        if len(options_set) >= 10: break # Generate a few more options for the pool
        if abs(dist_num) < 0.001 and dist_num != 0: dist_num_rounded = round(dist_num,5)
        elif abs(dist_num) < 1: dist_num_rounded = round(dist_num,3)
        else: dist_num_rounded = round(dist_num,2)
        if dist_num_rounded == int(dist_num_rounded): dist_num_rounded = int(dist_num_rounded)
        dist_num_str = str(dist_num_rounded)
        if dist_num_str not in options_set:
            options_set.add(dist_num_str)
            
    options_list = list(options_set)
    random.shuffle(options_list)
    
    st.session_state.all_possible_options = list(options_list)
    st.session_state.available_options_pool = list(options_list)
    st.session_state.options_in_slots = [None, None, None]
    st.session_state.invalid_slot_attempt_idx = None # Reset invalid highlight


def generate_question():
    st.session_state.feedback_html_content = ""
    st.session_state.invalid_slot_attempt_idx = None # Reset invalid highlight
    # Value generation logic
    category_name = random.choice(list(CONVERSIONS.keys()))
    conversion = random.choice(CONVERSIONS[category_name])
    if conversion["operation"] == "÷":
        base_val = random.randint(1, 500) * random.choice([1, 10, 0.1, 5, 0.5])
        if conversion["factor"] > 100: base_val *= random.choice([1, 1, 10, 2])
        else: base_val *= random.choice([1, 0.1, 0.01, 0.2])
    else: # "×"
        base_val = random.randint(1, 50) * random.choice([1, 0.1, 0.01, 0.001, 0.5, 0.2])
        if conversion["factor"] > 100: base_val *= random.choice([1, 0.1, 0.01, 0.001, 0.2])
        else: base_val *= random.choice([1, 10, 0.1, 2, 5])
    start_value = round(base_val, 5)
    if start_value == 0 and base_val != 0: 
        start_value = base_val if abs(base_val) > 1e-5 else (0.001 if base_val > 0 else -0.001)
    start_value = max(min(start_value, 1_000_000), 0.00001) if start_value > 0 else start_value
    start_value = min(max(start_value, -1_000_000), -0.00001) if start_value < 0 else start_value
    if abs(start_value) < 0.001 and start_value != 0: start_value = round(start_value,5) 
    elif abs(start_value) < 1: start_value = round(start_value,3)
    else: start_value = round(start_value,2)
    if start_value == int(start_value): start_value = int(start_value)
    correct_answer_val = 0
    if conversion["operation"] == "÷":
        if conversion["factor"] == 0: correct_answer_val = float('inf')
        else: correct_answer_val = start_value / conversion["factor"]
    else: # "×"
        correct_answer_val = start_value * conversion["factor"]
    if abs(correct_answer_val) < 0.00001 and correct_answer_val !=0 : correct_answer_val = round(correct_answer_val, 8)
    elif abs(correct_answer_val) < 1: correct_answer_val = round(correct_answer_val, 4)
    elif abs(correct_answer_val) < 100: correct_answer_val = round(correct_answer_val, 2)
    else: correct_answer_val = round(correct_answer_val, 1)
    if correct_answer_val == int(correct_answer_val): correct_answer_val = int(correct_answer_val)
    
    question_template_text = f"Convert: {format_number_display(str(start_value))} {conversion['from']} = _____ {conversion['to']}"

    st.session_state.current_question_data = {
        "question_template_text": question_template_text,
        "start_value": start_value, "from_unit": conversion['from'], "to_unit": conversion['to'],
        "correct_factor": conversion["factor"], "correct_operation_symbol": conversion["operation"],
        "correct_answer_value": correct_answer_val
    }
    generate_options_data() # This will also reset slots and available options

def rebuild_available_options_pool():
    all_opts = set(st.session_state.all_possible_options)
    opts_in_slots = set(s for s in st.session_state.options_in_slots if s is not None)
    current_available = list(all_opts - opts_in_slots)
    random.shuffle(current_available) 
    st.session_state.available_options_pool = current_available

def handle_available_option_click(option_value_clicked):
    try:
        target_slot_idx = st.session_state.options_in_slots.index(None) 
    except ValueError:
        st.toast("All answer slots are full!", icon="⚠️")
        st.session_state.invalid_slot_attempt_idx = None # Clear any previous highlight
        return

    is_op_clicked = option_value_clicked in ["×", "÷"]
    valid_placement = False
    expected_type_msg = ""

    if target_slot_idx == 0: 
        if not is_op_clicked: valid_placement = True
        else: expected_type_msg = "a number"
    elif target_slot_idx == 1: 
        if is_op_clicked: valid_placement = True
        else: expected_type_msg = "an operation ('×' or '÷')"
    elif target_slot_idx == 2: 
        if not is_op_clicked: valid_placement = True
        else: expected_type_msg = "a number"
    
    if valid_placement:
        st.session_state.options_in_slots[target_slot_idx] = option_value_clicked
        rebuild_available_options_pool()
        st.session_state.feedback_html_content = "" 
        st.session_state.invalid_slot_attempt_idx = None # Clear invalid highlight on valid move
    else:
        st.toast(f"Invalid. Expected {expected_type_msg} for the next slot.", icon="🚫")
        st.session_state.invalid_slot_attempt_idx = target_slot_idx # Set for highlight

def handle_slot_click(slot_idx_clicked):
    option_value_to_move_back = st.session_state.options_in_slots[slot_idx_clicked]
    if option_value_to_move_back is not None:
        st.session_state.options_in_slots[slot_idx_clicked] = None
        rebuild_available_options_pool() 
        st.session_state.feedback_html_content = "" 
        st.session_state.invalid_slot_attempt_idx = None # Clear invalid highlight

def on_submit_button_clicked():
    current_feedback_html = ""
    cqd = st.session_state.current_question_data
    st.session_state.invalid_slot_attempt_idx = None # Clear invalid highlight on submit
    
    if None in st.session_state.options_in_slots:
        st.session_state.feedback_html_content = "<p style='color:orange; font-weight:bold;'>Please fill all three slots in the answer.</p>"
        return

    val_str, op_str, factor_str = st.session_state.options_in_slots

    try:
        student_selected_start_val = float(val_str)
        student_selected_factor = float(factor_str)

        if abs(student_selected_start_val - cqd["start_value"]) > 1e-9:
            msg = (f"Oops! Your calculation must start with the given value: "
                   f"{format_number_display(str(cqd['start_value']))}. "
                   f"You started with {format_number_display(val_str)}.")
            current_feedback_html += f"<p style='color:red; font-weight:bold;'>{msg}</p>"
            current_feedback_html += "<p style='color:orange; font-weight:bold;'>The slots have been cleared. Please try again.</p>"
            st.session_state.options_in_slots = [None, None, None] 
            rebuild_available_options_pool() 
            st.session_state.feedback_html_content = current_feedback_html
            return

        current_feedback_html += f"<p>You submitted: {format_number_display(val_str)} {op_str} {format_number_display(factor_str)}</p>"
        st.session_state.feedback_html_content = current_feedback_html; time.sleep(0.7)

        student_result = None
        if op_str == "÷":
            if student_selected_factor == 0:
                current_feedback_html += "<p style='color:red; font-weight:bold;'>Error: Division by zero is not allowed.</p>"
                st.session_state.feedback_html_content = current_feedback_html; return
            student_result = student_selected_start_val / student_selected_factor
        elif op_str == "×":
            student_result = student_selected_start_val * student_selected_factor
        else: 
            current_feedback_html += "<p style='color:red; font-weight:bold;'>Error: Invalid operation in slots.</p>"
            st.session_state.feedback_html_content = current_feedback_html; return
        
        if abs(student_result) < 0.00001 and student_result !=0 : student_result_rounded = round(student_result, 8)
        elif abs(student_result) < 1: student_result_rounded = round(student_result, 4)
        elif abs(student_result) < 100: student_result_rounded = round(student_result, 2)
        else: student_result_rounded = round(student_result, 1)
        if student_result_rounded == int(student_result_rounded): student_result_rounded = int(student_result_rounded)
        
        current_feedback_html += f"<p>Calculating... {format_number_display(val_str)} {op_str} {format_number_display(factor_str)} = {format_number_display(str(student_result_rounded))}</p>"
        st.session_state.feedback_html_content = current_feedback_html; time.sleep(1.2)

        correct_ans_val = cqd["correct_answer_value"]
        is_correct = abs(student_result_rounded - correct_ans_val) < 1e-9
        result_unit = cqd['to_unit']

        if is_correct:
            msg = f"Result: {format_number_display(str(student_result_rounded))} {result_unit}. Correct! Well done! 🎉"
            current_feedback_html += f"<p style='color:green; font-weight:bold;'>{msg}</p>"
        else:
            msg = f"Result: {format_number_display(str(student_result_rounded))} {result_unit}. Not quite right. 🤔"
            current_feedback_html += f"<p style='color:red; font-weight:bold;'>{msg}</p>"
            st.session_state.feedback_html_content = current_feedback_html; time.sleep(0.8)
            current_feedback_html += "<hr><p><strong>Let's see the correct steps:</strong></p>"
            correct_op_sym, correct_fact_num, start_v_num = cqd['correct_operation_symbol'], cqd['correct_factor'], cqd['start_value']
            from_u, to_u = cqd['from_unit'], cqd['to_unit']
            current_feedback_html += f"<p>1. Start with: {format_number_display(str(start_v_num))} {from_u}</p>"
            st.session_state.feedback_html_content = current_feedback_html; time.sleep(0.7)
            explanation = f"2. To convert from {from_u} to {to_u}, you need to {'divide by' if correct_op_sym == '÷' else 'multiply by'} {format_number_display(str(correct_fact_num))}."
            current_feedback_html += f"<p>{explanation}</p>"
            st.session_state.feedback_html_content = current_feedback_html; time.sleep(1.2)
            current_feedback_html += f"<p>3. So, the calculation is: {format_number_display(str(start_v_num))} {correct_op_sym} {format_number_display(str(correct_fact_num))}</p>"
            st.session_state.feedback_html_content = current_feedback_html; time.sleep(0.7)
            current_feedback_html += f"<p>4. Which equals: <strong>{format_number_display(str(correct_ans_val))} {to_u}</strong></p>"
        st.session_state.feedback_html_content = current_feedback_html
    except ValueError:
        st.session_state.feedback_html_content = "<p style='color:red; font-weight:bold;'>Error processing numbers from slots. Please check selections.</p>"
    except Exception as e:
        st.session_state.feedback_html_content = f"<p style='color:red; font-weight:bold;'>An unexpected error occurred: {e}</p>"

def on_new_question_clicked():
    generate_question() 
    st.session_state.game_initialized = True # Ensure it's marked as initialized

# --- Main App Layout and Execution ---
def main():
    st.set_page_config(page_title="Unit Converter Practice", layout="wide") 
    st.title("👩‍🔬 Interactive Unit Converter 📐")
    st.markdown("Click options from the 'Available Options' pool to fill the slots in the question. Click an option in a slot to move it back.")

    init_session_state()

    if not st.session_state.game_initialized:
        generate_question()
        st.session_state.game_initialized = True

    cqd = st.session_state.get('current_question_data', {})
    st.markdown("---") 

    if cqd and "question_template_text" in cqd and "from_unit" in cqd and "to_unit" in cqd:
        question_template = cqd["question_template_text"]
        parts_around_placeholder = question_template.split("_____")
        q_prefix = parts_around_placeholder[0]
        q_suffix = parts_around_placeholder[1] if len(parts_around_placeholder) > 1 else ""
        q_col_widths = [3, 1.5, 1.5, 1.5, 2] 
        q_cols = st.columns(q_col_widths)
        
        with q_cols[0]:
            st.markdown(f"<div style='text-align: right; margin-top: 0.5rem; font-size: 1.2em;'>{q_prefix}</div>", unsafe_allow_html=True)

        for i in range(3): 
            with q_cols[i+1]:
                option_in_slot = st.session_state.options_in_slots[i]
                slot_style = "border: 1.5px dashed #AED6F1; background-color: #EBF5FB; text-align:center; padding: 0.4rem; margin:1px auto; height: 2.375rem; border-radius:0.25rem; width: 95%;"
                # Check if this slot had an invalid attempt
                if st.session_state.invalid_slot_attempt_idx == i and option_in_slot is None:
                    slot_style = "border: 2px solid red; background-color: #FADBD8; text-align:center; padding: 0.4rem; margin:1px auto; height: 2.375rem; border-radius:0.25rem; width: 95%;"

                if option_in_slot is not None:
                    st.button(
                        format_number_display(option_in_slot), 
                        key=f"slot_btn_{i}", 
                        on_click=handle_slot_click, 
                        args=(i,),
                        use_container_width=True
                    )
                else:
                    st.markdown(f"<div style='{slot_style}'></div>", unsafe_allow_html=True)
        
        with q_cols[-1]: 
            st.markdown(f"<div style='text-align: left; margin-top: 0.5rem; font-size: 1.2em;'>{q_suffix}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<h3>Loading question... Please wait.</h3>", unsafe_allow_html=True)
        if st.button("Force Reload Question", key="force_reload_question_btn"):
            st.session_state.game_initialized = False # Trigger re-generation
            st.rerun()

    st.markdown("---")
    st.write("**Available Options:**")
    available_options_pool = st.session_state.get('available_options_pool', [])
    if not available_options_pool:
        st.caption("All options are placed in slots above, or no options generated.")
    else:
        num_avail_cols = 5 
        rows_of_avail_buttons = [available_options_pool[i:i + num_avail_cols] for i in range(0, len(available_options_pool), num_avail_cols)]
        for r_idx, row_options in enumerate(rows_of_avail_buttons):
            cols_avail = st.columns(num_avail_cols)
            for c_idx, option_val_str in enumerate(row_options):
                button_label = format_number_display(option_val_str)
                unique_key = f"avail_btn_{option_val_str}_{r_idx}_{c_idx}_{random.random()}" # Ensure unique key if values repeat
                cols_avail[c_idx].button(
                    button_label, 
                    key=unique_key,
                    on_click=handle_available_option_click, 
                    args=(option_val_str,),
                    use_container_width=True
                )
    st.markdown("---")

    submit_col, new_q_col = st.columns([1,1]) 
    submit_disabled = (None in st.session_state.options_in_slots) 

    with submit_col:
        st.button("Submit Answer", on_click=on_submit_button_clicked, disabled=submit_disabled, use_container_width=True, type="primary")
    with new_q_col:
        st.button("New Question", on_click=on_new_question_clicked, use_container_width=True)

    if st.session_state.feedback_html_content:
        st.markdown("---")
        st.markdown("### Feedback & Calculation Steps:")
        st.markdown(st.session_state.feedback_html_content, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

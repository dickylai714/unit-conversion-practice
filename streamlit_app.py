import streamlit as st
import random
import time
import math

# 1. Conversion Data Store
# Added "area" and "volume_metric_cubed" categories with HTML superscripts for units.
# Renamed original "volume" to "volume_liquid" for clarity.
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
    "volume_liquid": [ # Renamed from "volume"
        {"from": "mL", "to": "L", "factor": 1000, "operation": "÷"},
        {"from": "L", "to": "mL", "factor": 1000, "operation": "×"},
        {"from": "L", "to": "kL", "factor": 1000, "operation": "÷"},
        {"from": "kL", "to": "L", "factor": 1000, "operation": "×"},
        {"from": "mL", "to": "kL", "factor": 1000000, "operation": "÷"},
        {"from": "kL", "to": "mL", "factor": 1000000, "operation": "×"},
    ],
    "area": [
        {"from": "cm<sup>2</sup>", "to": "m<sup>2</sup>", "factor": 10000, "operation": "÷"}, # 100^2
        {"from": "m<sup>2</sup>", "to": "cm<sup>2</sup>", "factor": 10000, "operation": "×"},
        {"from": "mm<sup>2</sup>", "to": "cm<sup>2</sup>", "factor": 100, "operation": "÷"},   # 10^2
        {"from": "cm<sup>2</sup>", "to": "mm<sup>2</sup>", "factor": 100, "operation": "×"},
        {"from": "m<sup>2</sup>", "to": "km<sup>2</sup>", "factor": 1000000, "operation": "÷"}, # 1000^2
        {"from": "km<sup>2</sup>", "to": "m<sup>2</sup>", "factor": 1000000, "operation": "×"},
        {"from": "mm<sup>2</sup>", "to": "m<sup>2</sup>", "factor": 1000000, "operation": "÷"}, # (1000)^2
        {"from": "m<sup>2</sup>", "to": "mm<sup>2</sup>", "factor": 1000000, "operation": "×"},
    ],
    "volume_metric_cubed": [
        {"from": "cm<sup>3</sup>", "to": "m<sup>3</sup>", "factor": 1000000, "operation": "÷"}, # 100^3
        {"from": "m<sup>3</sup>", "to": "cm<sup>3</sup>", "factor": 1000000, "operation": "×"},
        {"from": "mm<sup>3</sup>", "to": "cm<sup>3</sup>", "factor": 1000, "operation": "÷"},    # 10^3
        {"from": "cm<sup>3</sup>", "to": "mm<sup>3</sup>", "factor": 1000, "operation": "×"},
        {"from": "m<sup>3</sup>", "to": "km<sup>3</sup>", "factor": 1000000000, "operation": "÷"}, # 1000^3
        {"from": "km<sup>3</sup>", "to": "m<sup>3</sup>", "factor": 1000000000, "operation": "×"},
        {"from": "mm<sup>3</sup>", "to": "m<sup>3</sup>", "factor": 1000000000, "operation": "÷"}, # (1000)^3
        {"from": "m<sup>3</sup>", "to": "mm<sup>3</sup>", "factor": 1000000000, "operation": "×"},
        # Conversions between metric cubed and liquid volume
        {"from": "cm<sup>3</sup>", "to": "mL", "factor": 1, "operation": "×"}, # 1 cm^3 = 1 mL
        {"from": "mL", "to": "cm<sup>3</sup>", "factor": 1, "operation": "×"},
        {"from": "m<sup>3</sup>", "to": "L", "factor": 1000, "operation": "×"},    # 1 m^3 = 1000 L
        {"from": "L", "to": "m<sup>3</sup>", "factor": 1000, "operation": "÷"},
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
            return f"{num_val:.1e}" # Use scientific notation for very small or very large numbers
        # Adjust precision for display based on magnitude
        if abs(num_val) < 0.01 and num_val != 0 :
            formatted_str = f"{num_val:.5f}".rstrip('0').rstrip('.') # More precision for small decimals
        elif abs(num_val) < 1 and num_val != 0 :
            formatted_str = f"{num_val:.4f}".rstrip('0').rstrip('.')
        else:
            formatted_str = f"{num_val:.2f}".rstrip('0').rstrip('.') # Standard 2 decimal for others
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
    if 'all_possible_options' not in st.session_state:
        st.session_state.all_possible_options = []
    if 'options_in_slots' not in st.session_state:
        st.session_state.options_in_slots = [None, None, None]
    if 'available_options_pool' not in st.session_state:
        st.session_state.available_options_pool = []
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

    # Generate distractors based on start value and correct factor
    for val in [sv, cf]:
        if val != 0:
            # More aggressive generation for larger numbers
            multipliers = [10, 100, 1000, 0.1, 0.01, 0.001, 2, 0.5]
            if val > 10000: multipliers.extend([10000, 0.0001])
            
            for mult in multipliers:
                if mult != 1: # Avoid adding val itself again if mult is 1
                    numerical_distractors_pool.append(val * mult)

    # Common conversion factors, including larger ones for area/volume
    numerical_distractors_pool.extend([1, 10, 100, 1000, 10000, 1000000, 0.1, 0.01, 0.001, 0.0001, 0.000001])
    # Add some other plausible numbers
    numerical_distractors_pool.extend([2, 5, 20, 25, 50, 200, 250, 500]) 
    
    random.shuffle(numerical_distractors_pool)
    for dist_num in numerical_distractors_pool:
        if len(options_set) >= 12: break # Allow a slightly larger pool of options
        
        # Round distractors for cleaner display, considering very small/large numbers
        if dist_num == 0: continue # Avoid zero as a distractor unless it's meaningful
        
        if abs(dist_num) < 0.000001 and dist_num != 0: dist_num_rounded = round(dist_num,7)
        elif abs(dist_num) < 0.001 and dist_num != 0: dist_num_rounded = round(dist_num,5)
        elif abs(dist_num) < 1: dist_num_rounded = round(dist_num,3)
        elif abs(dist_num) > 100000: dist_num_rounded = round(dist_num,0) # Round large numbers to int
        else: dist_num_rounded = round(dist_num,2)

        if dist_num_rounded == int(dist_num_rounded): dist_num_rounded = int(dist_num_rounded)
        
        dist_num_str = str(dist_num_rounded)
        if dist_num_str not in options_set: # Ensure unique options
            options_set.add(dist_num_str)
            
    options_list = list(options_set)
    random.shuffle(options_list)
    
    st.session_state.all_possible_options = list(options_list)
    st.session_state.available_options_pool = list(options_list)
    # Slots are reset by generate_question calling this, or should be explicitly reset here
    st.session_state.options_in_slots = [None, None, None] 
    st.session_state.invalid_slot_attempt_idx = None


def generate_question():
    st.session_state.feedback_html_content = ""
    st.session_state.invalid_slot_attempt_idx = None 
    
    category_name = random.choice(list(CONVERSIONS.keys()))
    conversion = random.choice(CONVERSIONS[category_name])
    
    # Adjust base_val generation slightly for potentially larger factors in area/volume
    factor = conversion["factor"]
    op = conversion["operation"]

    if op == "÷": # e.g. cm^2 to m^2 (factor 10000)
        if factor > 100000: # Very large factor (e.g., cubed units)
             base_val = random.uniform(0.1, 50) * factor * random.choice([0.1, 1, 10])
        elif factor > 1000: # Large factor
            base_val = random.uniform(1, 500) * factor * random.choice([0.01, 0.1, 1, 10]) / random.choice([1,10,100])
        else: # Smaller factor
            base_val = random.uniform(1, 1000) * random.choice([0.1,1,10])
    else: # op == "×", e.g. m^2 to cm^2
        if factor > 100000:
            base_val = random.uniform(0.00001, 5) * random.choice([0.1,1,10])
        elif factor > 1000:
            base_val = random.uniform(0.001, 50) * random.choice([0.1,1,10])
        else:
            base_val = random.uniform(0.1, 500) * random.choice([0.01, 0.1,1])

    # General rounding and clamping for start_value
    start_value = round(base_val, 7) # Allow more precision initially for wider range of numbers
    if start_value == 0 and base_val != 0: 
        start_value = base_val if abs(base_val) > 1e-7 else (1e-7 if base_val > 0 else -1e-7)
    
    # Clamping to avoid extremely large or small numbers that are hard to work with
    min_val, max_val = 1e-6, 1e9 # Min/max for start_value
    start_value = max(min(start_value, max_val), min_val) if start_value > 0 else start_value
    start_value = min(max(start_value, -max_val), -min_val) if start_value < 0 else start_value


    # Fine-tune rounding for display based on magnitude
    if abs(start_value) < 0.0001 and start_value != 0: start_value = round(start_value,6) 
    elif abs(start_value) < 0.01 and start_value != 0: start_value = round(start_value,5)
    elif abs(start_value) < 1 and start_value != 0: start_value = round(start_value,4)
    elif abs(start_value) < 1000: start_value = round(start_value,2)
    else: start_value = round(start_value,0) # For very large numbers, round to integer

    if start_value == int(start_value): start_value = int(start_value)

    correct_answer_val = 0
    if conversion["operation"] == "÷":
        if conversion["factor"] == 0: correct_answer_val = float('inf')
        else: correct_answer_val = start_value / conversion["factor"]
    else: # "×"
        correct_answer_val = start_value * conversion["factor"]

    # Rounding for correct_answer_val (similar to start_value for consistency)
    if abs(correct_answer_val) < 0.0001 and correct_answer_val !=0 : correct_answer_val = round(correct_answer_val, 6)
    elif abs(correct_answer_val) < 0.01 and correct_answer_val !=0 : correct_answer_val = round(correct_answer_val, 5)
    elif abs(correct_answer_val) < 1 and correct_answer_val !=0 : correct_answer_val = round(correct_answer_val, 4)
    elif abs(correct_answer_val) < 1000 : correct_answer_val = round(correct_answer_val, 2)
    else: correct_answer_val = round(correct_answer_val,0) # Round large answers to integer

    if correct_answer_val == int(correct_answer_val): correct_answer_val = int(correct_answer_val)
    
    # question_template_text includes the units which might have HTML
    question_template_text = f"Convert: {format_number_display(str(start_value))} {conversion['from']} = _____ {conversion['to']}"

    st.session_state.current_question_data = {
        "question_template_text": question_template_text,
        "start_value": start_value, "from_unit": conversion['from'], "to_unit": conversion['to'],
        "correct_factor": conversion["factor"], "correct_operation_symbol": conversion["operation"],
        "correct_answer_value": correct_answer_val
    }
    generate_options_data()


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
        st.session_state.invalid_slot_attempt_idx = None 
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
        st.session_state.invalid_slot_attempt_idx = None 
    else:
        st.toast(f"Invalid. Expected {expected_type_msg} for the next slot.", icon="🚫")
        st.session_state.invalid_slot_attempt_idx = target_slot_idx 

def handle_slot_click(slot_idx_clicked):
    option_value_to_move_back = st.session_state.options_in_slots[slot_idx_clicked]
    if option_value_to_move_back is not None:
        st.session_state.options_in_slots[slot_idx_clicked] = None
        rebuild_available_options_pool() 
        st.session_state.feedback_html_content = "" 
        st.session_state.invalid_slot_attempt_idx = None 

def on_submit_button_clicked():
    current_feedback_html = ""
    cqd = st.session_state.current_question_data
    st.session_state.invalid_slot_attempt_idx = None 
    
    if None in st.session_state.options_in_slots:
        st.session_state.feedback_html_content = "<p style='color:orange; font-weight:bold;'>Please fill all three slots in the answer.</p>"
        return

    val_str, op_str, factor_str = st.session_state.options_in_slots

    try:
        student_selected_start_val = float(val_str)
        student_selected_factor = float(factor_str)

        if abs(student_selected_start_val - cqd["start_value"]) > 1e-9: # Using a small tolerance for float comparison
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
            if student_selected_factor == 0: # Avoid division by zero
                current_feedback_html += "<p style='color:red; font-weight:bold;'>Error: Division by zero is not allowed.</p>"
                st.session_state.feedback_html_content = current_feedback_html; return
            student_result = student_selected_start_val / student_selected_factor
        elif op_str == "×":
            student_result = student_selected_start_val * student_selected_factor
        else: 
            current_feedback_html += "<p style='color:red; font-weight:bold;'>Error: Invalid operation in slots.</p>"
            st.session_state.feedback_html_content = current_feedback_html; return
        
        # Round student_result for comparison and display, similar to correct_answer_value
        if abs(student_result) < 0.0001 and student_result !=0 : student_result_rounded = round(student_result, 6)
        elif abs(student_result) < 0.01 and student_result !=0 : student_result_rounded = round(student_result, 5)
        elif abs(student_result) < 1 and student_result !=0 : student_result_rounded = round(student_result, 4)
        elif abs(student_result) < 1000 : student_result_rounded = round(student_result, 2)
        else: student_result_rounded = round(student_result,0)
        if student_result_rounded == int(student_result_rounded): student_result_rounded = int(student_result_rounded)
        
        current_feedback_html += f"<p>Calculating... {format_number_display(val_str)} {op_str} {format_number_display(factor_str)} = {format_number_display(str(student_result_rounded))}</p>"
        st.session_state.feedback_html_content = current_feedback_html; time.sleep(1.2)

        correct_ans_val = cqd["correct_answer_value"]
        # Using a small tolerance for float comparison
        is_correct = abs(student_result_rounded - correct_ans_val) < 1e-9 
        if isinstance(correct_ans_val, int) and isinstance(student_result_rounded, float) and student_result_rounded == float(correct_ans_val):
            is_correct = True # Handle cases like 5.0 vs 5

        result_unit = cqd['to_unit'] # This will have HTML if it's an area/volume unit

        if is_correct:
            msg = f"Result: {format_number_display(str(student_result_rounded))} {result_unit}. Correct! Well done! 🎉"
            current_feedback_html += f"<p style='color:green; font-weight:bold;'>{msg}</p>"
        else:
            msg = f"Result: {format_number_display(str(student_result_rounded))} {result_unit}. Not quite right. 🤔"
            current_feedback_html += f"<p style='color:red; font-weight:bold;'>{msg}</p>"
            st.session_state.feedback_html_content = current_feedback_html; time.sleep(0.8)
            current_feedback_html += "<hr><p><strong>Let's see the correct steps:</strong></p>"
            correct_op_sym, correct_fact_num, start_v_num = cqd['correct_operation_symbol'], cqd['correct_factor'], cqd['start_value']
            from_u, to_u = cqd['from_unit'], cqd['to_unit'] # These will have HTML
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
    st.session_state.game_initialized = True 

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
        q_prefix = parts_around_placeholder[0] # Contains ... {value} {from_unit} =
        q_suffix = parts_around_placeholder[1] if len(parts_around_placeholder) > 1 else "" # Contains {to_unit}
        
        q_col_widths = [3, 1.5, 1.5, 1.5, 2] 
        q_cols = st.columns(q_col_widths)
        
        with q_cols[0]:
            # The q_prefix already contains the value and from_unit, so just display it.
            st.markdown(f"<div style='text-align: right; margin-top: 0.5rem; font-size: 1.2em;'>{q_prefix}</div>", unsafe_allow_html=True)

        for i in range(3): 
            with q_cols[i+1]:
                option_in_slot = st.session_state.options_in_slots[i]
                slot_style_default = "border: 1.5px dashed #AED6F1; background-color: #EBF5FB; text-align:center; padding: 0.4rem; margin:1px auto; height: 2.375rem; border-radius:0.25rem; width: 95%; box-sizing: border-box;"
                slot_style_invalid = "border: 2px solid red; background-color: #FADBD8; text-align:center; padding: 0.4rem; margin:1px auto; height: 2.375rem; border-radius:0.25rem; width: 95%; box-sizing: border-box;"
                
                current_slot_style = slot_style_default
                if st.session_state.invalid_slot_attempt_idx == i and option_in_slot is None:
                    current_slot_style = slot_style_invalid

                if option_in_slot is not None:
                    st.button(
                        format_number_display(option_in_slot), 
                        key=f"slot_btn_{i}", 
                        on_click=handle_slot_click, 
                        args=(i,),
                        use_container_width=True
                    )
                else:
                    st.markdown(f"<div style='{current_slot_style}'></div>", unsafe_allow_html=True)
        
        with q_cols[-1]: 
            # The q_suffix contains the to_unit
            st.markdown(f"<div style='text-align: left; margin-top: 0.5rem; font-size: 1.2em;'>{q_suffix}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<h3>Loading question... Please wait.</h3>", unsafe_allow_html=True)
        if st.button("Force Reload Question", key="force_reload_question_btn"):
            st.session_state.game_initialized = False 
            st.rerun()

    st.markdown("---")
    st.write("**Available Options:**")
    available_options_pool = st.session_state.get('available_options_pool', [])
    if not available_options_pool:
        st.caption("All options are placed in slots above, or no options generated.")
    else:
        num_avail_cols = st.slider("Number of columns for options:", min_value=3, max_value=8, value=5, key="num_avail_cols_slider")
        
        rows_of_avail_buttons = [available_options_pool[i:i + num_avail_cols] for i in range(0, len(available_options_pool), num_avail_cols)]
        for r_idx, row_options in enumerate(rows_of_avail_buttons):
            cols_avail = st.columns(num_avail_cols)
            for c_idx, option_val_str in enumerate(row_options):
                if c_idx < len(row_options): # Ensure we don't try to access out of bounds if last row is not full
                    button_label = format_number_display(option_val_str)
                    unique_key = f"avail_btn_{option_val_str}_{r_idx}_{c_idx}" # Key needs to be stable for given option if possible
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

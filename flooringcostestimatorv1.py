import streamlit as st
from fpdf import FPDF
import pandas as pd
from datetime import datetime
import io

st.title('Flooring Cost Estimator')

# Customer/Client Details
st.header('Customer/Client Details')
client_name = st.text_input('Enter the client\'s name:')
client_address = st.text_input('Enter the client\'s address:')
client_email = st.text_input('Enter the client\'s email:')
client_phone = st.text_input('Enter the client\'s phone number:')

# Project Dates
st.header('Project Dates')
proposal_date = st.date_input('Enter the date of the project proposal:')
proposal_time = st.time_input('Enter the time of the project proposal:')
completion_date = st.date_input('Enter the expected project completion date:')
completion_time = st.number_input('Enter the expected project completion time (in hours):', min_value=0, format="%d")

# Job Inputs
st.header('Input Dimensions')
length = st.number_input('Enter the length of the area (in feet):', min_value=0.0, format="%f")
width = st.number_input('Enter the width of the area (in feet):', min_value=0.0, format="%f")
area_name = st.text_input('Enter the name of the area for flooring to be installed:')

st.header('Input Materials')
flooring_type = st.selectbox('Select the type of flooring:', ['Hard Wood Flooring', 'Laminate', 'Vinyl'])
subfloor_type = st.text_input('Enter the type of subfloor:')
sound_barrier = st.text_input('Enter the type of sound barrier:')
mold_barrier = st.text_input('Enter the type of mold barrier:')
moisture_barrier = st.text_input('Enter the type of moisture barrier:')

st.header('Itemized Costs')

# Material Costs
if 'material_items' not in st.session_state:
    st.session_state['material_items'] = []

material_item = st.text_input('Enter a material cost item:')
material_cost = st.number_input('Enter the cost for this item (per foot):', min_value=0.0, format="%f")

if st.button('Add Material Cost Item'):
    st.session_state.material_items.append({'item': material_item, 'cost': material_cost})
    st.success('Material cost item added!')

st.subheader('Material Cost Items')
for i, item in enumerate(st.session_state.material_items):
    st.write(f"{i+1}. {item['item']}: ${item['cost']:.2f} per foot")

# Labor Costs
if 'labor_items' not in st.session_state:
    st.session_state['labor_items'] = []

labor_item = st.text_input('Enter total labor cost:')
labor_cost = st.number_input('Enter the hourly cost for this item:', min_value=0.0, format="%f")

if st.button('Add Labor Cost Item'):
    st.session_state.labor_items.append({'item': labor_item, 'cost': labor_cost})
    st.success('Labor cost item added!')

st.subheader('Labor Cost Items')
for i, item in enumerate(st.session_state.labor_items):
    st.write(f"{i+1}. {item['item']}: ${item['cost']:.2f} per hour")

# Laborers and Work Time
if 'laborers' not in st.session_state:
    st.session_state['laborers'] = []

laborer_name = st.text_input('Enter the name of the laborer:')
hours_worked = st.number_input('Enter the number of hours worked:', min_value=0, format="%d")
minutes_worked = st.number_input('Enter the number of minutes worked:', min_value=0, max_value=59, format="%d")

if st.button('Add Laborer'):
    total_hours = hours_worked + minutes_worked / 60
    st.session_state.laborers.append({'name': laborer_name, 'hours': total_hours})
    st.success('Laborer added!')

st.subheader('Laborers and Work Time')
for i, laborer in enumerate(st.session_state.laborers):
    st.write(f"{i+1}. {laborer['name']}: {int(laborer['hours'])} hours and {int((laborer['hours'] % 1) * 60)} minutes")

# Individual Expenses
if 'expenses' not in st.session_state:
    st.session_state['expenses'] = []

expense_item = st.text_input('Enter an expense description:')
expense_cost = st.number_input('Enter the dollar amount for this expense:', min_value=0.0, format="%f")

if st.button('Add Expense Item'):
    st.session_state.expenses.append({'description': expense_item, 'amount': expense_cost})
    st.success('Expense item added!')

st.subheader('Individual Expenses')
for i, expense in enumerate(st.session_state.expenses):
    st.write(f"{i+1}. {expense['description']}: ${expense['amount']:.2f}")

# Calculate total cost
area = length * width
total_material_cost = sum(item['cost'] for item in st.session_state.material_items) * area
total_labor_cost = sum(laborer['hours'] * sum(item['cost'] for item in st.session_state.labor_items) for laborer in st.session_state.laborers)
total_expenses = sum(expense['amount'] for expense in st.session_state.expenses)

st.write(f'Total Material Cost: ${total_material_cost:.2f}')
st.write(f'Total Labor Cost: ${total_labor_cost:.2f}')
st.write(f'Total Additional Expenses: ${total_expenses:.2f}')

# Save user inputs
if 'inputs' not in st.session_state:
    st.session_state['inputs'] = []

if st.button('Save Inputs'):
    inputs = {
        'client_name': client_name,
        'client_address': client_address,
        'client_email': client_email,
        'client_phone': client_phone,
        'proposal_date': proposal_date.strftime("%Y-%m-%d"),
        'proposal_time': proposal_time.strftime("%H:%M:%S"),
        'completion_date': completion_date.strftime("%Y-%m-%d"),
        'completion_time': f"{completion_time} hours",
        'length': length,
        'width': width,
        'area_name': area_name,
        'flooring_type': flooring_type,
        'subfloor_type': subfloor_type,
        'sound_barrier': sound_barrier,
        'mold_barrier': mold_barrier,
        'moisture_barrier': moisture_barrier,
        'material_items': st.session_state.material_items,
        'labor_items': st.session_state.labor_items,
        'laborers': st.session_state.laborers,
        'expenses': st.session_state.expenses,
        'total_material_cost': total_material_cost,
        'total_labor_cost': total_labor_cost,
        'total_expenses': total_expenses,
    }
    st.session_state.inputs.append(inputs)
    st.success('Inputs saved!')

# Export to PDF
def export_to_pdf(inputs):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for i, input_set in enumerate(inputs):
        pdf.cell(200, 10, txt=f"Input Set {i+1}", ln=True, align='L')
        for key, value in input_set.items():
            if isinstance(value, list):
                pdf.cell(200, 10, txt=f"{key}:", ln=True, align='L')
                for item in value:
                    if 'item' in item:
                        pdf.cell(200, 10, txt=f" - {item['item']}: ${item['cost']}", ln=True, align='L')
                    elif 'name' in item:
                        pdf.cell(200, 10, txt=f" - {item['name']}: {int(item['hours'])} hours and {int((item['hours'] % 1) * 60)} minutes", ln=True, align='L')
                    else:
                        pdf.cell(200, 10, txt=f" - {item['description']}: ${item['amount']}", ln=True, align='L')
            else:
                pdf.cell(200, 10, txt=f"{key}: {value}", ln=True, align='L')
        pdf.cell(200, 10, txt="--------------------------------------", ln=True, align='L')

    return pdf.output(dest='S').encode('latin1')

# Export to CSV
def export_to_csv(inputs):
    all_data = []
    for input_set in inputs:
        for key, value in input_set.items():
            if isinstance(value, list):
                for item in value:
                    if 'item' in item:
                        all_data.append({'set': inputs.index(input_set) + 1, 'type': key, 'description': item['item'], 'cost': item['cost']})
                    elif 'name' in item:
                        all_data.append({'set': inputs.index(input_set) + 1, 'type': key, 'description': item['name'], 'cost': item['hours']})
                    else:
                        all_data.append({'set': inputs.index(input_set) + 1, 'type': key, 'description': item['description'], 'cost': item['amount']})
            else:
                all_data.append({'set': inputs.index(input_set) + 1, 'type': key, 'description': value, 'cost': None})

    df = pd.DataFrame(all_data)
    return df.to_csv(index=False).encode('utf-8')

if st.button('Export to PDF'):
    if st.session_state.inputs:
        pdf_bytes = export_to_pdf(st.session_state.inputs)
        st.download_button(label="Download PDF", data=pdf_bytes, file_name="flooring_cost_estimator.pdf", mime="application/pdf")
        st.success('PDF exported successfully!')
    else:
        st.error('No inputs to export!')

if st.button('Export to CSV'):
    if st.session_state.inputs:
        csv_bytes = export_to_csv(st.session_state.inputs)
        st.download_button(label="Download CSV", data=csv_bytes, file_name="flooring_cost_estimator.csv", mime="text/csv")
        st.success('CSV exported successfully!')
    else:
        st.error('No inputs to export!')

st.header('Saved Inputs')
st.write(st.session_state.inputs)
